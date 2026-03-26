# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 180 天回测 (完整修复版)
根据用户提供的完整策略规则编写
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

# 品种配置（使用主连合约，自动处理移仓）
# margin_ratio: 保证金比例（期货通常 10%-15%，这里用 10% 计算）
SYMBOLS = [
    {"code": "KQ.m@CZCE.SM", "name": "锰硅", "tick": 2, "multiplier": 5, "margin_ratio": 0.10},
    {"code": "KQ.m@CZCE.FG", "name": "玻璃", "tick": 1, "multiplier": 20, "margin_ratio": 0.10},
    {"code": "KQ.m@DCE.c", "name": "玉米", "tick": 1, "multiplier": 10, "margin_ratio": 0.10},
]

# 策略参数
EXPMA_FAST = 13
EXPMA_SLOW = 26
KDJ_PERIOD = 9
ADX_PERIOD = 14
ADX_THRESHOLD = 25  # ADX 低于此值视为震荡市，不开仓
COMMISSION_RATIO = 0.00006
SLIPPAGE = 1
MAX_POSITION_RATIO = 0.5  # 仓位 50%
MAX_DAILY_TRADES = 3


def calculate_kdj(df, period=9):
    """计算 KDJ 指标 - 修复除零问题"""
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    
    # 防止除零：当 high_max == low_min 时，RSV 设为 50
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


def calculate_adx(df, period=14):
    """
    计算 ADX 指标（趋势强度）
    ADX > 25: 趋势市
    ADX < 25: 震荡市
    """
    high = df['high']
    low = df['low']
    close = df['close']
    
    # 计算 +DM 和 -DM
    diff_high = high.diff()
    diff_low = low.diff()
    
    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)
    
    plus_dm[(diff_high > diff_low) & (diff_high > 0)] = diff_high[(diff_high > diff_low) & (diff_high > 0)]
    minus_dm[(diff_low > diff_high) & (diff_low > 0)] = diff_low[(diff_low > diff_high) & (diff_low > 0)]
    
    # 计算 TR (True Range)
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # 平滑处理（使用 EMA）
    plus_di = pd.Series(0.0, index=df.index)
    minus_di = pd.Series(0.0, index=df.index)
    
    plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
    minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()
    tr_smooth = tr.ewm(span=period, adjust=False).mean()
    
    # 计算 +DI 和 -DI
    mask = tr_smooth > 0
    plus_di[mask] = 100 * plus_dm_smooth[mask] / tr_smooth[mask]
    minus_di[mask] = 100 * minus_dm_smooth[mask] / tr_smooth[mask]
    
    # 计算 DX
    di_sum = plus_di + minus_di
    di_diff = abs(plus_di - minus_di)
    dx = pd.Series(0.0, index=df.index)
    mask = di_sum > 0
    dx[mask] = 100 * di_diff[mask] / di_sum[mask]
    
    # 计算 ADX（DX 的平滑）
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return adx, plus_di, minus_di


def find_bottom_fractal(klines, start_idx, lookback=10):
    """
    查找底分型最低点
    底分型：中间 K 线低点最低，左右各有一根 K 线低点更高
    """
    if start_idx < lookback:
        return klines.iloc[start_idx]['low']
    
    for i in range(start_idx - lookback, start_idx - 2):
        if i < 0:
            continue
        # 检查是否形成底分型（3 根 K 线）
        if (klines.iloc[i]['low'] > klines.iloc[i+1]['low'] and 
            klines.iloc[i+2]['low'] > klines.iloc[i+1]['low']):
            return klines.iloc[i+1]['low']
    
    # 没找到分型，返回最低点
    return klines.iloc[start_idx-lookback:start_idx]['low'].min()


def find_top_fractal(klines, start_idx, lookback=10):
    """
    查找顶分型最高点
    顶分型：中间 K 线高点最高，左右各有一根 K 线高点更低
    """
    if start_idx < lookback:
        return klines.iloc[start_idx]['high']
    
    for i in range(start_idx - lookback, start_idx - 2):
        if i < 0:
            continue
        # 检查是否形成顶分型（3 根 K 线）
        if (klines.iloc[i]['high'] < klines.iloc[i+1]['high'] and 
            klines.iloc[i+2]['high'] < klines.iloc[i+1]['high']):
            return klines.iloc[i+1]['high']
    
    # 没找到分型，返回最高点
    return klines.iloc[start_idx-lookback:start_idx]['high'].max()


def run_backtest(symbol_info):
    """运行单个品种回测"""
    symbol = symbol_info["code"]
    name = symbol_info["name"]
    tick = symbol_info["tick"]
    multiplier = symbol_info["multiplier"]
    
    print(f"\n{'='*60}")
    print(f"开始回测：{name} ({symbol})")
    print(f"回测区间：{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    print(f"{'='*60}")
    
    try:
        # 使用 TqBacktest 进行回测
        api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=TqBacktest(
                start_dt=START_DATE,
                end_dt=END_DATE
            )
        )
        
        # 获取合约信息（包含保证金比例）
        quote = api.get_quote(symbol)
        # 获取交易所保证金比例（margin_long 和 margin_short 通常相同）
        margin_ratio = quote.margin_long if hasattr(quote, 'margin_long') and quote.margin_long > 0 else 0.10
        print(f"[INFO] {name} 保证金比例：{margin_ratio*100:.1f}%")
        
        # 获取 5 分钟 K 线数据 - 增加数据量到 10000 根（约 180 天）
        klines = api.get_kline_serial(symbol, duration_seconds=300, data_length=10000)
        
        if len(klines) < 50:
            print(f"[WARN] {name} 数据不足 ({len(klines)}条)，跳过")
            api.close()
            return {
                "symbol": symbol,
                "name": name,
                "period": f"{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}",
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "error": "数据不足"
            }
        
        # 计算 30 分钟 K 线（通过重采样）
        klines_30 = klines.copy()
        klines_30['datetime'] = pd.to_datetime(klines_30['datetime'])
        klines_30 = klines_30.set_index('datetime')
        
        # 重采样到 30 分钟
        ohlc_dict = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }
        klines_30 = klines_30.resample('30min').agg(ohlc_dict).dropna().reset_index()
        
        if len(klines_30) < 30:
            print(f"[WARN] {name} 30 分钟数据不足，跳过")
            api.close()
            return {
                "symbol": symbol,
                "name": name,
                "period": f"{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}",
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "error": "30 分钟数据不足"
            }
        
        # 计算 30 分钟指标
        klines_30['expma13'] = calculate_ema(klines_30['close'], EXPMA_FAST)
        klines_30['expma26'] = calculate_ema(klines_30['close'], EXPMA_SLOW)
        k_30, d_30, j_30 = calculate_kdj(klines_30, KDJ_PERIOD)
        klines_30['kdj_j'] = j_30
        
        # 计算 5 分钟指标
        klines['expma13'] = calculate_ema(klines['close'], EXPMA_FAST)
        klines['expma26'] = calculate_ema(klines['close'], EXPMA_SLOW)
        k_5, d_5, j_5 = calculate_kdj(klines, KDJ_PERIOD)
        klines['kdj_j'] = j_5
        
        # 计算 5 分钟 ADX（趋势强度过滤）
        adx_5, plus_di_5, minus_di_5 = calculate_adx(klines, ADX_PERIOD)
        klines['adx'] = adx_5
        
        # 交易记录
        trades = []
        position = 0  # 1=多，-1=空，0=无
        entry_price = 0
        entry_time = ""
        entry_kline_idx = 0
        hands = 1
        stop_loss = 0
        
        daily_trades = 0
        last_trade_date = None
        
        # 遍历 5 分钟 K 线
        for i in range(50, len(klines)):
            current_time = str(klines.iloc[i]['datetime'])[:10]
            
            # 重置每日交易次数
            if current_time != last_trade_date:
                daily_trades = 0
                last_trade_date = current_time
            
            # 找到对应的 30 分钟索引 - 修复：使用整数除法对齐
            idx_30 = i // 6  # 5 分钟 K 线索引除以 6 得到对应的 30 分钟索引
            if idx_30 >= len(klines_30):
                idx_30 = len(klines_30) - 1
            
            # 获取 30 分钟指标
            expma13_30 = klines_30.iloc[idx_30]['expma13']
            expma26_30 = klines_30.iloc[idx_30]['expma26']
            j_30 = klines_30.iloc[idx_30]['kdj_j']
            
            # 获取 5 分钟指标
            expma13_5 = klines.iloc[i]['expma13']
            expma26_5 = klines.iloc[i]['expma26']
            j_5 = klines.iloc[i]['kdj_j']
            
            price = klines.iloc[i]['close']
            
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
                    print(f"[止损] {name} 多单 @ {price}, 盈亏={net_pnl:.2f}")
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
                    print(f"[止损] {name} 空单 @ {price}, 盈亏={net_pnl:.2f}")
                    position = 0
                
                # 移动止损检查（多单：底分型上移）
                if position == 1 and i >= entry_kline_idx + 5:
                    bottom_fractal = find_bottom_fractal(klines, i, lookback=10)
                    prev_bottom = find_bottom_fractal(klines, i-10, lookback=10)
                    if bottom_fractal > prev_bottom and bottom_fractal > stop_loss:
                        stop_loss = bottom_fractal
                        print(f"[移动止损] {name} 多单上移至 {stop_loss:.2f}")
                
                # 移动止损检查（空单：顶分型下移）
                if position == -1 and i >= entry_kline_idx + 5:
                    top_fractal = find_top_fractal(klines, i, lookback=10)
                    prev_top = find_top_fractal(klines, i-10, lookback=10)
                    if top_fractal < prev_top and top_fractal < stop_loss:
                        stop_loss = top_fractal
                        print(f"[移动止损] {name} 空单下移至 {stop_loss:.2f}")
                
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
                        print(f"[止盈] {name} 多单 @ {price}, 盈亏={net_pnl:.2f}")
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
                        print(f"[止盈] {name} 空单 @ {price}, 盈亏={net_pnl:.2f}")
                        position = 0
            
            # 如果无仓位，检查入场（每天最多 3 笔）
            if position == 0 and daily_trades < 3:
                # 获取当前 ADX 值
                adx_current = klines.iloc[i]['adx'] if not pd.isna(klines.iloc[i]['adx']) else 0
                
                # ADX 过滤：低于阈值视为震荡市，不开仓
                if adx_current < ADX_THRESHOLD:
                    continue
                
                # 定方向：30 分钟 EXPMA 决定只做多或只做空
                only_long = expma13_30 > expma26_30
                only_short = expma13_30 < expma26_30
                
                # 做多检查（30 分钟 J<20 且 EXPMA13>EXPMA26）
                if only_long and j_30 < 20:
                    # 5 分钟 J<20 且 EXPMA13>EXPMA26 且底分型确认
                    if expma13_5 > expma26_5 and j_5 < 20:
                        # 底分型判断：当前 K 线低点 < 前一根低点，且后一根低点 > 当前低点（确认形成）
                        # 即：i-1 是最低点，i 和 i-2 的低点都比 i-1 高
                        if i >= 2 and klines.iloc[i-1]['low'] < klines.iloc[i-2]['low'] and klines.iloc[i]['low'] > klines.iloc[i-1]['low']:
                            entry_price = price  # 在确认 K 线（第 i 根）收盘价入场
                            entry_time = str(klines.iloc[i]['datetime'])
                            entry_kline_idx = i
                            # 期货保证金计算：手数 = 资金 × 仓位比例 ÷ (价格 × 乘数 × 保证金比例)
                            hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * margin_ratio)))
                            stop_loss = klines.iloc[i-1]['low'] - tick  # 底分型最低点下方 1 个 tick
                            position = 1
                            daily_trades += 1
                            print(f"[开多] {name} @ {price:.2f}, 手数={hands}, 止损={stop_loss} (底分型确认)")
                
                # 做空检查（30 分钟 J>80 且 EXPMA13<EXPMA26）
                elif only_short and j_30 > 80:
                    # 5 分钟 J>80 且 EXPMA13<EXPMA26 且顶分型确认
                    if expma13_5 < expma26_5 and j_5 > 80:
                        # 顶分型判断：当前 K 线高点 > 前一根高点，且后一根高点 < 当前高点（确认形成）
                        # 即：i-1 是最高点，i 和 i-2 的高点都比 i-1 低
                        if i >= 2 and klines.iloc[i-1]['high'] > klines.iloc[i-2]['high'] and klines.iloc[i]['high'] < klines.iloc[i-1]['high']:
                            entry_price = price  # 在确认 K 线（第 i 根）收盘价入场
                            entry_time = str(klines.iloc[i]['datetime'])
                            entry_kline_idx = i
                            # 期货保证金计算：手数 = 资金 × 仓位比例 ÷ (价格 × 乘数 × 保证金比例)
                            hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * margin_ratio)))
                            stop_loss = klines.iloc[i-1]['high'] + tick  # 顶分型最高点上方 1 个 tick
                            position = -1
                            daily_trades += 1
                            print(f"[开空] {name} @ {price:.2f}, 手数={hands}, 止损={stop_loss} (顶分型确认)")
        
        api.close()
        
        # 生成报告
        if not trades:
            print(f"[WARN] {name} 无交易记录")
            return {
                "symbol": symbol,
                "name": name,
                "period": f"{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}",
                "initial_capital": INITIAL_CAPITAL,
                "final_capital": INITIAL_CAPITAL,
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "trades": []
            }
        
        total_pnl = sum(t['pnl'] for t in trades)
        winning = [t for t in trades if t['pnl'] > 0]
        losing = [t for t in trades if t['pnl'] <= 0]
        win_rate = len(winning) / len(trades) * 100 if trades else 0
        
        # 计算资金曲线
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
        
        print(f"\n{name} 回测完成:")
        print(f"  总交易：{len(trades)}笔")
        print(f"  总盈亏：{total_pnl:.2f}元")
        print(f"  胜率：{win_rate:.2f}%")
        print(f"  最终资金：{capital:.2f}元")
        
        return report
        
    except Exception as e:
        import traceback
        print(f"[ERROR] {name} 回测失败：{str(e)}")
        traceback.print_exc()
        return {
            "symbol": symbol,
            "name": name,
            "error": str(e)
        }


if __name__ == "__main__":
    print("="*60)
    print("均线+KDJ 策略 - 180 天回测 (完整修复版)")
    print(f"回测区间：{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
    print(f"初始资金：{INITIAL_CAPITAL}元")
    print(f"仓位比例：{MAX_POSITION_RATIO*100}%")
    print("="*60)
    
    results = {}
    for symbol_info in SYMBOLS:
        report = run_backtest(symbol_info)
        if report:
            results[symbol_info["code"]] = report
    
    # 保存结果
    os.makedirs("backtest_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backtest_results/ma_kdj_180d_complete_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"[OK] 回测结果已保存：{output_file}")
    print("="*60)
    
    # 打印汇总
    print("\n回测汇总:")
    print("-"*70)
    print(f"{'品种':<10} {'交易笔数':<10} {'总盈亏 (元)':<15} {'胜率':<10} {'最终资金':<15}")
    print("-"*70)
    for code, report in results.items():
        if "error" not in report:
            print(f"{report['name']:<10} {report['total_trades']:<10} {report['total_pnl']:<15.2f} {report['win_rate']:<10.2f}% {report['final_capital']:<15.2f}")
        else:
            print(f"{report['name']:<10} {'失败':<10} {report.get('error', '未知错误'):<40}")
    print("-"*70)
