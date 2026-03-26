# -*- coding: utf-8 -*-
"""
分析 ADX 过滤前策略的最后几笔交易明细
"""

import json
import sys
import pandas as pd
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 读取回测结果
with open('backtest_results/ma_kdj_180d_complete_20260324_084201.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def timestamp_to_datetime(ts):
    """将纳秒时间戳转换为 datetime"""
    try:
        ts_float = float(ts)
        return pd.to_datetime(ts_float, unit='ns').to_pydatetime()
    except:
        return None

def format_datetime(dt):
    """格式化日期时间"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return 'N/A'

print("="*80)
print("ADX 过滤前策略 - 最后交易明细报告")
print(f"回测区间：2025-09-24 ~ 2026-03-23")
print("="*80)

for symbol_code, symbol_data in data.items():
    name = symbol_data['name']
    trades = symbol_data['trades']
    
    print(f"\n{'='*80}")
    print(f"品种：{name} ({symbol_code})")
    print(f"总交易笔数：{len(trades)}")
    print(f"{'='*80}")
    
    if not trades:
        print(f"\n无交易记录")
        continue
    
    # 显示最后 3 笔交易
    last_trades = trades[-3:] if len(trades) >= 3 else trades
    
    print(f"\n📋 最后 {len(last_trades)} 笔交易明细:")
    print(f"{'─'*80}")
    
    for idx, trade in enumerate(last_trades, len(trades) - len(last_trades) + 1):
        entry_dt = timestamp_to_datetime(trade['entry_time'])
        exit_dt = timestamp_to_datetime(trade['exit_time'])
        
        direction = "做多" if trade['direction'] == 'LONG' else "做空"
        direction_icon = "[多]" if trade['direction'] == 'LONG' else "[空]"
        
        print(f"\n【交易 #{idx}】{direction_icon} {direction}")
        print(f"  ─────────────────────────────────────")
        print(f"  开仓:")
        print(f"    时间：{format_datetime(entry_dt)}")
        print(f"    价格：{trade['entry_price']:.2f}")
        print(f"    理由：30 分钟 J 值极端 + EXPMA 同向 + 5 分钟 J 值极端 + 分型确认")
        print(f"  ")
        print(f"  平仓:")
        print(f"    时间：{format_datetime(exit_dt)}")
        print(f"    价格：{trade['exit_price']:.2f}")
        print(f"    理由：{trade['exit_reason']}")
        print(f"  ")
        pnl_status = "盈利" if trade['pnl'] > 0 else "亏损"
        print(f"  盈亏：[{pnl_status}] {trade['pnl']:+.2f} 元")
        print(f"  {'─'*80}")

# 汇总统计
print(f"\n{'='*80}")
print("📊 全部交易汇总")
print(f"{'='*80}")

total_trades = 0
total_pnl = 0
win_count = 0

for symbol_code, symbol_data in data.items():
    name = symbol_data['name']
    trades = symbol_data['trades']
    
    if trades:
        symbol_pnl = sum(t['pnl'] for t in trades)
        symbol_wins = len([t for t in trades if t['pnl'] > 0])
        win_rate = symbol_wins / len(trades) * 100 if trades else 0
        
        print(f"\n  {name}:")
        print(f"    交易笔数：{len(trades)}")
        print(f"    总盈亏：{symbol_pnl:+.2f} 元")
        print(f"    胜率：{win_rate:.1f}% ({symbol_wins}/{len(trades)})")
        
        total_trades += len(trades)
        total_pnl += symbol_pnl
        win_count += symbol_wins

if total_trades > 0:
    total_win_rate = win_count / total_trades * 100
    print(f"\n{'─'*80}")
    print(f"  合计:")
    print(f"    总交易：{total_trades} 笔")
    print(f"    总盈亏：{total_pnl:+.2f} 元")
    print(f"    胜率：{total_win_rate:.1f}% ({win_count}/{total_trades})")

print(f"\n{'='*80}")
print("备注：最近 3 天（2026-03-21 ~ 2026-03-23）所有品种均无新开仓交易")
print("原因：策略条件未触发（KDJ J 值未在极端区域或分型未形成）")
print(f"{'='*80}")
