# -*- coding: utf-8 -*-
"""
MA+KDJ 策略 - 锰硅专项回测（修复版）
修复问题：
1. 30 分钟 K 线索引对齐（使用时间匹配）
2. 只测试锰硅品种
3. 优化参数
"""

from tqsdk import TqApi, TqAuth, TqBacktest
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import os
import sys

# 添加路径导入配置
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

# 回测配置
END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=180)
INITIAL_CAPITAL = 100000

# 品种配置（只测试锰硅）
SYMBOL = {"code": "KQ.m@CZCE.SM", "name": "锰硅", "tick": 2, "multiplier": 5}

# 策略参数（优化版 - 针对锰硅）
EXPMA_FAST = 13
EXPMA_SLOW = 26
KDJ_PERIOD = 9
# 放宽 KDJ 阈值，增加信号
KDJ_LONG_THRESHOLD = 30   # 多头 J 值<30（原 20）
KDJ_SHORT_THRESHOLD = 70  # 空头 J 值>70（原 80）
COMMISSION_RATIO = 0.00006
SLIPPAGE = 1
MAX_POSITION_RATIO = 0.5
MAX_DAILY_TRADES = 5  # 增加每日交易次数
STOP_LOSS_TICKS = 3   # 止损 tick 数（原 1tick）


def calculate_kdj(df, period=9):
    """计算 KDJ 指标 - 修复除零问题"""
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    
    rsv = pd.Series(index=df.index, dtype=float)
    mask = (high_max - low_min) != 0
    rsv[mask] = (df['close'][mask] - low_min[mask]) / (high_max[mask] - low_min[mask]) * 100
    rsv[~mask] = 50
    rsv = rsv.fillna(50)
    
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    
    return k, d, j


def calculate_ema(series, period):
    """计算 EMA"""
    return series.ewm(span=period, adjust=False).mean()


def find_bottom_fractal(klines, start_idx, lookback=10):
    """查找底分型最低点"""
    if start_idx < lookback:
        return klines.iloc[start_idx]['low']
    
    for i in range(start_idx - lookback, start_idx - 2):
        if i < 0:
            continue
        if (klines.iloc[i]['low'] > klines.iloc[i+1]['low'] and 
            klines.iloc[i+2]['low'] > klines.iloc[i+1]['low']):
            return klines.iloc[i+1]['low']
    
    return klines.iloc[start_idx-lookback:start_idx]['low'].min()


def find_top_fractal(klines, start_idx, lookback=10):
    """查找顶分型最高点"""
    if start_idx < lookback:
        return klines.iloc[start_idx]['high']
    
    for i in range(start_idx - lookback, start_idx - 2):
        if i < 0:
            continue
        if (klines.iloc[i]['high'] < klines.iloc[i+1]['high'] and 
            klines.iloc[i+2]['high'] < klines.iloc[i+1]['high']):
            return klines.iloc[i+1]['high']
    
    return klines.iloc[start_idx-lookback:start_idx]['high'].max()


def get_30min_index(klines_30, current_datetime):
    """
    获取当前 5 分钟 K 线对应的 30 分钟 K 线索引
    使用时间匹配而不是简单除法
    """
    # 找到最后一个 datetime <= current_datetime 的 30 分钟 K 线
    matches = klines_30[klines_30['datetime'] <= current_datetime]
    if len(matches) == 0:
        return 0
    return len(matches) - 1


def run_backtest():
    """运行锰硅回测"""
    symbol = SYMBOL["code"]
    name = SYMBOL["name"]
    tick = SYMBOL["tick"]
    multiplier = SYMBOL["multiplier"]
    
    print(f"\n{'='*60}")
    print(f"MA+KDJ 策略 - 锰硅专项回测")
    print(f"回测区间：{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    print(f"初始资金：{INITIAL_CAPITAL}元")
    print(f"{'='*60}")
    
    try:
        api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=TqBacktest(
                start_dt=START_DATE,
                end_dt=END_DATE
            )
        )
        
        # 获取 5 分钟 K 线数据
        klines = api.get_kline_serial(symbol, duration_seconds=300, data_length=10000)
        
        print(f"\n获取到 {len(klines)} 条 5 分钟 K 线数据")
        
        if len(klines) < 50:
            print(f"[ERROR] 数据不足")
            api.close()
            return None
        
        # 准备 30 分钟 K 线
        klines_30 = klines.copy()
        klines_30['datetime'] = pd.to_datetime(klines_30['datetime'])
        klines_30 = klines_30.set_index('datetime')
        
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        klines_30 = klines_30.resample('30min').agg(ohlc_dict).dropna().reset_index()
        
        print(f"重采样得到 {len(klines_30)} 条 30 分钟 K 线数据")
        
        if len(klines_30) < 30:
            print(f"[ERROR] 30 分钟数据不足")
            api.close()
            return None
        
        # 计算 30 分钟指标
        klines_30['expma13'] = calculate_ema(klines_30['close'], EXPMA_FAST)
        klines_30['expma26'] = calculate_ema(klines_30['close'], EXPMA_SLOW)
        k_30, d_30, j_30 = calculate_kdj(klines_30, KDJ_PERIOD)
        klines_30['kdj_j'] = j_30
        
        # 计算 5 分钟指标
        klines['datetime_dt'] = pd.to_datetime(klines['datetime'])
        klines['expma13'] = calculate_ema(klines['close'], EXPMA_FAST)
        klines['expma26'] = calculate_ema(klines['close'], EXPMA_SLOW)
        k_5, d_5, j_5 = calculate_kdj(klines, KDJ_PERIOD)
        klines['kdj_j'] = j_5
        
        # 交易记录
        trades = []
        position = 0
        entry_price = 0
        entry_time = ""
        entry_kline_idx = 0
        hands = 1
        stop_loss = 0
        
        daily_trades = 0
        last_trade_date = None
        
        # 调试计数器
        debug_print_count = 0
        
        # 遍历 5 分钟 K 线
        for i in range(50, len(klines)):
            current_time = str(klines.iloc[i]['datetime'])[:10]
            
            if current_time != last_trade_date:
                daily_trades = 0
                last_trade_date = current_time
            
            # 获取 30 分钟索引（使用时间匹配）
            idx_30 = get_30min_index(klines_30, klines.iloc[i]['datetime_dt'])
            
            # 获取 30 分钟指标
            expma13_30 = klines_30.iloc[idx_30]['expma13']
            expma26_30 = klines_30.iloc[idx_30]['expma26']
            j_30 = klines_30.iloc[idx_30]['kdj_j']
            
            # 获取 5 分钟指标
            expma13_5 = klines.iloc[i]['expma13']
            expma26_5 = klines.iloc[i]['expma26']
            j_5 = klines.iloc[i]['kdj_j']
            
            price = klines.iloc[i]['close']
            
            # 调试输出（每天第一条）
            if debug_print_count < 5 and i % 100 == 0:
                print(f"[调试] K 线{i} | 时间:{klines.iloc[i]['datetime']} | 30 分:EXPMA13={expma13_30:.1f}, EXPMA26={expma26_30:.1f}, J={j_30:.1f} | 5 分:EXPMA13={expma13_5:.1f}, EXPMA26={expma26_5:.1f}, J={j_5:.1f}")
                debug_print_count += 1
            
            # 如果持有仓位，检查出场
            if position != 0:
                # 止损检查
                if position == 1 and price <= stop_loss:
                    pnl = (price - entry_price) * hands * multiplier
                    commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
                    slip = SLIPPAGE * hands * multiplier * 2
                    net_pnl = pnl - commission - slip
                    trades.append({
                        "entry_time": entry_time,
                        "entry_price": entry_price,
                        "exit_time": str(klines.iloc[i]['datetime']),
                        "exit_price": price,
                        "direction": "LONG",
                        "pnl": round(net_pnl, 2),
                        "exit_reason": "止损"
                    })
                    print(f"[止损] 多单 @ {price}, 盈亏={net_pnl:.2f}")
                    position = 0
                    
                elif position == -1 and price >= stop_loss:
                    pnl = (entry_price - price) * hands * multiplier
                    commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
                    slip = SLIPPAGE * hands * multiplier * 2
                    net_pnl = pnl - commission - slip
                    trades.append({
                        "entry_time": entry_time,
                        "entry_price": entry_price,
                        "exit_time": str(klines.iloc[i]['datetime']),
                        "exit_price": price,
                        "direction": "SHORT",
                        "pnl": round(net_pnl, 2),
                        "exit_reason": "止损"
                    })
                    print(f"[止损] 空单 @ {price}, 盈亏={net_pnl:.2f}")
                    position = 0
                
                # 移动止损（多单：底分型上移）
                if position == 1 and i >= entry_kline_idx + 5:
                    bottom_fractal = find_bottom_fractal(klines, i, lookback=10)
                    prev_bottom = find_bottom_fractal(klines, i-10, lookback=10)
                    if bottom_fractal > prev_bottom and bottom_fractal > stop_loss:
                        stop_loss = bottom_fractal
                        print(f"[移动止损] 多单上移至 {stop_loss:.2f}")
                
                # 移动止损（空单：顶分型下移）
                if position == -1 and i >= entry_kline_idx + 5:
                    top_fractal = find_top_fractal(klines, i, lookback=10)
                    prev_top = find_top_fractal(klines, i-10, lookback=10)
                    if top_fractal < prev_top and top_fractal < stop_loss:
                        stop_loss = top_fractal
                        print(f"[移动止损] 空单下移至 {stop_loss:.2f}")
                
                # 止盈检查（EXPMA 反向交叉）
                if position == 1 and i >= 1:
                    prev_diff = klines.iloc[i-1]['expma13'] - klines.iloc[i-1]['expma26']
                    curr_diff = expma13_5 - expma26_5
                    if prev_diff > 0 and curr_diff <= 0:
                        pnl = (price - entry_price) * hands * multiplier
                        commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
                        slip = SLIPPAGE * hands * multiplier * 2
                        net_pnl = pnl - commission - slip
                        trades.append({
                            "entry_time": entry_time,
                            "entry_price": entry_price,
                            "exit_time": str(klines.iloc[i]['datetime']),
                            "exit_price": price,
                            "direction": "LONG",
                            "pnl": round(net_pnl, 2),
                            "exit_reason": "止盈 (死叉)"
                        })
                        print(f"[止盈] 多单 @ {price}, 盈亏={net_pnl:.2f}")
                        position = 0
                        
                elif position == -1 and i >= 1:
                    prev_diff = klines.iloc[i-1]['expma13'] - klines.iloc[i-1]['expma26']
                    curr_diff = expma13_5 - expma26_5
                    if prev_diff < 0 and curr_diff >= 0:
                        pnl = (entry_price - price) * hands * multiplier
                        commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
                        slip = SLIPPAGE * hands * multiplier * 2
                        net_pnl = pnl - commission - slip
                        trades.append({
                            "entry_time": entry_time,
                            "entry_price": entry_price,
                            "exit_time": str(klines.iloc[i]['datetime']),
                            "exit_price": price,
                            "direction": "SHORT",
                            "pnl": round(net_pnl, 2),
                            "exit_reason": "止盈 (金叉)"
                        })
                        print(f"[止盈] 空单 @ {price}, 盈亏={net_pnl:.2f}")
                        position = 0
            
            # 无仓位时检查开仓（去掉方向限制，只依赖 KDJ 超买超卖）
            if position == 0 and daily_trades < MAX_DAILY_TRADES:
                # 多头开仓（J<30 超卖区）
                if j_30 < KDJ_LONG_THRESHOLD and j_5 < KDJ_LONG_THRESHOLD:
                    # 方式 1:K 线低点抬高确认
                    if i >= 1 and klines.iloc[i]['low'] > klines.iloc[i-1]['low']:
                        entry_price = price
                        entry_time = str(klines.iloc[i]['datetime'])
                        entry_kline_idx = i
                        hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier)))
                        stop_loss = klines.iloc[i-1]['low'] - tick * STOP_LOSS_TICKS
                        position = 1
                        daily_trades += 1
                        print(f"[开仓 1 多] 多单 @ {price:.2f}, 手数={hands}, 止损={stop_loss}")
                
                # 空头开仓（J>70 超买区）
                elif j_30 > KDJ_SHORT_THRESHOLD and j_5 > KDJ_SHORT_THRESHOLD:
                    # 方式 1:K 线高点降低确认
                    if i >= 1 and klines.iloc[i]['high'] < klines.iloc[i-1]['high']:
                        entry_price = price
                        entry_time = str(klines.iloc[i]['datetime'])
                        entry_kline_idx = i
                        hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier)))
                        stop_loss = klines.iloc[i-1]['high'] + tick * STOP_LOSS_TICKS
                        position = -1
                        daily_trades += 1
                        print(f"[开仓 1 空] 空单 @ {price:.2f}, 手数={hands}, 止损={stop_loss}")
        
        api.close()
        
        # 生成报告
        if not trades:
            print(f"\n[WARN] 无交易记录")
            return {
                "symbol": symbol,
                "name": name,
                "period": f"{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}",
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "trades": []
            }
        
        total_pnl = sum(t['pnl'] for t in trades)
        winning = [t for t in trades if t['pnl'] > 0]
        losing = [t for t in trades if t['pnl'] <= 0]
        win_rate = len(winning) / len(trades) * 100 if trades else 0
        
        # 资金曲线
        capital = INITIAL_CAPITAL
        capital_curve = [{"date": START_DATE.strftime('%Y-%m-%d'), "capital": capital}]
        for t in trades:
            capital += t['pnl']
            capital_curve.append({"date": t['exit_time'][:10], "capital": round(capital, 2)})
        
        report = {
            "symbol": symbol,
            "name": name,
            "period": f"{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}",
            "initial_capital": INITIAL_CAPITAL,
            "final_capital": round(capital, 2),
            "total_pnl": round(total_pnl, 2),
            "total_trades": len(trades),
            "win_count": len(winning),
            "loss_count": len(losing),
            "win_rate": round(win_rate, 2),
            "avg_win": round(sum(t['pnl'] for t in winning) / len(winning), 2) if winning else 0,
            "avg_loss": round(sum(t['pnl'] for t in losing) / len(losing), 2) if losing else 0,
            "max_profit": max(t['pnl'] for t in trades) if trades else 0,
            "max_loss": min(t['pnl'] for t in trades) if trades else 0,
            "trades": trades,
            "capital_curve": capital_curve
        }
        
        print(f"\n{'='*60}")
        print(f"锰硅回测结果:")
        print(f"  总交易：{len(trades)}笔")
        print(f"  总盈亏：{total_pnl:.2f}元")
        print(f"  胜率：{win_rate:.2f}%")
        print(f"  平均盈利：{report['avg_win']:.2f}元")
        print(f"  平均亏损：{report['avg_loss']:.2f}元")
        print(f"  最大盈利：{report['max_profit']:.2f}元")
        print(f"  最大亏损：{report['max_loss']:.2f}元")
        print(f"  最终资金：{capital:.2f}元")
        print(f"{'='*60}")
        
        return report
        
    except Exception as e:
        import traceback
        print(f"[ERROR] 回测失败：{str(e)}")
        traceback.print_exc()
        return None


if __name__ == "__main__":
    report = run_backtest()
    
    if report:
        # 保存结果
        os.makedirs("backtest_results", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"backtest_results/ma_kdj_sm_fixed_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n[OK] 结果已保存：{output_file}")
