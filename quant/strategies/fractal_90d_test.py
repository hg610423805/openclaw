# -*- coding: utf-8 -*-
"""
分型策略 - 最近 90 天回测（从 CSV 固定数据中截取）
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, '..')

INITIAL_CAPITAL = 100000
MAX_POSITION_RATIO = 0.5
COMMISSION_RATIO = 0.00006
SLIPPAGE = 1


def detect_fractals(klines):
    bottoms = []
    tops = []
    for i in range(1, len(klines) - 1):
        if (klines.iloc[i]['low'] < klines.iloc[i-1]['low'] and 
            klines.iloc[i]['low'] < klines.iloc[i+1]['low']):
            strength = min(klines.iloc[i-1]['low'], klines.iloc[i+1]['low']) - klines.iloc[i]['low']
            bottoms.append({'index': i, 'low': klines.iloc[i]['low'], 'confirm_idx': i + 1, 'strength': strength})
        if (klines.iloc[i]['high'] > klines.iloc[i-1]['high'] and 
            klines.iloc[i]['high'] > klines.iloc[i+1]['high']):
            strength = klines.iloc[i]['high'] - max(klines.iloc[i-1]['high'], klines.iloc[i+1]['high'])
            tops.append({'index': i, 'high': klines.iloc[i]['high'], 'confirm_idx': i + 1, 'strength': strength})
    return bottoms, tops


# 读取 CSV
klines = pd.read_csv('kline_data_sm_60m.csv')
total = len(klines)

# 取最后 90 天的数据（每天约 8 根 60 分钟 K 线）
last_n = 90 * 8  # 720 根
if last_n > total:
    last_n = total

klines_90d = klines.iloc[total - last_n:].reset_index(drop=True)

print("="*80)
print("分型策略 - 最近 90 天回测（CSV 固定数据）")
print(f"总 K 线：{total} 根，截取最后 {len(klines_90d)} 根")
print(f"初始资金：{INITIAL_CAPITAL} 元")
print("="*80)

# 检测分型
bottoms, tops = detect_fractals(klines_90d)
print(f"[INFO] 底分型：{len(bottoms)} 个，顶分型：{len(tops)} 个，合计 {len(bottoms)+len(tops)} 个")

# 回测
trades = []
position = 0
entry_price = 0
entry_time = ""
stop_loss = 0
hands = 1
prev_bottom_low = None
prev_top_high = None
last_bottom_idx = -1
last_top_idx = -1
multiplier = 5
tick = 2

for i in range(2, len(klines_90d)):
    price = klines_90d.iloc[i]['close']
    current_time = str(klines_90d.iloc[i]['datetime'])
    
    current_bottom = None
    current_top = None
    
    for b in bottoms:
        if b['confirm_idx'] == i:
            if last_bottom_idx >= 0 and (b['index'] - last_bottom_idx) < 1:
                continue
            current_bottom = b
            break
    
    for t in tops:
        if t['confirm_idx'] == i:
            if last_top_idx >= 0 and (t['index'] - last_top_idx) < 1:
                continue
            current_top = t
            break
    
    # 底分型
    if current_bottom:
        if position == 1:
            old_stop = stop_loss
            stop_loss = current_bottom['low']
            if stop_loss > old_stop:
                pass  # 移动止损
        
        if prev_bottom_low is not None and position == 0:
            if current_bottom['low'] > prev_bottom_low:
                entry_price = price
                entry_time = current_time
                hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * 0.10)))
                stop_loss = current_bottom['low']
                position = 1
        
        prev_bottom_low = current_bottom['low']
        last_bottom_idx = current_bottom['index']
    
    # 顶分型
    if current_top:
        if position == -1:
            old_stop = stop_loss
            stop_loss = current_top['high']
            if stop_loss < old_stop:
                pass  # 移动止损
        
        if prev_top_high is not None and position == 0:
            if current_top['high'] < prev_top_high:
                entry_price = price
                entry_time = current_time
                hands = max(1, int(INITIAL_CAPITAL * MAX_POSITION_RATIO / (price * multiplier * 0.10)))
                stop_loss = current_top['high']
                position = -1
        
        prev_top_high = current_top['high']
        last_top_idx = current_top['index']
    
    # 止损
    if position == 1 and price <= stop_loss:
        pnl = (price - entry_price) * hands * multiplier
        commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
        slip = SLIPPAGE * hands * multiplier * 2
        net_pnl = pnl - commission - slip
        trades.append({
            "entry_time": entry_time, "entry_price": entry_price,
            "exit_time": current_time, "exit_price": price,
            "direction": "LONG", "pnl": round(net_pnl, 2), "hands": hands
        })
        position = 0
    
    elif position == -1 and price >= stop_loss:
        pnl = (entry_price - price) * hands * multiplier
        commission = (entry_price + price) * hands * multiplier * COMMISSION_RATIO
        slip = SLIPPAGE * hands * multiplier * 2
        net_pnl = pnl - commission - slip
        trades.append({
            "entry_time": entry_time, "entry_price": entry_price,
            "exit_time": current_time, "exit_price": price,
            "direction": "SHORT", "pnl": round(net_pnl, 2), "hands": hands
        })
        position = 0

# 汇总
total_pnl = sum(t['pnl'] for t in trades)
winning = [t for t in trades if t['pnl'] > 0]
losing = [t for t in trades if t['pnl'] <= 0]
win_rate = len(winning) / len(trades) * 100 if trades else 0

print(f"\n{'='*80}")
print(f"回测结果")
print(f"{'='*80}")
print(f"交易笔数：{len(trades)}")
print(f"盈利笔数：{len(winning)}")
print(f"亏损笔数：{len(losing)}")
print(f"胜率：{win_rate:.2f}%")
print(f"总盈亏：{total_pnl:.2f} 元")
print(f"最终资金：{INITIAL_CAPITAL + total_pnl:.2f} 元")
print(f"收益率：{total_pnl/INITIAL_CAPITAL*100:.2f}%")

if winning:
    print(f"\n盈利交易：")
    print(f"  平均盈利：{sum(t['pnl'] for t in winning)/len(winning):.2f} 元")
    print(f"  最大单笔：{max(t['pnl'] for t in trades):.2f} 元")

if losing:
    print(f"\n亏损交易：")
    print(f"  平均亏损：{sum(t['pnl'] for t in losing)/len(losing):.2f} 元")
    print(f"  最大单笔：{min(t['pnl'] for t in trades):.2f} 元")

if trades:
    avg_hands = sum(t['hands'] for t in trades) / len(trades)
    print(f"\n平均手数：{avg_hands:.1f} 手")

# 保存
with open('backtest_results/fractal_90d_csv.json', 'w', encoding='utf-8') as f:
    json.dump({"trades": trades, "total_pnl": total_pnl, "win_rate": win_rate, "total_trades": len(trades)}, f, ensure_ascii=False, indent=2)

print(f"\n[OK] 结果已保存")
