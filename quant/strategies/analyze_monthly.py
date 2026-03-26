# -*- coding: utf-8 -*-
"""
分析月度盈亏和开仓手数
"""

import json
import pandas as pd
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 读取回测结果（使用最新修正版）
with open('backtest_results/fractal_adx_90d_20260324_201237.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取锰硅数据
sm_data = data['KQ.m@CZCE.SM']
trades = sm_data['trades']

print("="*80)
print("锰硅策略 - 月度盈亏分析报告")
print(f"回测区间：{sm_data['period']}")
print(f"总交易笔数：{sm_data['total_trades']} 笔")
print(f"总盈亏：{sm_data['total_pnl']:.2f} 元")
print("="*80)

# 转换时间戳
def timestamp_to_datetime(ts):
    try:
        ts_float = float(ts)
        return pd.to_datetime(ts_float, unit='ns').to_pydatetime()
    except:
        return None

# 按月统计
monthly_stats = {}

for trade in trades:
    exit_dt = timestamp_to_datetime(trade['exit_time'])
    if not exit_dt:
        continue
    
    month_key = exit_dt.strftime('%Y-%m')
    
    if month_key not in monthly_stats:
        monthly_stats[month_key] = {
            'pnl': 0,
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_hands': 0,
            'win_pnl': 0,
            'loss_pnl': 0
        }
    
    # 估算开仓手数（根据盈亏反推）
    pnl = trade['pnl']
    entry_price = trade['entry_price']
    exit_price = trade['exit_price']
    direction = trade['direction']
    
    # 锰硅乘数=5
    multiplier = 5
    if direction == 'LONG':
        price_diff = exit_price - entry_price
    else:
        price_diff = entry_price - exit_price
    
    # 扣除手续费和滑点前的盈亏
    # 手续费 = (entry+exit) * hands * 5 * 0.00006
    # 滑点 = 1 * hands * 5 * 2 = hands * 10
    # net_pnl = price_diff * hands * 5 - (entry+exit) * hands * 5 * 0.00006 - hands * 10
    # 简化估算：hands ≈ net_pnl / (price_diff * 5)
    if price_diff != 0:
        hands = abs(pnl / (price_diff * multiplier))
    else:
        hands = 1  # 平手情况
    
    monthly_stats[month_key]['pnl'] += pnl
    monthly_stats[month_key]['trades'] += 1
    monthly_stats[month_key]['total_hands'] += hands
    
    if pnl > 0:
        monthly_stats[month_key]['wins'] += 1
        monthly_stats[month_key]['win_pnl'] += pnl
    else:
        monthly_stats[month_key]['losses'] += 1
        monthly_stats[month_key]['loss_pnl'] += pnl

# 打印月度报告
print(f"\n{'月份':<10} {'盈亏 (元)':<15} {'交易笔数':<10} {'胜率':<10} {'平均手数':<10} {'均笔盈亏':<12}")
print("-"*80)

total_pnl = 0
total_trades = 0
total_hands = 0

for month in sorted(monthly_stats.keys()):
    stats = monthly_stats[month]
    win_rate = stats['wins'] / stats['trades'] * 100 if stats['trades'] > 0 else 0
    avg_hands = stats['total_hands'] / stats['trades'] if stats['trades'] > 0 else 0
    avg_pnl = stats['pnl'] / stats['trades'] if stats['trades'] > 0 else 0
    
    pnl_sign = "+" if stats['pnl'] > 0 else ""
    
    print(f"{month} {pnl_sign}{stats['pnl']:<14.2f} {stats['trades']:<10} {win_rate:<10.1f}% {avg_hands:<10.1f} {avg_pnl:<12.2f}")
    
    total_pnl += stats['pnl']
    total_trades += stats['trades']
    total_hands += stats['total_hands']

print("-"*80)
print(f"{'合计':<10} {total_pnl:<15.2f} {total_trades:<10} {total_trades>0 and total_trades>0 and (sum(s['wins'] for s in monthly_stats.values())/total_trades*100):<10.1f}% {total_hands/total_trades if total_trades>0 else 0:<10.1f} {total_pnl/total_trades if total_trades>0 else 0:<12.2f}")

# 年度汇总
print(f"\n{'='*80}")
print("年度汇总")
print(f"{'='*80}")

yearly_stats = {}
for month, stats in monthly_stats.items():
    year = month[:4]
    if year not in yearly_stats:
        yearly_stats[year] = {'pnl': 0, 'trades': 0, 'wins': 0, 'hands': 0}
    yearly_stats[year]['pnl'] += stats['pnl']
    yearly_stats[year]['trades'] += stats['trades']
    yearly_stats[year]['wins'] += stats['wins']
    yearly_stats[year]['hands'] += stats['total_hands']

print(f"\n{'年份':<10} {'盈亏 (元)':<15} {'交易笔数':<10} {'胜率':<10} {'平均手数':<10}")
print("-"*80)

for year in sorted(yearly_stats.keys()):
    stats = yearly_stats[year]
    win_rate = stats['wins'] / stats['trades'] * 100 if stats['trades'] > 0 else 0
    avg_hands = stats['hands'] / stats['trades'] if stats['trades'] > 0 else 0
    
    pnl_sign = "+" if stats['pnl'] > 0 else ""
    
    print(f"{year} {pnl_sign}{stats['pnl']:<14.2f} {stats['trades']:<10} {win_rate:<10.1f}% {avg_hands:<10.1f}")

# 连续盈亏分析
print(f"\n{'='*80}")
print("连续盈亏分析")
print(f"{'='*80}")

max_consecutive_wins = 0
max_consecutive_losses = 0
current_wins = 0
current_losses = 0

sorted_months = sorted(monthly_stats.keys())
for month in sorted_months:
    stats = monthly_stats[month]
    if stats['pnl'] > 0:
        current_wins += 1
        current_losses = 0
        max_consecutive_wins = max(max_consecutive_wins, current_wins)
    else:
        current_losses += 1
        current_wins = 0
        max_consecutive_losses = max(max_consecutive_losses, current_losses)

print(f"\n最长连续盈利月数：{max_consecutive_wins} 个月")
print(f"最长连续亏损月数：{max_consecutive_losses} 个月")

# 月度盈亏分布
profitable_months = sum(1 for s in monthly_stats.values() if s['pnl'] > 0)
losing_months = sum(1 for s in monthly_stats.values() if s['pnl'] <= 0)

print(f"\n盈利月份：{profitable_months} 个 ({profitable_months/len(monthly_stats)*100:.1f}%)")
print(f"亏损月份：{losing_months} 个 ({losing_months/len(monthly_stats)*100:.1f}%)")

print(f"\n{'='*80}")
print("报告生成完毕")
print(f"{'='*80}")
