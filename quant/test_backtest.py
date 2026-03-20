# -*- coding: utf-8 -*-
"""
最简回测测试 - 确保能看到完整结果
"""

from datetime import date
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished

print("=" * 60)
print("TQSDK 回测测试")
print("=" * 60)

# 配置
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"
SYMBOL = "SHFE.rb2405"
START = date(2024, 1, 15)
END = date(2024, 1, 25)

print(f"合约：{SYMBOL}")
print(f"时间：{START} 至 {END}")
print(f"账户：{ACCOUNT}")
print("=" * 60)

try:
    # 初始化
    auth = TqAuth(ACCOUNT, PASSWORD)
    sim = TqSim(1000000)
    
    print("正在连接天勤服务器...")
    api = TqApi(
        account=sim,
        backtest=TqBacktest(start_dt=START, end_dt=END),
        auth=auth
    )
    
    # 获取 K 线
    klines = api.get_kline_serial(SYMBOL, 60)  # 1 分钟线
    
    print(f"已获取 {len(klines)} 根 K 线")
    print(f"第一根：{klines.datetime.iloc[0]}")
    print(f"最后一根：{klines.datetime.iloc[-1]}")
    print("=" * 60)
    
    # 简单回测：持有 1 手多单
    from tqsdk import TargetPosTask
    target_pos = TargetPosTask(api, SYMBOL)
    target_pos.set_target_volume(1)
    print("开多 1 手")
    
    count = 0
    while True:
        api.wait_update()
        count += 1
        
        if count % 500 == 0:
            account = api.get_account()
            print(f"进度：{count} | 资金：{account.balance:.2f}")
    
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
    
    print(f"\n交易日志:")
    print(sim.trade_log)
    
    api.close()
    
except Exception as e:
    print(f"\n错误：{e}")
    import traceback
    traceback.print_exc()
