# -*- coding: utf-8 -*-
"""
调试 K 线数据格式
"""

from tqsdk import TqApi, TqAuth, TqBacktest
from datetime import datetime
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

api = TqApi(
    auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
    backtest=TqBacktest(
        start_dt=datetime(2016, 1, 1),
        end_dt=datetime(2017, 12, 31)
    )
)

klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=100)

print("="*80)
print("调试 K 线数据格式")
print("="*80)

print(f"\nK 线数量：{len(klines)}")
print(f"K 线列名：{klines.columns.tolist()}")

if len(klines) > 0:
    print(f"\n前 3 根 K 线:")
    for i in range(min(3, len(klines))):
        print(f"  K 线 {i}: datetime={klines.iloc[i]['datetime']}, open={klines.iloc[i]['open']}, high={klines.iloc[i]['high']}, low={klines.iloc[i]['low']}, close={klines.iloc[i]['close']}")
    
    # 检测分型
    print(f"\n检测分型:")
    for i in range(1, min(50, len(klines) - 1)):
        # 底分型
        if (klines.iloc[i]['low'] < klines.iloc[i-1]['low'] and 
            klines.iloc[i]['low'] < klines.iloc[i+1]['low']):
            strength = min(klines.iloc[i-1]['low'], klines.iloc[i+1]['low']) - klines.iloc[i]['low']
            print(f"  底分型 @ i={i}, low={klines.iloc[i]['low']}, strength={strength}")
        
        # 顶分型
        if (klines.iloc[i]['high'] > klines.iloc[i-1]['high'] and 
            klines.iloc[i]['high'] > klines.iloc[i+1]['high']):
            strength = klines.iloc[i]['high'] - max(klines.iloc[i-1]['high'], klines.iloc[i+1]['high'])
            print(f"  顶分型 @ i={i}, high={klines.iloc[i]['high']}, strength={strength}")

api.close()
