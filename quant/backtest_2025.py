# -*- coding: utf-8 -*-
"""
日内 5 分钟均线策略 - 2025 年全年回测
"""

from datetime import date, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd

# ===== 配置 =====
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"
SYMBOL = "KQ.m@SHFE.rb"  # 螺纹钢主力
START = date(2025, 1, 1)
END = date(2025, 12, 31)

def calc_expma(series, period):
    result = series.copy()
    alpha = 2.0 / (period + 1)
    for i in range(1, len(result)):
        result.iloc[i] = alpha * result.iloc[i] + (1 - alpha) * result.iloc[i-1]
    return result

print("="*70)
print("日内 5 分钟均线策略 - 2025 年全年回测")
print("="*70)
print(f"合约：{SYMBOL}")
print(f"时间：{START} 至 {END}")
print("="*70)

try:
    auth = TqAuth(ACCOUNT, PASSWORD)
    sim = TqSim(1000000)
    api = TqApi(account=sim, backtest=TqBacktest(start_dt=START, end_dt=END), auth=auth)
    
    daily = api.get_kline_serial(SYMBOL, 86400)
    k5m = api.get_kline_serial(SYMBOL, 300)
    target_pos = TargetPosTask(api, SYMBOL)
    
    print(f"\n数据加载:")
    print(f"  日线：{len(daily)} 根")
    print(f"  5 分钟：{len(k5m)} 根")
    
    # 状态
    pos = 0
    entry_price = 0
    stop_loss = 0
    session_high = None
    session_low = None
    session_bars = 0
    last_date = None
    direction = 0
    
    trades = []
    total_bars = 0
    
    print("\n开始回测...")
    
    while True:
        api.wait_update()
        total_bars += 1
        
        if api.is_changing(k5m):
            curr = k5m.iloc[-1]
            curr_dt = pd.to_datetime(curr['datetime'], unit='ns') if isinstance(curr['datetime'], (int,float)) else curr['datetime']
            curr_date = curr_dt.date()
            curr_time = curr_dt.time()
            curr_close = curr['close']
            curr_high = curr['high']
            curr_low = curr['low']
            
            # 新交易日
            if curr_date != last_date:
                session_high = session_low = None
                session_bars = 0
                pos = 0
                last_date = curr_date
                
                # 计算日线方向
                if len(daily) >= 20:
                    close = daily['close'].copy()
                    e5 = calc_expma(close, 5).iloc[-1]
                    e10 = calc_expma(close, 10).iloc[-1]
                    e20 = calc_expma(close, 20).iloc[-1]
                    
                    if e5 > e10 > e20 and (e5-e10)/e10 > 0.01 and (e10-e20)/e20 > 0.01:
                        direction = 1
                        print(f"\n[{curr_date}] 多头 (5>{e5:.0f} 10>{e10:.0f} 20>{e20:.0f})")
                    elif e5 < e10 < e20 and (e10-e5)/e10 > 0.01 and (e20-e10)/e20 > 0.01:
                        direction = -1
                        print(f"\n[{curr_date}] 空头 (5<{e5:.0f} 10<{e10:.0f} 20<{e20:.0f})")
                    else:
                        direction = 0
                continue
            
            if direction == 0:
                continue
            
            # 强平
            if curr_time >= time(14, 57):
                if pos != 0:
                    pnl = (curr_close - entry_price) * 10 if pos == 1 else (entry_price - curr_close) * 10
                    print(f"  [{curr_time}] 强平 @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'date':curr_date, 'action':'FORCE_CLOSE', 'price':curr_close, 'pnl':pnl})
                    pos = 0
                continue
            
            # 交易时段
            if not (time(9,0) <= curr_time <= time(11,30) or time(21,0) <= curr_time <= time(23,30)):
                continue
            
            # 前 6 根标记高低点
            if session_bars < 6:
                session_high = curr_high if session_high is None else max(session_high, curr_high)
                session_low = curr_low if session_low is None else min(session_low, curr_low)
                session_bars += 1
                continue
            
            # 开仓
            if pos == 0 and curr_time <= time(11, 30):
                if direction == 1 and curr_close > session_high:
                    stop_loss = curr_low
                    print(f"  [{curr_time}] 开多 @ {curr_close:.0f}, 止损={stop_loss:.0f}")
                    target_pos.set_target_volume(1)
                    entry_price = curr_close
                    pos = 1
                    trades.append({'date':curr_date, 'action':'BUY', 'price':curr_close, 'stop_loss':stop_loss})
                elif direction == -1 and curr_close < session_low:
                    stop_loss = curr_high
                    print(f"  [{curr_time}] 开空 @ {curr_close:.0f}, 止损={stop_loss:.0f}")
                    target_pos.set_target_volume(-1)
                    entry_price = curr_close
                    pos = -1
                    trades.append({'date':curr_date, 'action':'SELL', 'price':curr_close, 'stop_loss':stop_loss})
                continue
            
            # 止损/止盈
            if pos != 0:
                # 止损
                if (pos == 1 and curr_low <= stop_loss) or (pos == -1 and curr_high >= stop_loss):
                    pnl = (curr_close - entry_price) * 10 if pos == 1 else (entry_price - curr_close) * 10
                    print(f"  [{curr_time}] 止损 @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'date':curr_date, 'action':'STOP_LOSS', 'price':curr_close, 'pnl':pnl})
                    pos = 0
                    continue
                
                # 止盈
                if len(k5m) >= 15:
                    close = k5m['close'].copy()
                    e5 = calc_expma(close, 5)
                    e13 = calc_expma(close, 13)
                    
                    if pos == 1 and e5.iloc[-2] >= e13.iloc[-2] and e5.iloc[-1] < e13.iloc[-1]:
                        pnl = (curr_close - entry_price) * 10
                        print(f"  [{curr_time}] 止盈 (死叉) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                        target_pos.set_target_volume(0)
                        trades.append({'date':curr_date, 'action':'TAKE_PROFIT', 'price':curr_close, 'pnl':pnl})
                        pos = 0
                        continue
                    
                    if pos == -1 and e5.iloc[-2] <= e13.iloc[-2] and e5.iloc[-1] > e13.iloc[-1]:
                        pnl = (entry_price - curr_close) * 10
                        print(f"  [{curr_time}] 止盈 (金叉) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                        target_pos.set_target_volume(0)
                        trades.append({'date':curr_date, 'action':'TAKE_PROFIT', 'price':curr_close, 'pnl':pnl})
                        pos = 0
                        continue
        
        if total_bars % 10000 == 0:
            print(f"进度：{total_bars} 根 K 线 | 资金:{api.get_account().balance:.0f}")

except BacktestFinished:
    print("\n" + "="*70)
    print("回测完成！")
    print("="*70)
    
    stats = sim.tqsdk_stat
    init_cap = stats.get('init_balance', 0)
    end_cap = stats.get('balance', 0)
    
    print(f"\n【回测结果】")
    print(f"  初始资金：  {init_cap:>12,.2f} 元")
    print(f"  结束资金：  {end_cap:>12,.2f} 元")
    print(f"  绝对收益：  {end_cap - init_cap:>12,.2f} 元")
    print(f"  收益率：    {stats.get('ror', 0)*100:>11.2f} %")
    print(f"  最大回撤：  {stats.get('max_drawdown', 0):>12,.2f} 元")
    print(f"  夏普比率：  {stats.get('sharpe_ratio', 0):>11.2f}")
    print(f"  年化收益：  {stats.get('annual_yield', 0)*100:>11.2f} %")
    
    print(f"\n【交易统计】")
    print(f"  总 K 线数：  {total_bars:,}")
    print(f"  总交易笔数：{len(trades)}")
    
    if trades:
        buys = len([t for t in trades if t['action']=='BUY'])
        sells = len([t for t in trades if t['action']=='SELL'])
        profits = [t for t in trades if t.get('pnl',0) > 0]
        losses = [t for t in trades if t.get('pnl',0) < 0]
        forces = len([t for t in trades if t['action']=='FORCE_CLOSE'])
        
        print(f"  开多次数：  {buys}")
        print(f"  开空次数：  {sells}")
        print(f"  盈利次数：  {len(profits)}")
        print(f"  亏损次数：  {len(losses)}")
        print(f"  强平次数：  {forces}")
        
        if len(profits) > 0:
            avg_profit = sum(t['pnl'] for t in profits) / len(profits)
            print(f"  平均盈利：  {avg_profit:>12,.0f} 元")
        
        if len(losses) > 0:
            avg_loss = sum(t['pnl'] for t in losses) / len(losses)
            print(f"  平均亏损：  {avg_loss:>12,.0f} 元")
        
        # 胜率
        if len(profits) + len(losses) > 0:
            win_rate = len(profits) / (len(profits) + len(losses)) * 100
            print(f"  胜率：      {win_rate:>11.1f} %")
        
        # 打印前 20 笔交易
        print(f"\n【交易明细】（前 20 笔）")
        for i, t in enumerate(trades[:20], 1):
            d = t['date']
            action = t['action']
            price = t['price']
            pnl = t.get('pnl', 0)
            
            if action in ['BUY', 'SELL']:
                sl = t.get('stop_loss', 0)
                print(f"  {i:2}. [{d}] {action} @ {price:>8.0f}, 止损={sl:.0f}")
            else:
                print(f"  {i:2}. [{d}] {action} @ {price:>8.0f}, 盈亏={pnl:>8.0f}")
        
        if len(trades) > 20:
            print(f"  ... 还有 {len(trades) - 20} 笔交易")
    
    api.close()

except Exception as e:
    print(f"\n错误：{e}")
    import traceback
    traceback.print_exc()
