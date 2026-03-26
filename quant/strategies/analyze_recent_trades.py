# -*- coding: utf-8 -*-
"""
分析 ADX 过滤前策略最近 3 天的交易明细
"""

import json
import sys
from datetime import datetime

# 设置输出编码为 UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# 读取回测结果
with open('backtest_results/ma_kdj_180d_complete_20260324_084201.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 回测结束日期是 2026-03-23，最近 3 天是 2026-03-21, 2026-03-22, 2026-03-23
END_DATE = datetime(2026, 3, 23)
THREE_DAYS_AGO = datetime(2026, 3, 21)

def timestamp_to_datetime(ts):
    """将纳秒时间戳转换为 datetime（JSON 保存时是纳秒）"""
    try:
        # 处理科学计数法
        ts_float = float(ts)
        # 使用 pandas 解析纳秒时间戳
        import pandas as pd
        return pd.to_datetime(ts_float, unit='ns').to_pydatetime()
    except:
        return None

def format_datetime(dt):
    """格式化日期时间"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return 'N/A'

def is_within_3_days(entry_time_str):
    """检查是否在最近 3 天内"""
    dt = timestamp_to_datetime(entry_time_str)
    if dt:
        return THREE_DAYS_AGO <= dt <= END_DATE
    return False

print("="*80)
print("ADX 过滤前策略 - 最近 3 天交易明细报告")
print(f"统计区间：2026-03-21 ~ 2026-03-23")
print("="*80)

for symbol_code, symbol_data in data.items():
    name = symbol_data['name']
    print(f"\n{'='*80}")
    print(f"品种：{name} ({symbol_code})")
    print(f"{'='*80}")
    
    # 筛选最近 3 天的交易
    recent_trades = [t for t in symbol_data['trades'] if is_within_3_days(t['entry_time'])]
    
    if not recent_trades:
        print(f"\n❌ 最近 3 天无开仓交易")
        print(f"\n可能原因：")
        print(f"  1. 30 分钟 KDJ J 值未在极端区域（多：J<20, 空：J>80）")
        print(f"  2. 30 分钟 EXPMA 方向不明确（未形成金叉/死叉）")
        print(f"  3. 5 分钟级别未形成底分型/顶分型确认")
        print(f"  4. 5 分钟 KDJ J 值未满足条件（多：J<20, 空：J>80）")
        print(f"  5. 5 分钟 EXPMA 与 30 分钟不同向")
        print(f"  6. 已达到每日最大交易次数限制（3 笔/天）")
        continue
    
    print(f"\n📊 最近 3 天交易数量：{len(recent_trades)} 笔")
    print(f"\n{'─'*80}")
    
    for idx, trade in enumerate(recent_trades, 1):
        entry_dt = timestamp_to_datetime(trade['entry_time'])
        exit_dt = timestamp_to_datetime(trade['exit_time'])
        
        direction = "🟢 做多" if trade['direction'] == 'LONG' else "🔴 做空"
        
        print(f"\n【交易 #{idx}】")
        print(f"  方向：{direction}")
        print(f"  ─────────────────────────────────────")
        print(f"  📥 开仓信息:")
        print(f"     时间：{format_datetime(entry_dt)}")
        print(f"     价格：{trade['entry_price']:.2f}")
        print(f"     理由：30 分钟 J<20/>80 + EXPMA 同向 + 5 分钟 J<20/80 + 分型确认")
        print(f"  ")
        print(f"  📤 平仓信息:")
        print(f"     时间：{format_datetime(exit_dt)}")
        print(f"     价格：{trade['exit_price']:.2f}")
        print(f"     理由：{trade['exit_reason']}")
        print(f"  ")
        pnl_icon = "✅" if trade['pnl'] > 0 else "❌"
        print(f"  💰 盈亏：{pnl_icon} {trade['pnl']:+.2f} 元")
        print(f"  {'─'*80}")

# 汇总统计
print(f"\n{'='*80}")
print("📈 最近 3 天汇总统计")
print(f"{'='*80}")

total_trades = 0
total_pnl = 0
win_count = 0

for symbol_code, symbol_data in data.items():
    name = symbol_data['name']
    recent_trades = [t for t in symbol_data['trades'] if is_within_3_days(t['entry_time'])]
    
    if recent_trades:
        symbol_pnl = sum(t['pnl'] for t in recent_trades)
        symbol_wins = len([t for t in recent_trades if t['pnl'] > 0])
        
        print(f"\n  {name}:")
        print(f"    交易笔数：{len(recent_trades)}")
        print(f"    总盈亏：{symbol_pnl:+.2f} 元")
        print(f"    盈利笔数：{symbol_wins}/{len(recent_trades)}")
        
        total_trades += len(recent_trades)
        total_pnl += symbol_pnl
        win_count += symbol_wins

if total_trades == 0:
    print(f"\n  ⚠️  最近 3 天所有品种均无交易")
else:
    win_rate = win_count / total_trades * 100 if total_trades > 0 else 0
    print(f"\n{'─'*80}")
    print(f"  合计:")
    print(f"    总交易：{total_trades} 笔")
    print(f"    总盈亏：{total_pnl:+.2f} 元")
    print(f"    胜率：{win_rate:.1f}% ({win_count}/{total_trades})")

print(f"\n{'='*80}")
print("报告生成完毕")
print(f"{'='*80}")
