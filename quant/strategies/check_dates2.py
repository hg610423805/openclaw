import pandas as pd

# 检查各品种最后一笔交易的时间（使用 pandas 处理大时间戳）
trades = {
    "锰硅最后": 1.7582628e+18,
    "玻璃最后": 1.7580897e+18,
    "玉米最后": 1.7568648e+18,
}

print("交易时间戳转换 (使用 pandas):")
for name, ts in trades.items():
    try:
        dt = pd.to_datetime(ts, unit='ms')
        print(f"  {name}: {dt}")
    except Exception as e:
        print(f"  {name}: 错误 - {e}")

# 检查回测结束日期
print(f"\n回测结束日期：2026-03-23")
print(f"最近 3 天：2026-03-21, 2026-03-22, 2026-03-23")

# 手动检查锰硅最后几笔交易
print("\n锰硅最后几笔交易时间:")
sm_trades = [
    1.7582628e+18,
    1.7573991e+18,
    1.7556681e+18,
    1.7554842e+18,
    1.7537715e+18,
]

for ts in sm_trades:
    try:
        dt = pd.to_datetime(ts, unit='ms')
        print(f"  {dt}")
    except Exception as e:
        print(f"  {ts}: 错误 - {e}")

# 检查玻璃最后几笔交易
print("\n玻璃最后几笔交易时间:")
fg_trades = [
    1.7580897e+18,
    1.7576391e+18,
    1.7563464e+18,
    1.7563446e+18,
    1.7552628e+18,
]

for ts in fg_trades:
    try:
        dt = pd.to_datetime(ts, unit='ms')
        print(f"  {dt}")
    except Exception as e:
        print(f"  {ts}: 错误 - {e}")
