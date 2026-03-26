# -*- coding: utf-8 -*-
"""
获取并保存 K 线数据到 CSV（确保回测数据稳定）
"""

from tqsdk import TqApi, TqAuth
import pandas as pd
import sys
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

print("="*80)
print("获取锰硅 60 分钟 K 线数据并保存")
print("="*80)

api = TqApi(auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD))

# 获取最近 5000 根 60 分钟 K 线（约 3-4 年）
klines = api.get_kline_serial("KQ.m@CZCE.SM", duration_seconds=3600, data_length=5000)

api.close()

print(f"\n获取到 {len(klines)} 根 K 线")

# 检查数据有效性
if len(klines) == 0 or pd.isna(klines.iloc[0]['open']):
    print("[ERROR] K 线数据无效！")
    exit(1)

# 打印时间范围
first_time = str(klines.iloc[0]['datetime'])[:10]
last_time = str(klines.iloc[-1]['datetime'])[:10]
print(f"时间范围：{first_time} ~ {last_time}")

# 保存为 CSV
output_file = 'kline_data_sm_60m.csv'
klines.to_csv(output_file, index=False)
print(f"\n[OK] 数据已保存到：{output_file}")
print(f"文件大小：{len(klines)} 行 x {len(klines.columns)} 列")
