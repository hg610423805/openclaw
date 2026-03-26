# -*- coding: utf-8 -*-
"""
检查回测结果中的交易时间
"""

import json
import pandas as pd

# 读取回测结果
with open('backtest_results/fractal_adx_90d_20260324_201237.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

trades = data['KQ.m@CZCE.SM']['trades']

print("="*80)
print("检查交易时间戳")
print("="*80)

for i, trade in enumerate(trades[:5]):
    entry_ts = trade['entry_time']
    exit_ts = trade['exit_time']
    
    print(f"\n交易 {i+1}:")
    print(f"  开仓时间戳：{entry_ts} (类型：{type(entry_ts).__name__})")
    print(f"  平仓时间戳：{exit_ts} (类型：{type(exit_ts).__name__})")
    
    # 尝试转换
    try:
        entry_dt = pd.to_datetime(float(entry_ts), unit='ns')
        print(f"  开仓时间：{entry_dt}")
    except Exception as e:
        print(f"  转换失败：{e}")
    
    try:
        exit_dt = pd.to_datetime(float(exit_ts), unit='ns')
        print(f"  平仓时间：{exit_dt}")
    except Exception as e:
        print(f"  转换失败：{e}")
