# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 单品种回测
用法：python backtest_one.py rb 2025-01-01 2025-03-22
"""

from tqsdk import TqApi, TqAuth, TqBacktest
from tqsdk.ta import EMA, KDJ
from datetime import date
import sys
import json
import os

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symbols_config import SYMBOL_CONFIG

# 导入账号
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD

def get_symbol(code):
    """获取合约代码"""
    code = code.lower()
    for k, v in SYMBOL_CONFIG.items():
        if k == code:
            return f"{v['exchange']}.{code}2505"
    raise ValueError(f"未知品种：{code}")

def backtest(symbol_code, start, end):
    """回测单个品种"""
    symbol = get_symbol(symbol_code)
    info = SYMBOL_CONFIG.get(symbol_code, {"tick": 1, "multiplier": 10, "commission_rate": 0.0001, "name": ""})
    
    print(f"\n{'='*60}")
    print(f"回测：{symbol} ({info['name']})")
    print(f"区间：{start} ~ {end}")
    print(f"{'='*60}")
    
    # API
    api = TqApi(
        auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
        backtest=TqBacktest(start_dt=date(2025,1,1), end_dt=date(2025,3,22))
    )
    
    # K 线
    k30 = api.get_kline_serial(symbol, 1800)
    k5 = api.get_kline_serial(symbol, 300)
    
    if len(k5) < 100:
        print("  数据不足")
        api.close()
        return None
    
    # 指标
    e13_30 = EMA(k30['close'], 13)
    e26_30 = EMA(k30['close'], 26)
    kdj_30 = KDJ(k30, 9)
    
    e13_5 = EMA(k5['close'], 13)
    e26_5 = EMA(k5['close'], 26)
    kdj_5 = KDJ(k5, 9)
    
    tick = info["tick"]
    mult = info["multiplier"]
    comm = info["commission_rate"]
    capital = 100000
    
    trades = []
    pos = 0
    entry = 0
    sl = 0
    daily = 0
    last_d = None
    cur_trade = None
    
    print(f"K 线：{len(k5)}条 | 开始...")
    
    for i in range(100, len(k5)):
        cur_d = str(k5.iloc[i]['datetime'])[:10]
        if cur_d != last_d:
            daily = 0
            last_d = cur_d
        
        p = k5.iloc[i]['close']
        t = str(k5.iloc[i]['datetime'])
        
        # 持仓
        if pos != 0:
            # 止损
            if (pos > 0 and p <= sl) or (pos < 0 and p >= sl):
                reason = "止损"
                if pos > 0: pnl = (p - entry) * pos * mult
                else: pnl = (entry - p) * abs(pos) * mult
                fee = (entry + p) * abs(pos) * mult * comm
                slip = tick * abs(pos) * mult * 2
                net = pnl - fee - slip
                trades.append({"entry_t": cur_trade["entry_t"], "entry_p": cur_trade["entry_p"],
                              "dir": cur_trade["dir"], "hands": cur_trade["hands"],
                              "exit_t": t, "exit_p": p, "reason": reason, "pnl": net,
                              "entry_reason": cur_trade["entry_reason"]})
                print(f"  [平仓] {t[:16]} @ {p} | {net:.0f} | {reason}")
                pos = 0
                continue
            
            # 止盈
            if i >= 2:
                pd = e13_5.iloc[i-1] - e26_5.iloc[i-1]
                cd = e13_5.iloc[i] - e26_5.iloc[i]
                if (pos > 0 and pd > 0 and cd <= 0) or (pos < 0 and pd < 0 and cd >= 0):
                    reason = "止盈"
                    if pos > 0: pnl = (p - entry) * pos * mult
                    else: pnl = (entry - p) * abs(pos) * mult
                    fee = (entry + p) * abs(pos) * mult * comm
                    slip = tick * abs(pos) * mult * 2
                    net = pnl - fee - slip
                    trades.append({"entry_t": cur_trade["entry_t"], "entry_p": cur_trade["entry_p"],
                                  "dir": cur_trade["dir"], "hands": cur_trade["hands"],
                                  "exit_t": t, "exit_p": p, "reason": reason, "pnl": net,
                                  "entry_reason": cur_trade["entry_reason"]})
                    print(f"  [平仓] {t[:16]} @ {p} | {net:.0f} | {reason}")
                    pos = 0
                    continue
        
        # 开仓
        elif daily < 3:
            j30 = kdj_30['j'].iloc[i] if i < len(kdj_30) else 50
            bull = e13_30.iloc[i] > e26_30.iloc[i]
            bear = e13_30.iloc[i] < e26_30.iloc[i]
            
            # 多
            if bull and j30 < 20:
                r = None
                if e13_5.iloc[i] > e26_5.iloc[i] and kdj_5['j'].iloc[i] < 20 and i >= 1 and k5.iloc[i]['low'] > k5.iloc[i-1]['low']:
                    r = "方式 1"
                elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) <= 0 and (e13_5.iloc[i] - e26_5.iloc[i]) > 0:
                    r = "方式 2"
                
                if r:
                    hands = int(capital * 0.5 / (p * mult))
                    if hands > 0:
                        pos = hands
                        entry = p
                        sl = k5.iloc[i-1]['low'] - tick if r == "方式 1" else p * 0.98
                        cur_trade = {"entry_t": t, "entry_p": p, "dir": "LONG", "hands": hands, "entry_reason": r}
                        daily += 1
                        print(f"  [开多] {t[:16]} @ {p} | {hands}手 | {r}")
            
            # 空
            elif bear and j30 > 80:
                r = None
                if e13_5.iloc[i] < e26_5.iloc[i] and kdj_5['j'].iloc[i] > 80 and i >= 1 and k5.iloc[i]['high'] < k5.iloc[i-1]['high']:
                    r = "方式 1"
                elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) >= 0 and (e13_5.iloc[i] - e26_5.iloc[i]) < 0:
                    r = "方式 2"
                
                if r:
                    hands = int(capital * 0.5 / (p * mult))
                    if hands > 0:
                        pos = -hands
                        entry = p
                        sl = k5.iloc[i-1]['high'] + tick if r == "方式 1" else p * 1.02
                        cur_trade = {"entry_t": t, "entry_p": p, "dir": "SHORT", "hands": hands, "entry_reason": r}
                        daily += 1
                        print(f"  [开空] {t[:16]} @ {p} | {hands}手 | {r}")
    
    api.close()
    
    # 统计
    if not trades:
        print("  无交易")
        return {"symbol": symbol, "name": info['name'], "trades": 0}
    
    total = sum(t["pnl"] for t in trades)
    wins = [t for t in trades if t["pnl"] > 0]
    loss = [t for t in trades if t["pnl"] <= 0]
    
    return {
        "symbol": symbol,
        "name": info['name'],
        "period": f"{start} ~ {end}",
        "trades": len(trades),
        "total_pnl": round(total, 2),
        "win_rate": round(len(wins)/len(trades)*100, 2),
        "avg_win": round(sum(t["pnl"] for t in wins)/len(wins), 2) if wins else 0,
        "avg_loss": round(sum(t["pnl"] for t in loss)/len(loss), 2) if loss else 0,
        "trades_detail": trades
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python backtest_one.py <品种> [开始日期] [结束日期]")
        print("例：python backtest_one.py rb 2025-01-01 2025-03-22")
        sys.exit(1)
    
    code = sys.argv[1]
    start = sys.argv[2] if len(sys.argv) > 2 else "2025-01-01"
    end = sys.argv[3] if len(sys.argv) > 3 else "2025-03-22"
    
    result = backtest(code, start, end)
    
    if result:
        os.makedirs("backtest_results", exist_ok=True)
        fn = f"backtest_results/{code}_result.json"
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n已保存：{fn}")
        print(f"\n结果：{result['trades']}笔 | 总盈亏：{result.get('total_pnl', 0)} | 胜率：{result.get('win_rate', 0)}%")
