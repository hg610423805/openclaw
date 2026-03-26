# -*- coding: utf-8 -*-
"""
检查 TQSDK 回测模式实际有数据的时间范围
"""

from tqsdk import TqApi, TqAuth, TqBacktest
from datetime import datetime
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

# 测试不同年份
test_ranges = [
    (datetime(2020, 1, 1), datetime(2020, 12, 31)),
    (datetime(2021, 1, 1), datetime(2021, 12, 31)),
    (datetime(2022, 1, 1), datetime(2022, 12, 31)),
    (datetime(2023, 1, 1), datetime(2023, 12, 31)),
]

for start, end in test_ranges:
    api = TqApi(
        auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
        backtest=TqBacktest(start_dt=start, end_dt=end)
    )
    
    klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=100)
    
    if len(klines) > 0 and not __import__('pandas').isna(klines.iloc[0]['open']):
        first = str(klines.iloc[0]['datetime'])[:10]
        last = str(klines.iloc[-1]['datetime'])[:10]
        print(f"{start.year}年：✅ 有效，{len(klines)} 根 K 线，{first} ~ {last}")
    else:
        print(f"{start.year}年：❌ 无效数据")
    
    api.close()
