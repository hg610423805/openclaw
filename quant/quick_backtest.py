# -*- coding: utf-8 -*-
"""
快速回测示例
============
5 分钟快速验证策略

用法:
    py quick_backtest.py
"""

from datetime import date
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask

# ============ 配置区 ============
# 快期账户（用于获取行情和数据）
SHINNY_ACCOUNT = "13163715864"
SHINNY_PASSWORD = "Hgssh285755"

# 回测配置
SYMBOL = "SHFE.rb2405"  # 螺纹钢 2405 合约（具体合约，非主力连续）
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 5, 31)  # rb2405 到期前
INITIAL_CAPITAL = 1000000  # 100 万起始资金
KLINE_INTERVAL = 60  # 1 分钟 K 线

# 策略参数
MA_SHORT = 10   # 短期均线
MA_LONG = 30    # 长期均线
POSITION_SIZE = 1  # 每次交易 1 手
# ===========================


def run_simple_strategy():
    """
    简单双均线策略
    =============
    逻辑：
    - 短期均线上穿长期均线 -> 开多
    - 短期均线下穿长期均线 -> 开空
    """
    
    print("[RUN] 启动回测...")
    print(f"  合约：{SYMBOL}")
    print(f"  时间：{START_DATE} 至 {END_DATE}")
    print(f"  周期：{KLINE_INTERVAL}秒 K 线")
    print(f"  资金：{INITIAL_CAPITAL:,}元")
    print("=" * 60)
    
    # 初始化 API
    auth = TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD)
    sim = TqSim(INITIAL_CAPITAL)
    
    api = TqApi(
        account=sim,
        backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
        auth=auth
    )
    
    # 获取 K 线数据
    klines = api.get_kline_serial(SYMBOL, KLINE_INTERVAL)
    target_pos = TargetPosTask(api, SYMBOL)
    
    # 交易记录
    trades = []
    last_signal = 0  # 0=无信号，1=多，-1=空
    
    try:
        while True:
            api.wait_update()
            
            # 检查是否有新 K 线
            if api.is_changing(klines):
                # 确保有足够的数据计算均线
                if len(klines) >= MA_LONG:
                    # 计算均线
                    ma_short = klines.close.rolling(window=MA_SHORT).mean().iloc[-1]
                    ma_long = klines.close.rolling(window=MA_LONG).mean().iloc[-1]
                    prev_ma_short = klines.close.rolling(window=MA_SHORT).mean().iloc[-2]
                    prev_ma_long = klines.close.rolling(window=MA_LONG).mean().iloc[-2]
                    
                    current_price = klines.close.iloc[-1]
                    current_time = klines.datetime.iloc[-1]
                    
                    # 金叉：短均线上穿长均线
                    if prev_ma_short <= prev_ma_long and ma_short > ma_long:
                        signal = 1
                        if last_signal != 1:
                            print(f"[BUY] [{current_time}] 金叉！价格={current_price:.2f}, MA{MA_SHORT}={ma_short:.2f}, MA{MA_LONG}={ma_long:.2f}")
                            target_pos.set_target_volume(POSITION_SIZE)
                            trades.append({
                                'time': current_time,
                                'action': 'BUY',
                                'price': current_price,
                                'volume': POSITION_SIZE
                            })
                            last_signal = 1
                    
                    # 死叉：短均线下穿长均线
                    elif prev_ma_short >= prev_ma_long and ma_short < ma_long:
                        signal = -1
                        if last_signal != -1:
                            print(f"[SELL] [{current_time}] 死叉！价格={current_price:.2f}, MA{MA_SHORT}={ma_short:.2f}, MA{MA_LONG}={ma_long:.2f}")
                            target_pos.set_target_volume(-POSITION_SIZE)
                            trades.append({
                                'time': current_time,
                                'action': 'SELL',
                                'price': current_price,
                                'volume': POSITION_SIZE
                            })
                            last_signal = -1
                    
                    # 打印当前状态（每 100 根 K 线打印一次）
                    if len(klines) % 100 == 0:
                        account = api.get_account()
                        print(f"[STATUS] K 线#{len(klines)} | 资金={account.balance:.2f} | 均线差={ma_short - ma_long:.2f}")
        
    except BacktestFinished:
        print("\n" + "=" * 60)
        print("[DONE] 回测完成！")
        
        # 获取回测统计
        stats = sim.tqsdk_stat
        print(f"\n[RESULT] 回测结果:")
        print(f"  初始资金：  {stats.get('init_balance', 0):>12.2f} 元")
        print(f"  结束资金：  {stats.get('balance', 0):>12.2f} 元")
        print(f"  收益率：    {stats.get('ror', 0)*100:>11.2f} %")
        print(f"  年化收益：  {stats.get('annual_yield', 0)*100:>11.2f} %")
        print(f"  最大回撤：  {stats.get('max_drawdown', 0):>12.2f} 元")
        print(f"  夏普比率：  {stats.get('sharpe_ratio', 0):>11.2f}")
        print(f"  胜率：      {stats.get('winning_rate', 0)*100:>11.2f} %")
        print(f"  盈亏比：    {stats.get('profit_loss_ratio', 0):>11.2f}")
        
        # 天勤点评
        if 'tqsdk_punchline' in stats:
            print(f"\n[NOTE] 天勤点评：{stats['tqsdk_punchline']}")
        
        # 交易记录
        print(f"\n[TRADES] 交易记录 ({len(trades)}笔):")
        if trades:
            for i, trade in enumerate(trades, 1):
                print(f"  {i}. [{trade['time']}] {trade['action']} {trade['volume']}手 @ {trade['price']:.2f}")
        else:
            print("  (无交易)")
        
        # 打印详细交易日志
        print(f"\n[LOG] 详细交易日志:")
        print(sim.trade_log)
        
        api.close()
        
        return stats


if __name__ == "__main__":
    # 检查配置
    if SHINNY_ACCOUNT == "你的快期账户":
        print("[ERROR] 错误：请先配置快期账户！")
        print(f"\n请编辑此文件，修改以下配置:")
        print(f"  SHINNY_ACCOUNT = \"你的快期账户\"")
        print(f"  SHINNY_PASSWORD = \"你的快期账户密码\"")
        print(f"\n注册快期账户：https://account.shinnytech.com/")
    else:
        run_simple_strategy()
