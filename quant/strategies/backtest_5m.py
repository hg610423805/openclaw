# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 单品种回测（官方示例风格）
"""

from datetime import date
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished
from tqsdk.ta import EXPMA, KDJ
from tqsdk.lib import TargetPosTask
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
        
        k5 = api.get_kline_serial(symbol, 300, data_length=5000)
        print(f"K 线：{len(k5)}根")
        
        e13 = EXPMA(k5, 13, 13)['ma1']
        e26 = EXPMA(k5, 26, 26)['ma1']
        
        # 调试输出
        for i in range(100, 110):
            if i < len(k5):
                print(f"  [{i}] e13={e13.iloc[i]:.1f} e26={e26.iloc[i]:.1f} diff={e13.iloc[i]-e26.iloc[i]:.1f}")
        
        target_pos = TargetPosTask(api, symbol)
        
        pos = 0
        daily = 0
        last_d = None
        
        while True:
            api.wait_update()
            
            if len(k5) < 100:
                continue
            
            i = len(k5) - 1
            p = k5.iloc[i]['close']
            t = str(k5.iloc[i]['datetime'])
            d = t[:10]
            
            if d != last_d:
                daily = 0
                last_d = d
            
            # 金叉开多
            if pos == 0 and daily < 3 and i >= 2:
                if e13.iloc[i-1] <= e26.iloc[i-1] and e13.iloc[i] > e26.iloc[i]:
                    hands = max(1, int(50000 / (p * info['multiplier'])))
                    target_pos.set_target_volume(hands)
                    pos = hands
                    daily += 1
                    print(f"  [开多] {t[:16]} @ {p:.1f} | {hands}手")
            
            # 死叉开空
            elif pos == 0 and daily < 3 and i >= 2:
                if e13.iloc[i-1] >= e26.iloc[i-1] and e13.iloc[i] < e26.iloc[i]:
                    hands = max(1, int(50000 / (p * info['multiplier'])))
                    target_pos.set_target_volume(-hands)
                    pos = -hands
                    daily += 1
                    print(f"  [开空] {t[:16]} @ {p:.1f} | {hands}手")
            
            # 反向信号平仓
            elif pos > 0 and i >= 2 and e13.iloc[i] < e26.iloc[i]:
                target_pos.set_target_volume(0)
                print(f"  [平多] {t[:16]} @ {p:.1f}")
                pos = 0
            
            elif pos < 0 and i >= 2 and e13.iloc[i] > e26.iloc[i]:
                target_pos.set_target_volume(0)
                print(f"  [平空] {t[:16]} @ {p:.1f}")
                pos = 0
    
    except BacktestFinished:
        api.close()
        
        # 获取交易记录
        trades = []
        if hasattr(sim, 'trade_log'):
            for date_key, log in sim.trade_log.items():
                for rec in log:
                    if rec.get('trade_id'):
                        trades.append(rec)
        
        stat = sim.tqsdk_stat if hasattr(sim, 'tqsdk_stat') else {}
        
        return {
            "symbol": symbol,
            "name": info['name'],
            "period": f"{start} ~ {end}",
            "total_trades": len(trades),
            "total_pnl": stat.get('profit_loss', 0),
            "win_rate": stat.get('winning_rate', 0),
            "trades": trades,
            "stat": stat
        }
    
    return {"symbol": symbol, "name": info['name'], "trades": []}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    code = sys.argv[1]
    start = sys.argv[2] if len(sys.argv) > 2 else "2025-01-01"
    end = sys.argv[3] if len(sys.argv) > 3 else "2025-03-22"
    
    result = backtest_one(code, start, end)
    
    os.makedirs("backtest_results", exist_ok=True)
    with open(f"backtest_results/{code}_result.json", 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\nSaved: {code}_result.json")
    print(f"Trades: {result.get('total_trades', 0)} | PnL: {result.get('total_pnl', 0)}")
