# -*- coding: utf-8 -*-
"""
日内 5 分钟均线策略 - 简化调试版
"""

from datetime import date, datetime, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd

# ============ 配置 ============
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"

# 只测一个品种先
SYMBOL = "KQ.m@SHFE.rb"  # 螺纹钢主力

# 回测时间：先测 1 个月
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 1, 31)

# 策略参数
DAILY_EXPMA = [5, 10, 20]
INTRADAY_EXPMA = [5, 13]
OPEN_WINDOW = 6  # 30 分钟
ENTRY_BAR = 7
STOP_LOSS_PCT = 0.03  # 3%
# ===========================


def calc_expma(series, period):
    """计算 EXPMA"""
    result = series.copy()
    alpha = 2.0 / (period + 1)
    for i in range(1, len(result)):
        result.iloc[i] = alpha * result.iloc[i] + (1 - alpha) * result.iloc[i-1]
    return result


print("=" * 60)
print("日内 5 分钟均线策略 - 简化版")
print("=" * 60)
print(f"合约：{SYMBOL}")
print(f"时间：{START_DATE} 至 {END_DATE}")
print(f"参数：日线 EXPMA{DAILY_EXPMA}, 5 分钟 EXPMA{INTRADAY_EXPMA}")
print("=" * 60)

try:
    auth = TqAuth(ACCOUNT, PASSWORD)
    sim = TqSim(1000000)
    
    print("正在初始化...")
    api = TqApi(
        account=sim,
        backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
        auth=auth
    )
    
    # 获取数据
    print("获取日线数据...")
    daily_klines = api.get_kline_serial(SYMBOL, 86400)
    print(f"日线：{len(daily_klines)} 根")
    
    print("获取 5 分钟数据...")
    klines_5m = api.get_kline_serial(SYMBOL, 300)
    print(f"5 分钟：{len(klines_5m)} 根")
    
    # 打印前几根看看
    print("\n前 5 根 5 分钟 K 线:")
    for i in range(min(5, len(klines_5m))):
        dt = klines_5m.datetime.iloc[i]
        if isinstance(dt, (int, float)):
            dt = pd.to_datetime(dt, unit='ns')
        print(f"  {dt}: O={klines_5m.open.iloc[i]:.0f} H={klines_5m.high.iloc[i]:.0f} L={klines_5m.low.iloc[i]:.0f} C={klines_5m.close.iloc[i]:.0f}")
    
    # 测试 EXPMA 计算
    print("\n测试 EXPMA 计算...")
    if len(daily_klines) >= 20:
        close = daily_klines['close'].copy()
        e5 = calc_expma(close, 5)
        e10 = calc_expma(close, 10)
        e20 = calc_expma(close, 20)
        
        print(f"最新 EXPMA5:  {e5.iloc[-1]:.2f}")
        print(f"最新 EXPMA10: {e10.iloc[-1]:.2f}")
        print(f"最新 EXPMA20: {e20.iloc[-1]:.2f}")
        
        # 判断方向
        if e5.iloc[-1] > e10.iloc[-1] > e20.iloc[-1]:
            gap1 = (e5.iloc[-1] - e10.iloc[-1]) / e10.iloc[-1] * 100
            gap2 = (e10.iloc[-1] - e20.iloc[-1]) / e20.iloc[-1] * 100
            print(f"-> 多头排列！间距：{gap1:.2f}%, {gap2:.2f}%")
        elif e5.iloc[-1] < e10.iloc[-1] < e20.iloc[-1]:
            print("-> 空头排列！")
        else:
            print("-> 震荡，无明确方向")
    
    # 简单回测：持有
    print("\n开始回测...")
    target_pos = TargetPosTask(api, SYMBOL)
    
    bar_count = 0
    day_count = 0
    last_date = None
    
    while True:
        api.wait_update()
        bar_count += 1
        
        if bar_count % 1000 == 0:
            account = api.get_account()
            print(f"进度：{bar_count} 根 K 线 | 资金：{account.balance:.2f}")
        
        # 统计天数
        if len(klines_5m) > 0:
            curr_dt = klines_5m.datetime.iloc[-1]
            if isinstance(curr_dt, (int, float)):
                curr_dt = pd.to_datetime(curr_dt, unit='ns')
            curr_date = curr_dt.date()
            
            if curr_date != last_date:
                day_count += 1
                last_date = curr_date
    
except BacktestFinished:
    print("\n" + "=" * 60)
    print("回测完成！")
    print("=" * 60)
    
    stats = sim.tqsdk_stat
    print(f"\n初始资金：  {stats.get('init_balance', 0):,.2f} 元")
    print(f"结束资金：  {stats.get('balance', 0):,.2f} 元")
    print(f"收益率：    {stats.get('ror', 0)*100:.2f}%")
    print(f"最大回撤：  {stats.get('max_drawdown', 0):,.2f} 元")
    print(f"夏普比率：  {stats.get('sharpe_ratio', 0):.2f}")
    print(f"总 K 线数： {bar_count}")
    print(f"交易天数：  {day_count}")
    
    api.close()

except Exception as e:
    print(f"\n错误：{e}")
    import traceback
    traceback.print_exc()
