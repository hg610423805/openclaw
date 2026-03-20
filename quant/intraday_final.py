# -*- coding: utf-8 -*-
"""
日内 5 分钟均线策略 - 最终版
===========================
开仓：前 6 根 K 线高低点突破
止损：开仓 K 线高低点
止盈：5 分钟 EXPMA5/13 交叉
强平：14:57
"""

from datetime import date, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd

# ===== 配置 =====
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"
SYMBOL = "KQ.m@SHFE.rb"
START = date(2024, 1, 1)
END = date(2024, 12, 31)

def calc_expma(series, period):
    result = series.copy()
    alpha = 2.0 / (period + 1)
    for i in range(1, len(result)):
        result.iloc[i] = alpha * result.iloc[i] + (1 - alpha) * result.iloc[i-1]
    return result

print("="*70)
print("日内 5 分钟均线策略 - 最终版")
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
    
    print(f"日线:{len(daily)} 5 分钟:{len(k5m)}")
    
    # 状态
    pos = 0  # 0/1/-1
    entry_price = 0
    stop_loss = 0
    session_high = None
    session_low = None
    session_bars = 0
    last_date = None
    direction = 0  # 1/-1/0
    
    trades = []
    
    while True:
        api.wait_update()
        
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
                        print(f"[{curr_date}] 多头 | 资金:{api.get_account().balance:.0f}")
                    elif e5 < e10 < e20 and (e10-e5)/e10 > 0.01 and (e20-e10)/e20 > 0.01:
                        direction = -1
                        print(f"[{curr_date}] 空头 | 资金:{api.get_account().balance:.0f}")
                    else:
                        direction = 0
                        print(f"[{curr_date}] 震荡")
                continue
            
            if direction == 0:
                continue
            
            # 强平
            if curr_time >= time(14, 57):
                if pos != 0:
                    print(f"  [{curr_time}] 强平 @ {curr_close:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'action': 'FORCE_CLOSE', 'price': curr_close})
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
                    trades.append({'action': 'BUY', 'price': curr_close, 'stop_loss': stop_loss})
                elif direction == -1 and curr_close < session_low:
                    stop_loss = curr_high
                    print(f"  [{curr_time}] 开空 @ {curr_close:.0f}, 止损={stop_loss:.0f}")
                    target_pos.set_target_volume(-1)
                    entry_price = curr_close
                    pos = -1
                    trades.append({'action': 'SELL', 'price': curr_close, 'stop_loss': stop_loss})
                continue
            
            # 止损/止盈
            if pos != 0:
                # 止损
                if (pos == 1 and curr_low <= stop_loss) or (pos == -1 and curr_high >= stop_loss):
                    action = 'STOP_LOSS_LONG' if pos == 1 else 'STOP_LOSS_SHORT'
                    pnl = (curr_close - entry_price) * 10 if pos == 1 else (entry_price - curr_close) * 10
                    print(f"  [{curr_time}] 止损 @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'action': action, 'price': curr_close, 'pnl': pnl})
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
                        trades.append({'action': 'TAKE_PROFIT_LONG', 'price': curr_close, 'pnl': pnl})
                        pos = 0
                        continue
                    
                    if pos == -1 and e5.iloc[-2] <= e13.iloc[-2] and e5.iloc[-1] > e13.iloc[-1]:
                        pnl = (entry_price - curr_close) * 10
                        print(f"  [{curr_time}] 止盈 (金叉) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                        target_pos.set_target_volume(0)
                        trades.append({'action': 'TAKE_PROFIT_SHORT', 'price': curr_close, 'pnl': pnl})
                        pos = 0
                        continue

except BacktestFinished:
    print("\n" + "="*70)
    stats = sim.tqsdk_stat
    print(f"初始:{stats.get('init_balance',0):,.0f}")
    print(f"结束:{stats.get('balance',0):,.0f}")
    print(f"收益:{stats.get('ror',0)*100:.2f}%")
    print(f"回撤:{stats.get('max_drawdown',0):,.0f}")
    print(f"夏普:{stats.get('sharpe_ratio',0):.2f}")
    print(f"交易:{len(trades)}笔")
    
    # 分类统计
    buys = len([t for t in trades if t['action']=='BUY'])
    sells = len([t for t in trades if t['action']=='SELL'])
    profits = [t for t in trades if t.get('pnl',0) > 0]
    losses = [t for t in trades if t.get('pnl',0) < 0]
    
    print(f"开多:{buys} 开空:{sells}")
    print(f"盈利:{len(profits)} 亏损:{len(losses)}")
    
    if profits:
        print(f"均盈:{sum(t['pnl'] for t in profits)/len(profits):.0f}")
    if losses:
        print(f"均亏:{sum(t['pnl'] for t in losses)/len(losses):.0f}")
    
    # 明细
    if trades:
        print(f"\n前 20 笔交易:")
        for i, t in enumerate(trades[:20], 1):
            if t['action'] in ['BUY','SELL']:
                print(f"  {i}. {t['action']} @ {t['price']:.0f}, 止损={t['stop_loss']:.0f}")
            else:
                print(f"  {i}. {t['action']} @ {t['price']:.0f}, 盈亏={t.get('pnl',0):.0f}")
    
    api.close()

except Exception as e:
    print(f"错误:{e}")
    import traceback
    traceback.print_exc()
