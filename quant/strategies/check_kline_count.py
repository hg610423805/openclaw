# -*- coding: utf-8 -*-
"""
检查 5 年 60 分钟 K 线数据量
"""

from tqsdk import TqApi, TqAuth, TqBacktest
from datetime import datetime, timedelta
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=365*5)

print("="*80)
print("检查 5 年 60 分钟 K 线数据量")
print(f"回测区间：{START_DATE.strftime('%Y-%m-%d')} ~ {END_DATE.strftime('%Y-%m-%d')}")
print("="*80)

api = TqApi(
    auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
    backtest=TqBacktest(
        start_dt=START_DATE,
        end_dt=END_DATE
    )
)

# 获取 60 分钟 K 线
klines_60m = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=50000)

print(f"\n60 分钟 K 线数量：{len(klines_60m)} 根")

if len(klines_60m) > 0:
    first_date = str(klines_60m.iloc[0]['datetime'])[:10]
    last_date = str(klines_60m.iloc[-1]['datetime'])[:10]
    print(f"数据区间：{first_date} ~ {last_date}")
    
    # 估算
    expected_days = (END_DATE - START_DATE).days
    print(f"\n预期天数：{expected_days}天")
    print(f"预期 60 分钟 K 线：约{expected_days * 8}根（按每天 8 根计算）")

# 获取 5 分钟 K 线对比
klines_5m = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=300, data_length=200000)
print(f"\n5 分钟 K 线数量：{len(klines_5m)} 根")

api.close()
