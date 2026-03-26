# -*- coding: utf-8 -*-
"""
调试分型检测逻辑
"""

from tqsdk import TqApi, TqAuth, TqBacktest
import pandas as pd
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=365*3)

def detect_fractals(klines):
    """检测分型"""
    bottoms = []
    tops = []
    
    for i in range(1, len(klines) - 1):
        # 底分型
        if (klines.iloc[i]['low'] < klines.iloc[i-1]['low'] and 
            klines.iloc[i]['low'] < klines.iloc[i+1]['low']):
            bottoms.append({
                'index': i,
                'low': klines.iloc[i]['low'],
                'confirm_idx': i + 1
            })
        
        # 顶分型
        if (klines.iloc[i]['high'] > klines.iloc[i-1]['high'] and 
            klines.iloc[i]['high'] > klines.iloc[i+1]['high']):
            tops.append({
                'index': i,
                'high': klines.iloc[i]['high'],
                'confirm_idx': i + 1
            })
    
    return bottoms, tops

print("="*80)
print("调试分型检测")
print(f"回测区间：{START_DATE} ~ {END_DATE}")
print("="*80)

api = TqApi(
    auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
    backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE)
)

klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=15000)

print(f"\nK 线数量：{len(klines)} 根")
print(f"K 线区间：{str(klines.iloc[0]['datetime'])[:10]} ~ {str(klines.iloc[-1]['datetime'])[:10]}")

bottoms, tops = detect_fractals(klines)

print(f"\n底分型数量：{len(bottoms)}")
print(f"顶分型数量：{len(tops)}")
print(f"分型总数：{len(bottoms) + len(tops)}")
print(f"分型密度：{len(bottoms) + len(tops):.2f} 个分型 / {len(klines)} 根 K 线 = {(len(bottoms) + len(tops)) / len(klines) * 100:.2f}%")

# 检查分型间隔
if len(bottoms) > 1:
    bottom_intervals = [(bottoms[i]['index'] - bottoms[i-1]['index']) for i in range(1, len(bottoms))]
    print(f"\n底分型间隔统计:")
    print(f"  最小间隔：{min(bottom_intervals)} 根 K 线")
    print(f"  最大间隔：{max(bottom_intervals)} 根 K 线")
    print(f"  平均间隔：{sum(bottom_intervals)/len(bottom_intervals):.2f} 根 K 线")
    print(f"  间隔=1 的数量：{sum(1 for x in bottom_intervals if x == 1)} ({sum(1 for x in bottom_intervals if x == 1)/len(bottom_intervals)*100:.1f}%)")
    print(f"  间隔<=2 的数量：{sum(1 for x in bottom_intervals if x <= 2)} ({sum(1 for x in bottom_intervals if x <= 2)/len(bottom_intervals)*100:.1f}%)")

if len(tops) > 1:
    top_intervals = [(tops[i]['index'] - tops[i-1]['index']) for i in range(1, len(tops))]
    print(f"\n顶分型间隔统计:")
    print(f"  最小间隔：{min(top_intervals)} 根 K 线")
    print(f"  最大间隔：{max(top_intervals)} 根 K 线")
    print(f"  平均间隔：{sum(top_intervals)/len(top_intervals):.2f} 根 K 线")
    print(f"  间隔=1 的数量：{sum(1 for x in top_intervals if x == 1)} ({sum(1 for x in top_intervals if x == 1)/len(top_intervals)*100:.1f}%)")
    print(f"  间隔<=2 的数量：{sum(1 for x in top_intervals if x <= 2)} ({sum(1 for x in top_intervals if x <= 2)/len(top_intervals)*100:.1f}%)")

api.close()
