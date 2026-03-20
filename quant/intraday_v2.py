# -*- coding: utf-8 -*-
"""
日内 5 分钟均线策略 - V2 突破版
================================
开仓逻辑：
- 前 6 根 K 线（30 分钟）标记高低点
- 11:30 前任意 K 线突破前 6 根高低点即开仓
- 日线 EXPMA5/10/20 发散定方向
"""

from datetime import date, datetime, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd

# ============ 配置 ============
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"

SYMBOL = "KQ.m@SHFE.rb"  # 螺纹钢主力

# 测 2024 年全年
START_DATE = date(2024, 1, 1)
END_DATE = date(2024, 12, 31)

# 策略参数
PARAMS = {
    "daily_expma": [5, 10, 20],
    "daily_divergence": 0.01,  # 1% 间距（放宽）
    "intraday_expma": [5, 13],
    "open_window": 6,  # 前 6 根 K 线标记高低点
    "trading_end_hour": 11,
    "trading_end_minute": 30,  # 11:30 前可开仓
    "force_close_hour": 14,
    "force_close_minute": 57,  # 14:57 强平
}
# ===========================


def calc_expma(series, period):
    """计算 EXPMA"""
    result = series.copy()
    alpha = 2.0 / (period + 1)
    for i in range(1, len(result)):
        result.iloc[i] = alpha * result.iloc[i] + (1 - alpha) * result.iloc[i-1]
    return result


def check_direction(daily_klines, params):
    """检查日线方向"""
    if len(daily_klines) < 20:
        return 0, None
    
    close = daily_klines['close'].copy()
    e5 = calc_expma(close, params["daily_expma"][0])
    e10 = calc_expma(close, params["daily_expma"][1])
    e20 = calc_expma(close, params["daily_expma"][2])
    
    latest_e5 = e5.iloc[-1]
    latest_e10 = e10.iloc[-1]
    latest_e20 = e20.iloc[-1]
    
    # 多头
    if latest_e5 > latest_e10 > latest_e20:
        gap1 = (latest_e5 - latest_e10) / latest_e10
        gap2 = (latest_e10 - latest_e20) / latest_e20
        if gap1 > params["daily_divergence"] and gap2 > params["daily_divergence"]:
            return 1, f"多 ({gap1*100:.1f}%/{gap2*100:.1f}%)"
    
    # 空头
    if latest_e5 < latest_e10 < latest_e20:
        gap1 = (latest_e10 - latest_e5) / latest_e10
        gap2 = (latest_e20 - latest_e10) / latest_e20
        if gap1 > params["daily_divergence"] and gap2 > params["daily_divergence"]:
            return -1, f"空 ({gap1*100:.1f}%/{gap2*100:.1f}%)"
    
    return 0, "震荡"


print("=" * 70)
print("日内 5 分钟均线策略 - V2 突破版")
print("=" * 70)
print(f"合约：{SYMBOL}")
print(f"时间：{START_DATE} 至 {END_DATE}")
print(f"参数：日线 EXPMA{PARAMS['daily_expma']}, 间距>{PARAMS['daily_divergence']*100}%")
print(f"      5 分钟 EXPMA{PARAMS['intraday_expma']}, 前{PARAMS['open_window']}根 K 线高低点突破")
print(f"      开仓截止：{PARAMS['trading_end_hour']}:{PARAMS['trading_end_minute']:02d}")
print("=" * 70)

try:
    auth = TqAuth(ACCOUNT, PASSWORD)
    sim = TqSim(1000000)
    
    api = TqApi(
        account=sim,
        backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
        auth=auth
    )
    
    # 获取数据
    daily_klines = api.get_kline_serial(SYMBOL, 86400)
    klines_5m = api.get_kline_serial(SYMBOL, 300)
    
    print(f"\n数据加载完成:")
    print(f"  日线：{len(daily_klines)} 根")
    print(f"  5 分钟：{len(klines_5m)} 根")
    
    # 创建交易工具
    target_pos = TargetPosTask(api, SYMBOL)
    
    # 状态变量
    position = 0  # 0=空仓，1=多，-1=空
    entry_price = 0
    stop_loss = 0
    entry_kline_high = 0
    entry_kline_low = 0
    
    # Session 高低点（前 6 根 K 线）
    session_high = None
    session_low = None
    session_bars = 0
    
    last_date = None
    today_direction = 0
    
    # 统计
    trades = []
    total_bars = 0
    days_traded = 0
    
    print("\n" + "=" * 70)
    print("开始回测...")
    print("=" * 70)
    
    while True:
        api.wait_update()
        total_bars += 1
        
        if api.is_changing(klines_5m):
            # 获取当前 K 线信息
            curr_kline = klines_5m.iloc[-1]
            curr_dt = curr_kline['datetime']
            
            # 转换时间
            if isinstance(curr_dt, (int, float)):
                curr_dt = pd.to_datetime(curr_dt, unit='ns')
            curr_date = curr_dt.date()
            curr_time = curr_dt.time()
            curr_close = curr_kline['close']
            curr_high = curr_kline['high']
            curr_low = curr_kline['low']
            
            # 检查是否新交易日
            if curr_date != last_date:
                # 重置 session
                session_high = None
                session_low = None
                session_bars = 0
                position = 0  # 新交易日强制空仓
                
                # 更新日线方向
                today_direction, direction_str = check_direction(daily_klines, PARAMS)
                
                if today_direction != 0:
                    print(f"\n[{curr_date}] {direction_str} | 资金：{api.get_account().balance:.0f}")
                    days_traded += 1
                
                last_date = curr_date
                continue
            
            # 只在有方向时交易
            if today_direction == 0:
                continue
            
            # 检查强制平仓时间
            if curr_time >= time(PARAMS["force_close_hour"], PARAMS["force_close_minute"]):
                if position != 0:
                    print(f"  [{curr_time}] 强制平仓 @ {curr_close:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'date': curr_date, 'time': curr_time, 'action': 'FORCE_CLOSE', 'price': curr_close})
                    position = 0
                continue
            
            # 检查是否在交易时段（早盘 9:00-11:30，夜盘 21:00-23:00）
            is_morning = time(9, 0) <= curr_time <= time(11, 30)
            is_night = time(21, 0) <= curr_time <= time(23, 30)
            
            if not (is_morning or is_night):
                continue
            
            # 前 6 根 K 线：标记高低点
            if session_bars < PARAMS["open_window"]:
                if session_high is None:
                    session_high = curr_high
                    session_low = curr_low
                else:
                    session_high = max(session_high, curr_high)
                    session_low = min(session_low, curr_low)
                session_bars += 1
                continue
            
            # 6 根之后：检查开仓（只在 11:30 前）
            if position == 0 and curr_time <= time(PARAMS["trading_end_hour"], PARAMS["trading_end_minute"]):
                # 检查突破
                if today_direction == 1:
                    # 多头：突破前 6 根高点做多
                    if curr_close > session_high:
                        stop_loss = curr_low  # 止损设在这根 K 线低点
                        entry_kline_low = curr_low
                        print(f"  [{curr_time}] 开多 @ {curr_close:.0f} (突破{session_high:.0f}), 止损={stop_loss:.0f}")
                        target_pos.set_target_volume(1)
                        entry_price = curr_close
                        position = 1
                        trades.append({
                            'date': curr_date,
                            'time': curr_time,
                            'action': 'BUY',
                            'price': curr_close,
                            'stop_loss': stop_loss,
                            'session_high': session_high,
                            'session_low': session_low
                        })
                
                elif today_direction == -1:
                    # 空头：突破前 6 根低点做空
                    if curr_close < session_low:
                        stop_loss = curr_high  # 止损设在这根 K 线高点
                        entry_kline_high = curr_high
                        print(f"  [{curr_time}] 开空 @ {curr_close:.0f} (突破{session_low:.0f}), 止损={stop_loss:.0f}")
                        target_pos.set_target_volume(-1)
                        entry_price = curr_close
                        position = -1
                        trades.append({
                            'date': curr_date,
                            'time': curr_time,
                            'action': 'SELL',
                            'price': curr_close,
                            'stop_loss': stop_loss,
                            'session_high': session_high,
                            'session_low': session_low
                        })
                
                # 开仓后不再重复开
                if position != 0:
                    continue
            
            # 已有持仓：检查止损/止盈
            if position != 0:
                # 检查止损
                if position == 1 and curr_low <= stop_loss:
                    pnl = (curr_close - entry_price) * 10  # 螺纹钢 10 吨/手
                    print(f"  [{curr_time}] 止损平仓 (多) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'date': curr_date, 'time': curr_time, 'action': 'STOP_LOSS', 'price': curr_close, 'pnl': pnl})
                    position = 0
                    continue
                
                if position == -1 and curr_high >= stop_loss:
                    pnl = (entry_price - curr_close) * 10
                    print(f"  [{curr_time}] 止损平仓 (空) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                    target_pos.set_target_volume(0)
                    trades.append({'date': curr_date, 'time': curr_time, 'action': 'STOP_LOSS', 'price': curr_close, 'pnl': pnl})
                    position = 0
                    continue
                
                # 检查止盈（EXPMA5/13 交叉）
                if len(klines_5m) >= PARAMS["intraday_expma"][1] + 2:
                    close_series = klines_5m['close'].copy()
                    expma5 = calc_expma(close_series, PARAMS["intraday_expma"][0])
                    expma13 = calc_expma(close_series, PARAMS["intraday_expma"][1])
                    
                    curr_e5 = expma5.iloc[-1]
                    curr_e13 = expma13.iloc[-1]
                    prev_e5 = expma5.iloc[-2]
                    prev_e13 = expma13.iloc[-2]
                    
                    # 多单：死叉平仓
                    if position == 1 and prev_e5 >= prev_e13 and curr_e5 < curr_e13:
                        pnl = (curr_close - entry_price) * 10
                        print(f"  [{curr_time}] 止盈平仓 (多，死叉) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                        target_pos.set_target_volume(0)
                        trades.append({'date': curr_date, 'time': curr_time, 'action': 'TAKE_PROFIT', 'price': curr_close, 'pnl': pnl})
                        position = 0
                        continue
                    
                    # 空单：金叉平仓
                    if position == -1 and prev_e5 <= prev_e13 and curr_e5 > curr_e13:
                        pnl = (entry_price - curr_close) * 10
                        print(f"  [{curr_time}] 止盈平仓 (空，金叉) @ {curr_close:.0f}, 盈亏={pnl:.0f}")
                        target_pos.set_target_volume(0)
                        trades.append({'date': curr_date, 'time': curr_time, 'action': 'TAKE_PROFIT', 'price': curr_close, 'pnl': pnl})
                        position = 0
                        continue
    
except BacktestFinished:
    print("\n" + "=" * 70)
    print("回测完成！")
    print("=" * 70)
    
    stats = sim.tqsdk_stat
    init_cap = stats.get('init_balance', 0)
    end_cap = stats.get('balance', 0)
    
    print(f"\n【回测结果】")
    print(f"  初始资金：  {init_cap:>12,.2f} 元")
    print(f"  结束资金：  {end_cap:>12,.2f} 元")
    print(f"  绝对收益：  {end_cap - init_cap:>12,.2f} 元")
    print(f"  收益率：    {(stats.get('ror', 0))*100:>11.2f} %")
    print(f"  最大回撤：  {stats.get('max_drawdown', 0):>12,.2f} 元")
    print(f"  夏普比率：  {stats.get('sharpe_ratio', 0):>11.2f}")
    print(f"  年化收益：  {stats.get('annual_yield', 0)*100:>11.2f} %")
    
    print(f"\n【交易统计】")
    print(f"  回测天数：  {days_traded}")
    print(f"  总交易次数：{len(trades)}")
    
    if trades:
        buy_trades = [t for t in trades if t['action'] == 'BUY']
        sell_trades = [t for t in trades if t['action'] == 'SELL']
        profit_trades = [t for t in trades if t.get('pnl', 0) > 0]
        loss_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        print(f"  开多次数：  {len(buy_trades)}")
        print(f"  开空次数：  {len(sell_trades)}")
        print(f"  盈利次数：  {len(profit_trades)}")
        print(f"  亏损次数：  {len(loss_trades)}")
        
        if len(profit_trades) > 0:
            avg_profit = sum(t['pnl'] for t in profit_trades) / len(profit_trades)
            print(f"  平均盈利：  {avg_profit:>12,.0f} 元")
        
        if len(loss_trades) > 0:
            avg_loss = sum(t['pnl'] for t in loss_trades) / len(loss_trades)
            print(f"  平均亏损：  {avg_loss:>12,.0f} 元")
        
        # 打印交易明细（前 20 笔）
        print(f"\n【交易明细】（前 20 笔）")
        for i, trade in enumerate(trades[:20], 1):
            action = trade['action']
            price = trade['price']
            t = trade['time']
            pnl = trade.get('pnl', 0)
            
            if action == 'BUY':
                print(f"  {i:2}. [{t}] 开多 @ {price:>8.0f}, 止损={trade['stop_loss']:.0f}")
            elif action == 'SELL':
                print(f"  {i:2}. [{t}] 开空 @ {price:>8.0f}, 止损={trade['stop_loss']:.0f}")
            elif action == 'STOP_LOSS':
                print(f"  {i:2}. [{t}] 止损平仓 @ {price:>8.0f}, 盈亏={pnl:>8.0f}")
            elif action == 'TAKE_PROFIT':
                print(f"  {i:2}. [{t}] 止盈平仓 @ {price:>8.0f}, 盈亏={pnl:>8.0f}")
            elif action == 'FORCE_CLOSE':
                print(f"  {i:2}. [{t}] 强制平仓 @ {price:>8.0f}")
        
        if len(trades) > 20:
            print(f"  ... 还有 {len(trades) - 20} 笔交易")
    
    print(f"\n  总 K 线数：  {total_bars}")
    
    api.close()

except Exception as e:
    print(f"\n错误：{e}")
    import traceback
    traceback.print_exc()
