# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 单品种回测
EXPMA: (df, p1, p2) -> ['ma1']
KDJ: (df, n, m1, m2) -> ['j']
"""

from datetime import date
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished
from tqsdk.ta import EXPMA, KDJ
import sys, os, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symbols_config import SYMBOL_CONFIG
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

def backtest_one(code, start="2025-01-01", end="2025-03-22"):
    info = SYMBOL_CONFIG.get(code, {"name": code, "tick": 1, "multiplier": 10, "commission_rate": 0.0001})
    exchange = info.get("exchange", "SHFE")
    symbol = f"KQ.m@{exchange}.{code}"
    
    print(f"\n回测：{symbol} ({info['name']}) | {start} ~ {end}")
    
    sim = TqSim(100000)
    try:
        api = TqApi(sim, backtest=TqBacktest(date(2025,1,1), date(2025,3,22)), auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD))
        
        k30 = api.get_kline_serial(symbol, 1800)
        k5 = api.get_kline_serial(symbol, 300)
        
        if len(k5) < 100:
            raise BacktestFinished()
        
        # 指标
        e13_30 = EXPMA(k30, 13, 13)['ma1']
        e26_30 = EXPMA(k30, 26, 26)['ma1']
        kdj_30 = KDJ(k30, 9, 3, 3)['j']
        e13_5 = EXPMA(k5, 13, 13)['ma1']
        e26_5 = EXPMA(k5, 26, 26)['ma1']
        kdj_5 = KDJ(k5, 9, 3, 3)['j']
        
        tick, mult, comm = info["tick"], info["multiplier"], info["commission_rate"]
        pos, entry, sl, daily, last_d, cur_t, trades = 0, 0, 0, 0, None, None, []
        
        while True:
            api.wait_update()
            if len(k5) < 100: continue
            i = len(k5) - 1
            p, t = k5.iloc[i]['close'], str(k5.iloc[i]['datetime'])
            d = t[:10]
            
            if d != last_d: daily, last_d = 0, d
            
            if pos != 0:
                # 止损
                if (pos > 0 and p <= sl) or (pos < 0 and p >= sl):
                    pnl = (p - entry) * pos * mult if pos > 0 else (entry - p) * abs(pos) * mult
                    fee = (entry + p) * abs(pos) * mult * comm
                    slip = tick * abs(pos) * mult * 2
                    trades.append({"entry_t": cur_t["entry_t"], "entry_p": cur_t["entry_p"], "dir": cur_t["dir"], "hands": cur_t["hands"], "exit_t": t, "exit_p": p, "exit_reason": "止损", "entry_reason": cur_t["entry_reason"], "pnl": round(pnl - fee - slip, 2), "fee": round(fee, 2), "slip": round(slip, 2)})
                    print(f"  [平仓] {t[:16]} @ {p:.1f} | {pnl - fee - slip:.0f} | 止损")
                    pos = 0
                    continue
                
                # 止盈
                if i >= 2:
                    pd = e13_5.iloc[i-1] - e26_5.iloc[i-1]
                    cd = e13_5.iloc[i] - e26_5.iloc[i]
                    if (pos > 0 and pd > 0 and cd <= 0) or (pos < 0 and pd < 0 and cd >= 0):
                        pnl = (p - entry) * pos * mult if pos > 0 else (entry - p) * abs(pos) * mult
                        fee = (entry + p) * abs(pos) * mult * comm
                        slip = tick * abs(pos) * mult * 2
                        trades.append({"entry_t": cur_t["entry_t"], "entry_p": cur_t["entry_p"], "dir": cur_t["dir"], "hands": cur_t["hands"], "exit_t": t, "exit_p": p, "exit_reason": "止盈", "entry_reason": cur_t["entry_reason"], "pnl": round(pnl - fee - slip, 2), "fee": round(fee, 2), "slip": round(slip, 2)})
                        print(f"  [平仓] {t[:16]} @ {p:.1f} | {pnl - fee - slip:.0f} | 止盈")
                        pos = 0
                        continue
            
            elif daily < 3:
                j30 = kdj_30.iloc[i] if i < len(kdj_30) else 50
                bull, bear = e13_30.iloc[i] > e26_30.iloc[i], e13_30.iloc[i] < e26_30.iloc[i]
                
                # 多
                if bull and j30 < 30:
                    r = None
                    if e13_5.iloc[i] > e26_5.iloc[i] and kdj_5.iloc[i] < 30 and i >= 1 and k5.iloc[i]['low'] > k5.iloc[i-1]['low']:
                        r = "方式 1"
                    elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) <= 0 and (e13_5.iloc[i] - e26_5.iloc[i]) > 0:
                        r = "方式 2"
                    if r:
                        hands = int(50000 / (p * mult))
                        if hands > 0:
                            pos, entry = hands, p
                            sl = k5.iloc[i-1]['low'] - tick if r == "方式 1" else p * 0.98
                            cur_t = {"entry_t": t, "entry_p": p, "dir": "LONG", "hands": hands, "entry_reason": r}
                            daily += 1
                            print(f"  [开多] {t[:16]} @ {p:.1f} | {hands}手 | {r}")
                
                # 空
                elif bear and j30 > 70:
                    r = None
                    if e13_5.iloc[i] < e26_5.iloc[i] and kdj_5.iloc[i] > 70 and i >= 1 and k5.iloc[i]['high'] < k5.iloc[i-1]['high']:
                        r = "方式 1"
                    elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) >= 0 and (e13_5.iloc[i] - e26_5.iloc[i]) < 0:
                        r = "方式 2"
                    if r:
                        hands = int(50000 / (p * mult))
                        if hands > 0:
                            pos, entry = -hands, p
                            sl = k5.iloc[i-1]['high'] + tick if r == "方式 1" else p * 1.02
                            cur_t = {"entry_t": t, "entry_p": p, "dir": "SHORT", "hands": hands, "entry_reason": r}
                            daily += 1
                            print(f"  [开空] {t[:16]} @ {p:.1f} | {hands}手 | {r}")
    except BacktestFinished:
        api.close()
    
    if not trades:
        return {"symbol": symbol, "name": info['name'], "period": f"{start} ~ {end}", "total_trades": 0, "trades": []}
    
    total = sum(t["pnl"] for t in trades)
    wins = [t for t in trades if t["pnl"] > 0]
    return {
        "symbol": symbol, "name": info['name'], "period": f"{start} ~ {end}",
        "total_trades": len(trades), "total_pnl": round(total, 2),
        "win_rate": round(len(wins)/len(trades)*100, 2),
        "total_fee": round(sum(t["fee"] for t in trades), 2),
        "trades": trades
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backtest_official.py <code> [start] [end]")
        sys.exit(1)
    
    code, start, end = sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "2025-01-01", sys.argv[3] if len(sys.argv) > 3 else "2025-03-22"
    result = backtest_one(code, start, end)
    
    os.makedirs("backtest_results", exist_ok=True)
    with open(f"backtest_results/{code}_result.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved: backtest_results/{code}_result.json")
    print(f"Trades: {result.get('total_trades', 0)} | PnL: {result.get('total_pnl', 0)} | Win: {result.get('win_rate', 0)}%")
