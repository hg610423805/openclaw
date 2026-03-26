import pandas as pd
from decimal import Decimal

# 检查时间戳（可能是纳秒）
timestamps = [
    1.7582628e+18,  # 锰硅最后
    1.7580879e+18,  # 玻璃最后
    1.7568198e+18,  # 玉米最后
]

print("时间戳解析测试:")
print("="*60)

for ts in timestamps:
    # 尝试纳秒
    try:
        dt_ns = pd.to_datetime(ts, unit='ns')
        print(f"{ts:.0f} -> 纳秒：{dt_ns}")
    except Exception as e:
        print(f"{ts:.0f} -> 纳秒错误：{e}")
    
    # 尝试毫秒
    try:
        dt_ms = pd.to_datetime(ts, unit='ms')
        print(f"           毫秒：{dt_ms}")
    except Exception as e:
        print(f"           毫秒错误：{e}")
    
    # 尝试微秒
    try:
        dt_us = pd.to_datetime(ts, unit='us')
        print(f"           微秒：{dt_us}")
    except Exception as e:
        print(f"           微秒错误：{e}")
    
    print()
