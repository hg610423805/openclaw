# -*- coding: utf-8 -*-
"""
分型趋势策略（固定 CSV 数据版）
交易周期：60 分钟 K 线
开仓条件：底分型抬高/顶分型降低
止损方式：移动止损（跟随新分型）
数据源：kline_data_sm_60m.csv（确保结果可复现）
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

# 添加路径导入配置
sys.path.insert(0, '..')

# 回测配置（从 CSV 读取固定数据，确保结果可复现）
# 数据文件：kline_data_sm_60m.csv（5000 根 60 分钟 K 线）
INITIAL_CAPITAL = 100000  # 10 万元
KLINE_CSV_FILE = 'kline_data_sm_60m.csv'

# 品种配置（只做锰硅）
SYMBOLS = [
    {"code": "KQ.m@CZCE.SM", "name": "锰硅", "tick": 2, "multiplier": 5},
]

# 策略参数
ADX_PERIOD = 14
ADX_THRESHOLD = 20  # ADX 阈值（已去掉）
MAX_POSITION_RATIO = 0.5  # 最大仓位 50%
FRACTAL_MIN_INTERVAL = 1  # 分型最小间隔（K 线数量）
FRACTAL_STRENGTH_TICKS = 0  # 分型力度：0=不过滤，所有分型都检测


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
    plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
    minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()
    tr_smooth = tr.ewm(span=period, adjust=False).mean()
    
    # 计算 +DI 和 -DI
    plus_di = pd.Series(0.0, index=df.index)
    minus_di = pd.Series(0.0, index=df.index)
    
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


def detect_fractals(klines, strength_ticks=2):
    """
    检测底分型和顶分型（带力度判断）
    返回：底分型列表、顶分型列表
    每个分型：{
        'index': K 线索引，
        'low/high': 极值，
        'confirm_idx': 确认时索引，
        'strength': 分型力度（中间 K 线比左右低/高的幅度）
    }
    """
    bottoms = []  # 底分型
    tops = []     # 顶分型
    
    for i in range(1, len(klines) - 1):
        # 检测底分型：中间 K 线低点最低
        if (klines.iloc[i]['low'] < klines.iloc[i-1]['low'] and 
            klines.iloc[i]['low'] < klines.iloc[i+1]['low']):
            # 计算力度：比左右 K 线低点低多少
            strength = min(klines.iloc[i-1]['low'], klines.iloc[i+1]['low']) - klines.iloc[i]['low']
            if strength >= strength_ticks:  # 力度满足才记录
                bottoms.append({
                    'index': i,
                    'low': klines.iloc[i]['low'],
                    'confirm_idx': i + 1,  # 第 i+1 根 K 线收盘时确认
                    'strength': strength
                })
        
        # 检测顶分型：中间 K 线高点最高
        if (klines.iloc[i]['high'] > klines.iloc[i-1]['high'] and 
            klines.iloc[i]['high'] > klines.iloc[i+1]['high']):
            # 计算力度：比左右 K 线高点高多少
            strength = klines.iloc[i]['high'] - max(klines.iloc[i-1]['high'], klines.iloc[i+1]['high'])
            if strength >= strength_ticks:  # 力度满足才记录
                tops.append({
                    'index': i,
                    'high': klines.iloc[i]['high'],
                    'confirm_idx': i + 1,  # 第 i+1 根 K 线收盘时确认
                    'strength': strength
                })
    
    return bottoms, tops


def run_backtest(symbol_info):
    """运行单个品种回测"""
    symbol = symbol_info["code"]
    name = symbol_info["name"]
    tick = symbol_info["tick"]
    multiplier = symbol_info["multiplier"]
    
    print(f"\n{'='*80}")
    print(f"开始回测：{name} ({symbol})")
    print(f"{'='*80}")
    
    try:
        # 从 CSV 读取固定 K 线数据（确保结果可复现）
        import os
        csv_path = os.path.join(os.path.dirname(__file__), KLINE_CSV_FILE)
        
        if not os.path.exists(csv_path):
            print(f"[ERROR] CSV 文件不存在：{csv_path}")
            print(f"请先运行：python save_kline_data.py")
            return None
        
        klines = pd.read_csv(csv_path)
        
        print(f"[INFO] 从 CSV 读取到 {len(klines)} 根 60 分钟 K 线")
        
        # 检查数据有效性
        if len(klines) == 0 or pd.isna(klines.iloc[0]['open']):
            print(f"[ERROR] K 线数据无效，跳过")
            return None
        
        # 打印实际数据区间
        first_time = str(klines.iloc[0]['datetime'])
        last_time = str(klines.iloc[-1]['datetime'])
        print(f"[INFO] K 线区间：{first_time[:10]} ~ {last_time[:10]}")
        
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
        
        # 计算 ADX
        adx, plus_di, minus_di = calculate_adx(klines, ADX_PERIOD)
        klines['adx'] = adx
        
        # 预先检测所有分型（带力度过滤）
        bottoms, tops = detect_fractals(klines, strength_ticks=FRACTAL_STRENGTH_TICKS)
        print(f"[INFO] 检测到 {len(bottoms)} 个底分型，{len(tops)} 个顶分型，合计 {len(bottoms)+len(tops)} 个分型")
        
        # 交易记录
        trades = []
        position = 0  # 1=多，-1=空，0=无
        entry_price = 0
        entry_time = ""
        stop_loss = 0
        hands = 1
        
        # 分型追踪
        last_bottom_idx = -1  # 上一个底分型索引
        last_top_idx = -1     # 上一个顶分型索引
        prev_bottom_low = None  # 上一个底分型最低点
        prev_top_high = None    # 上一个顶分型最高点
        
        # 遍历 K 线（从 ADX 有值的地方开始）
        start_idx = ADX_PERIOD + 10
        for i in range(start_idx, len(klines)):
            price = klines.iloc[i]['close']
            current_time = str(klines.iloc[i]['datetime'])
            adx_current = klines.iloc[i]['adx'] if not pd.isna(klines.iloc[i]['adx']) else 0
            
            # 检查当前 K 线是否确认了新分型
            current_bottom = None
            current_top = None
            
            # 检查底分型确认
            for b in bottoms:
                if b['confirm_idx'] == i:
                    # 检查间隔限制（至少 2 根 K 线）
                    if last_bottom_idx >= 0 and (b['index'] - last_bottom_idx) < FRACTAL_MIN_INTERVAL:
                        continue  # 间隔不足，忽略
                    current_bottom = b
                    break
            
            # 检查顶分型确认
            for t in tops:
                if t['confirm_idx'] == i:
                    # 检查间隔限制（至少 2 根 K 线）
                    if last_top_idx >= 0 and (t['index'] - last_top_idx) < FRACTAL_MIN_INTERVAL:
                        continue  # 间隔不足，忽略
                    current_top = t
                    break
            
            # 处理底分型
            if current_bottom:
                # 有多单时，上移止损
                if position == 1:
                    old_stop = stop_loss
                    stop_loss = current_bottom['low']
                    if stop_loss > old_stop:
                        print(f"[移动止损] {name} 多单止损上移：{old_stop:.2f} → {stop_loss:.2f}")
                
                # 检查是否开仓（有上一个分型 + 抬高 + 无持仓）
                if prev_bottom_low is not None and position == 0:
                    if current_bottom['low'] > prev_bottom_low:
                        # 开多
                        entry_price = price
                        entry_time = current_time
                        hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * 0.10)))
                        # 止损 = 当前开仓底分型的最低点（不是上一个分型！）
                        stop_loss = current_bottom['low']
                        position = 1
                        print(f"[开多] {name} @ {price:.2f}, 手数={hands}, 止损={stop_loss:.2f} (底分型抬高，力度={current_bottom['strength']:.1f})")
                
                # 更新记录
                prev_bottom_low = current_bottom['low']
                last_bottom_idx = current_bottom['index']
            
            # 处理顶分型
            if current_top:
                # 有空单时，下移止损
                if position == -1:
                    old_stop = stop_loss
                    stop_loss = current_top['high']
                    if stop_loss < old_stop:
                        print(f"[移动止损] {name} 空单止损下移：{old_stop:.2f} → {stop_loss:.2f}")
                
                # 检查是否开仓（有上一个分型 + 降低 + 无持仓）
                if prev_top_high is not None and position == 0:
                    if current_top['high'] < prev_top_high:
                        # 开空
                        entry_price = price
                        entry_time = current_time
                        hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * 0.10)))
                        # 止损 = 当前开仓顶分型的最高点（不是上一个分型！）
                        stop_loss = current_top['high']
                        position = -1
                        print(f"[开空] {name} @ {price:.2f}, 手数={hands}, 止损={stop_loss:.2f} (顶分型降低，力度={current_top['strength']:.1f})")
                
                # 更新记录
                prev_top_high = current_top['high']
                last_top_idx = current_top['index']
            
            # 检查止损平仓
            if position == 1 and price <= stop_loss:
                # 多单止损
                pnl = (price - entry_price) * hands * multiplier
                commission = (entry_price + price) * hands * multiplier * 0.00006
                slip = 1 * hands * multiplier * 2
                net_pnl = pnl - commission - slip
                trades.append({
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "exit_time": current_time,
                    "exit_price": price,
                    "direction": "LONG",
                    "pnl": round(net_pnl, 2),
                    "exit_reason": "止损",
                    "stop_loss": stop_loss
                })
                print(f"[止损] {name} 多单 @ {price:.2f}, 盈亏={net_pnl:.2f}")
                position = 0
            
            elif position == -1 and price >= stop_loss:
                # 空单止损
                pnl = (entry_price - price) * hands * multiplier
                commission = (entry_price + price) * hands * multiplier * 0.00006
                slip = 1 * hands * multiplier * 2
                net_pnl = pnl - commission - slip
                trades.append({
                    "entry_time": entry_time,
                    "entry_price": entry_price,
                    "exit_time": current_time,
                    "exit_price": price,
                    "direction": "SHORT",
                    "pnl": round(net_pnl, 2),
                    "exit_reason": "止损",
                    "stop_loss": stop_loss
                })
                print(f"[止损] {name} 空单 @ {price:.2f}, 盈亏={net_pnl:.2f}")
                position = 0
        
        # 生成报告
        if not trades:
            print(f"[WARN] {name} 无交易记录")
            return {
                "symbol": symbol,
                "name": name,
                "period": f"{first_time[:10]} ~ {last_time[:10]}",
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
        
        # 获取实际回测区间
        if len(klines) > 0:
            first_time = str(klines.iloc[0]['datetime'])[:10]
            last_time = str(klines.iloc[-1]['datetime'])[:10]
            period_str = f"{first_time} ~ {last_time}"
        else:
            period_str = "未知"
        
        # 计算资金曲线
        capital = INITIAL_CAPITAL
        capital_curve = [{"date": first_time if len(klines) > 0 else "unknown", "capital": capital}]
        for t in trades:
            capital += t['pnl']
            capital_curve.append({"date": t['exit_time'][:10], "capital": round(capital, 2)})
        
        report = {
            "symbol": symbol,
            "name": name,
            "period": period_str,
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
    print("="*80)
    print("分型趋势策略 - CSV 数据回测（结果完全可复现）")
    print(f"数据文件：{KLINE_CSV_FILE}")
    print(f"初始资金：{INITIAL_CAPITAL}元")
    print(f"仓位比例：{MAX_POSITION_RATIO*100}%")
    print(f"分型间隔：{FRACTAL_MIN_INTERVAL}根 K 线")
    print(f"分型力度：>={FRACTAL_STRENGTH_TICKS} tick")
    print(f"交易周期：60 分钟 K 线")
    print("="*80)
    
    results = {}
    for symbol_info in SYMBOLS:
        report = run_backtest(symbol_info)
        if report:
            results[symbol_info["code"]] = report
    
    # 保存结果
    os.makedirs("backtest_results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"backtest_results/fractal_adx_90d_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"[OK] 回测结果已保存：{output_file}")
    print("="*80)
    
    # 打印汇总
    print("\n回测汇总:")
    print("-"*80)
    print(f"{'品种':<12} {'交易笔数':<10} {'总盈亏 (元)':<15} {'胜率':<10} {'最终资金':<15}")
    print("-"*80)
    for code, report in results.items():
        if "error" not in report:
            print(f"{report['name']:<12} {report['total_trades']:<10} {report['total_pnl']:<15.2f} {report['win_rate']:<10.2f}% {report['final_capital']:<15.2f}")
        else:
            print(f"{report['name']:<12} {'失败':<10} {report.get('error', '未知错误'):<40}")
    print("-"*80)
