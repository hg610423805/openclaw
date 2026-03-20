# -*- coding: utf-8 -*-
"""
日内策略 - 快速调试版
直接测 2024 年 1 月，看是否有交易信号
"""

from datetime import date, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd

ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"
SYMBOL = "KQ.m@SHFE.rb"

print("=" * 60)
print("日内策略 - 快速调试")
print("=" * 60)

try:
    auth = TqAuth(ACCOUNT, PASSWORD)
    sim = TqSim(1000000)
    
    # 只测 10 天
    api = TqApi(
        account=sim,
        backtest=TqBacktest(start_dt=date(2024, 1, 1), end_dt=date(2024, 1, 15)),
        auth=auth
    )
    
    daily = api.get_kline_serial(SYMBOL, 86400)
    k5m = api.get_kline_serial(SYMBOL, 300)
    
    print(f"日线：{len(daily)} 根")
    print(f"5 分钟：{len(k5m)} 根")
    
    # 打印前几天看看
    print("\n日线前 5 根:")
    for i in range(min(5, len(daily))):
        dt = daily.datetime.iloc[i]
        if isinstance(dt, (int, float)):
            dt = pd.to_datetime(dt, unit='ns').date()
        print(f"  {dt}: C={daily.close.iloc[i]:.0f}")
    
    print("\n5 分钟前 10 根:")
    for i in range(min(10, len(k5m))):
        dt = k5m.datetime.iloc[i]
        if isinstance(dt, (int, float)):
            dt = pd.to_datetime(dt, unit='ns')
        print(f"  {dt}: O={k5m.open.iloc[i]:.0f} H={k5m.high.iloc[i]:.0f} L={k5m.low.iloc[i]:.0f} C={k5m.close.iloc[i]:.0f}")
    
    # 简单测试：只要有数据就开仓
    print("\n开始测试...")
    target_pos = TargetPosTask(api, SYMBOL)
    
    position = 0
    bar_count = 0
    trade_count = 0
    last_date = None
    
    while True:
        api.wait_update()
        bar_count += 1
        
        if api.is_changing(k5m):
            curr = k5m.iloc[-1]
            curr_dt = curr['datetime']
            if isinstance(curr_dt, (int, float)):
                curr_dt = pd.to_datetime(curr_dt, unit='ns')
            curr_date = curr_dt.date()
            curr_time = curr_dt.time()
            
            # 新交易日
            if curr_date != last_date:
                position = 0
                last_date = curr_date
                print(f"\n[{curr_date}] 资金={api.get_account().balance:.0f}")
            
            # 简单开仓逻辑：每天早上 9:30 开 1 手多
            if position == 0 and time(9, 30) <= curr_time <= time(9, 35):
                print(f"  [{curr_time}] 开多 @ {curr.close:.0f}")
                target_pos.set_target_volume(1)
                position = 1
                trade_count += 1
            
            # 14:57 平仓
            if position != 0 and time(14, 57) <= curr_time <= time(15, 0):
                print(f"  [{curr_time}] 平仓 @ {curr.close:.0f}")
                target_pos.set_target_volume(0)
                position = 0
        
        if bar_count % 5000 == 0:
            print(f"进度：{bar_count} 根")
    
except BacktestFinished:
    print("\n" + "=" * 60)
    print("回测完成！")
    stats = sim.tqsdk_stat
    print(f"初始：{stats.get('init_balance', 0):,.0f}")
    print(f"结束：{stats.get('balance', 0):,.0f}")
    print(f"收益：{stats.get('ror', 0)*100:.2f}%")
    print(f"交易：{trade_count} 笔")
    print(f"K 线：{bar_count} 根")
    api.close()

except Exception as e:
    print(f"错误：{e}")
    import traceback
    traceback.print_exc()
