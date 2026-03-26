# -*- coding: utf-8 -*-
"""
检查 K 线实际时间范围
"""

from tqsdk import TqApi, TqAuth, TqBacktest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

# 3 年回测
END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=365*3)

print("="*80)
print("检查 K 线实际时间范围")
print(f"设定回测区间：{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
print("="*80)

api = TqApi(
    auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
    backtest=TqBacktest(
        start_dt=START_DATE,
        end_dt=END_DATE
    )
)

# 获取 60 分钟 K 线
klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=15000)

print(f"\n获取到 {len(klines)} 根 60 分钟 K 线")

if len(klines) > 0:
    first_time = klines.iloc[0]['datetime']
    last_time = klines.iloc[-1]['datetime']
    print(f"第一根 K 线时间：{first_time}")
    print(f"最后一根 K 线时间：{last_time}")
    
    # 检查时间戳类型
    print(f"\n时间戳类型：{type(first_time)}")
    print(f"第一根时间戳值：{first_time}")

api.close()
