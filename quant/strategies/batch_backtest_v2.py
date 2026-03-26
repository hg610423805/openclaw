# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 批量回测（简化版）
"""

from tqsdk import TqApi, TqAuth, TqBacktest, TqSim
from tqsdk.ta import EMA, KDJ
import pandas as pd
import json
import os
from datetime import datetime, date
from typing import Dict, List
import sys
import re

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symbols_config import SYMBOL_CONFIG, get_full_symbol

# 导入账号
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD


class SimpleBacktest:
    """简化回测"""
    
    def __init__(self, symbol: str, start_date: str, end_date: str, initial_capital: float = 100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # 获取品种信息
        code = re.sub(r'\d+', '', symbol.split('.')[-1].lower())
        self.info = SYMBOL_CONFIG.get(code, {"tick": 1, "multiplier": 10, "commission_rate": 0.0001})
        
        self.trades = []
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.daily_trades = 0
        self.last_date = None
        
    def run(self) -> Dict:
        """运行回测"""
        print(f"\n{'='*60}")
        print(f"回测：{self.symbol}")
        print(f"区间：{self.start_date} ~ {self.end_date}")
        print(f"{'='*60}")
        
        # 创建 API（回测模式）
        api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=TqBacktest(
                start_dt=date(2025, 1, 1),
                end_dt=date(2025, 3, 22)
            )
        )
        
        # 获取 K 线（第二个参数是 duration_seconds）
        k30 = api.get_kline_serial(self.symbol, 1800)
        k5 = api.get_kline_serial(self.symbol, 300)
        
        if len(k5) < 100:
            print(f"  数据不足，跳过")
            api.close()
            return {"symbol": self.symbol, "error": "数据不足", "trades": []}
        
        # 指标
        e13_30 = EXPMA(k30['close'], 13)
        e26_30 = EXPMA(k30['close'], 26)
        kdj_30 = KDJ(k30, 9)
        
        e13_5 = EXPMA(k5['close'], 13)
        e26_5 = EXPMA(k5['close'], 26)
        kdj_5 = KDJ(k5, 9)
        
        tick = self.info["tick"]
        mult = self.info["multiplier"]
        comm_rate = self.info["commission_rate"]
        
        print(f"K 线：{len(k5)}条 | 开始回测...")
        
        # 主循环
        for i in range(100, len(k5)):
            cur_date = str(k5.iloc[i]['datetime'])[:10]
            if cur_date != self.last_date:
                self.daily_trades = 0
                self.last_date = cur_date
            
            price = k5.iloc[i]['close']
            time = str(k5.iloc[i]['datetime'])
            
            # 持仓管理
            if self.position != 0:
                # 止损
                if (self.position > 0 and price <= self.stop_loss) or \
                   (self.position < 0 and price >= self.stop_loss):
                    self._close(price, time, "止损", mult, comm_rate)
                    continue
                
                # 止盈
                if i >= 2:
                    prev_d = e13_5.iloc[i-1] - e26_5.iloc[i-1]
                    curr_d = e13_5.iloc[i] - e26_5.iloc[i]
                    if (self.position > 0 and prev_d > 0 and curr_d <= 0) or \
                       (self.position < 0 and prev_d < 0 and curr_d >= 0):
                        self._close(price, time, "止盈", mult, comm_rate)
                        continue
            
            # 开仓
            elif self.daily_trades < 3:
                j30 = kdj_30['j'].iloc[i] if i < len(kdj_30) else 50
                bull = e13_30.iloc[i] > e26_30.iloc[i]
                bear = e13_30.iloc[i] < e26_30.iloc[i]
                
                # 做多
                if bull and j30 < 20:
                    reason = None
                    if e13_5.iloc[i] > e26_5.iloc[i] and kdj_5['j'].iloc[i] < 20 and \
                       i >= 1 and k5.iloc[i]['low'] > k5.iloc[i-1]['low']:
                        reason = "方式 1: 双周期 J<20"
                    elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) <= 0 and \
                         (e13_5.iloc[i] - e26_5.iloc[i]) > 0:
                        reason = "方式 2: 金叉"
                    
                    if reason:
                        self._open_long(price, time, reason, k5, i, tick)
                
                # 做空
                elif bear and j30 > 80:
                    reason = None
                    if e13_5.iloc[i] < e26_5.iloc[i] and kdj_5['j'].iloc[i] > 80 and \
                       i >= 1 and k5.iloc[i]['high'] < k5.iloc[i-1]['high']:
                        reason = "方式 1: 双周期 J>80"
                    elif i >= 1 and (e13_5.iloc[i-1] - e26_5.iloc[i-1]) >= 0 and \
                         (e13_5.iloc[i] - e26_5.iloc[i]) < 0:
                        reason = "方式 2: 死叉"
                    
                    if reason:
                        self._open_short(price, time, reason, k5, i, tick)
        
        api.close()
        return self._report()
    
    def _open_long(self, price, time, reason, k5, i, tick):
        hands = int(self.initial_capital * 0.5 / (price * self.info["multiplier"]))
        if hands <= 0: return
        
        self.position = hands
        self.entry_price = price
        self.stop_loss = k5.iloc[i-1]['low'] - tick if "方式 1" in reason else price * 0.98
        
        self.current_trade = {
            "entry_time": time, "entry_price": price, "direction": "LONG",
            "hands": hands, "reason": reason, "stop_loss": self.stop_loss
        }
        self.daily_trades += 1
        print(f"  [开多] {time[:16]} @ {price} | 手数={hands} | {reason[:15]}")
    
    def _open_short(self, price, time, reason, k5, i, tick):
        hands = int(self.initial_capital * 0.5 / (price * self.info["multiplier"]))
        if hands <= 0: return
        
        self.position = -hands
        self.entry_price = price
        self.stop_loss = k5.iloc[i-1]['high'] + tick if "方式 1" in reason else price * 1.02
        
        self.current_trade = {
            "entry_time": time, "entry_price": price, "direction": "SHORT",
            "hands": hands, "reason": reason, "stop_loss": self.stop_loss
        }
        self.daily_trades += 1
        print(f"  [开空] {time[:16]} @ {price} | 手数={hands} | {reason[:15]}")
    
    def _close(self, price, time, reason, mult, comm_rate):
        if not hasattr(self, 'current_trade'): return
        
        trade = self.current_trade
        trade["exit_time"] = time
        trade["exit_price"] = price
        trade["exit_reason"] = reason
        
        if self.position > 0:
            pnl = (price - self.entry_price) * self.position * mult
        else:
            pnl = (self.entry_price - price) * abs(self.position) * mult
        
        comm = (self.entry_price + price) * abs(self.position) * mult * comm_rate
        slip = self.info["tick"] * abs(self.position) * mult * 2
        trade["pnl"] = pnl - comm - slip
        trade["commission"] = comm
        trade["slippage"] = slip
        
        self.trades.append(trade)
        print(f"  [平仓] {time[:16]} @ {price} | 盈亏={pnl - comm - slip:.0f} | {reason}")
        
        self.position = 0
        del self.current_trade
    
    def _report(self) -> Dict:
        if not self.trades:
            return {"symbol": self.symbol, "total_trades": 0, "trades": []}
        
        total_pnl = sum(t["pnl"] for t in self.trades)
        wins = [t for t in self.trades if t["pnl"] > 0]
        losses = [t for t in self.trades if t["pnl"] <= 0]
        
        return {
            "symbol": self.symbol,
            "symbol_name": self.info.get("name", ""),
            "period": f"{self.start_date} ~ {self.end_date}",
            "initial_capital": self.initial_capital,
            "total_trades": len(self.trades),
            "total_pnl": round(total_pnl, 2),
            "win_rate": round(len(wins)/len(self.trades)*100, 2) if self.trades else 0,
            "avg_win": round(sum(t["pnl"] for t in wins)/len(wins), 2) if wins else 0,
            "avg_loss": round(sum(t["pnl"] for t in losses)/len(losses), 2) if losses else 0,
            "total_commission": round(sum(t["commission"] for t in self.trades), 2),
            "entry_reasons": {},
            "exit_reasons": {},
            "trades": self.trades
        }


def batch_backtest(symbols, start, end):
    results = {}
    for sym in symbols:
        bt = SimpleBacktest(sym, start, end)
        results[sym] = bt.run()
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbols", default="rb,sm,sf,fg,m,rm,ur,ma")
    parser.add_argument("--start", default="2025-01-01")
    parser.add_argument("--end", default="2025-03-22")
    parser.add_argument("--output", default="backtest_results")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    codes = [c.strip() for c in args.symbols.split(',')]
    symbols = [get_full_symbol(c, "2505") for c in codes]
    
    print(f"\n{'='*60}")
    print(f"批量回测")
    print(f"品种：{', '.join(codes)}")
    print(f"区间：{args.start} ~ {args.end}")
    print(f"{'='*60}")
    
    results = batch_backtest(symbols, args.start, args.end)
    
    for sym, res in results.items():
        fn = f"{args.output}/{sym.replace('.', '_')}.json"
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"\n已保存：{fn}")
    
    with open(f"{args.output}/summary.json", 'w', encoding='utf-8') as f:
        json.dump({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "symbols": codes,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("完成！")
    print(f"{'='*60}")
 print(f"{'='*60}")
