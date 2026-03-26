# -*- coding: utf-8 -*-
"""
调试 ADX 值分布
"""

from tqsdk import TqApi, TqAuth, TqBacktest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=365*3)

def calculate_adx(df, period=14):
    high = df['high']
    low = df['low']
    close = df['close']
    
    diff_high = high.diff()
    diff_low = low.diff()
    
    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)
    
    plus_dm[(diff_high > diff_low) & (diff_high > 0)] = diff_high[(diff_high > diff_low) & (diff_high > 0)]
    minus_dm[(diff_low > diff_high) & (diff_low > 0)] = diff_low[(diff_low > diff_high) & (diff_low > 0)]
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    plus_dm_smooth = plus_dm.ewm(span=period, adjust=False).mean()
    minus_dm_smooth = minus_dm.ewm(span=period, adjust=False).mean()
    tr_smooth = tr.ewm(span=period, adjust=False).mean()
    
    plus_di = pd.Series(0.0, index=df.index)
    minus_di = pd.Series(0.0, index=df.index)
    
    mask = tr_smooth > 0
    plus_di[mask] = 100 * plus_dm_smooth[mask] / tr_smooth[mask]
    minus_di[mask] = 100 * minus_dm_smooth[mask] / tr_smooth[mask]
    
    di_sum = plus_di + minus_di
    di_diff = abs(plus_di - minus_di)
    dx = pd.Series(0.0, index=df.index)
    mask = di_sum > 0
    dx[mask] = 100 * di_diff[mask] / di_sum[mask]
    
    adx = dx.ewm(span=period, adjust=False).mean()
    
    return adx

print("="*80)
print("调试 ADX 值分布")
print(f"回测区间：{START_DATE} ~ {END_DATE}")
print("="*80)

api = TqApi(
    auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
    backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE)
)

klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=15000)
adx = calculate_adx(klines)

print(f"\nK 线数量：{len(klines)} 根")
print(f"ADX 有效数量：{adx.notna().sum()} 根")

# ADX 分布
print(f"\nADX 统计:")
print(f"  最小值：{adx.min():.2f}")
print(f"  最大值：{adx.max():.2f}")
print(f"  平均值：{adx.mean():.2f}")
print(f"  中位数：{adx.median():.2f}")

# ADX>20 的比例
adx_gt_20 = (adx > 20).sum()
adx_gt_25 = (adx > 25).sum()
adx_gt_30 = (adx > 30).sum()

print(f"\nADX 阈值统计:")
print(f"  ADX>20: {adx_gt_20} 根 ({adx_gt_20/len(klines)*100:.1f}%)")
print(f"  ADX>25: {adx_gt_25} 根 ({adx_gt_25/len(klines)*100:.1f}%)")
print(f"  ADX>30: {adx_gt_30} 根 ({adx_gt_30/len(klines)*100:.1f}%)")

# 估算交易笔数
# 假设每个分型确认时检查 ADX
total_fractals = 3959  # 从之前的调试结果
print(f"\n估算交易笔数:")
print(f"  分型总数：{total_fractals}")
print(f"  如果 ADX>20: 约 {total_fractals * adx_gt_20/len(klines):.0f} 笔")
print(f"  如果 ADX>25: 约 {total_fractals * adx_gt_25/len(klines):.0f} 笔")
print(f"  如果 ADX>30: 约 {total_fractals * adx_gt_30/len(klines):.0f} 笔")

api.close()
