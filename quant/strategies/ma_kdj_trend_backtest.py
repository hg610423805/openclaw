# -*- coding: utf-8 -*-
"""
均线+KDJ 趋势跟踪策略 - 回测脚本
"""

from tqsdk import TqApi, TqAuth, Backtest
from tqsdk.indicators import MA, KDJ
from tqsdk.ta import EXPMA
import pandas as pd
from datetime import datetime
from typing import Dict, List
import json


class BacktestConfig:
    """回测配置"""
    SYMBOLS = ["SHFE.rb2505"]  # 回测合约列表
    START_DATE = "2025-01-01"
    END_DATE = "2025-03-22"
    INITIAL_CAPITAL = 100000
    COMMISSION_RATIO = 0.0001  # 手续费万分之一
    SLIPPAGE = 1  # 滑点 1 个 tick
    
    # 策略参数
    EXPMA_FAST = 13
    EXPMA_SLOW = 26
    KDJ_PERIOD = 9
    MAX_DAILY_TRADES = 3
    MAX_POSITION_RATIO = 0.5


class Trade:
    """交易记录"""
    def __init__(self, entry_time: str, entry_price: float, direction: str, 
                 hands: int, exit_time: str = None, exit_price: float = None,
                 pnl: float = 0, exit_reason: str = ""):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.direction = direction  # LONG/SHORT
        self.hands = hands
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.pnl = pnl
        self.exit_reason = exit_reason  # 止损/止盈/移仓
    
    def to_dict(self) -> dict:
        return {
            "entry_time": self.entry_time,
            "entry_price": self.entry_price,
            "direction": self.direction,
            "hands": self.hands,
            "exit_time": self.exit_time,
            "exit_price": self.exit_price,
            "pnl": self.pnl,
            "exit_reason": self.exit_reason
        }


class MA_KDJ_Backtest:
    """策略回测"""
    
    def __init__(self, api: TqApi, symbol: str, start: str, end: str):
        self.api = api
        self.symbol = symbol
        self.start = start
        self.end = end
        self.config = BacktestConfig()
        
        # 回测账户（从 config.py 读取认证）
        import sys
        sys.path.insert(0, '..')
        from config import SHINNY_ACCOUNT, SHINNY_PASSWORD
        
        self.api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=Backtest(
                start_dt=self.start,
                end_dt=self.end,
                initial_cash=self.config.INITIAL_CAPITAL
            )
        )
        
        # K 线数据
        self.kline_30 = api.get_kline_serial(symbol, 200, duration_seconds=1800)
        self.kline_5 = api.get_kline_serial(symbol, 200, duration_seconds=300)
        
        # 指标
        self.expma13_30 = EXPMA(self.kline_30['close'], self.config.EXPMA_FAST)
        self.expma26_30 = EXPMA(self.kline_30['close'], self.config.EXPMA_SLOW)
        self.kdj_30 = KDJ(self.kline_30, self.config.KDJ_PERIOD)
        
        self.expma13_5 = EXPMA(self.kline_5['close'], self.config.EXPMA_FAST)
        self.expma26_5 = EXPMA(self.kline_5['close'], self.config.EXPMA_SLOW)
        self.kdj_5 = KDJ(self.kline_5, self.config.KDJ_PERIOD)
        
        # 交易记录
        self.trades: List[Trade] = []
        self.current_trade: Trade = None
        
        # 状态
        self.position = 0
        self.daily_trades = 0
        self.last_trade_date = None
    
    def get_j_value(self, kdj_series) -> float:
        """获取 J 值"""
        return kdj_series.iloc[-1] if len(kdj_series) > 0 else 50
    
    def is_bullish_30(self) -> bool:
        return self.expma13_30.iloc[-1] > self.expma26_30.iloc[-1]
    
    def is_bearish_30(self) -> bool:
        return self.expma13_30.iloc[-1] < self.expma26_30.iloc[-1]
    
    def check_long_signal_1(self) -> bool:
        """做多方式 1"""
        if self.get_j_value(self.kdj_30['j']) >= 20:
            return False
        if not self.is_bullish_30():
            return False
        if self.expma13_5.iloc[-1] <= self.expma26_5.iloc[-1]:
            return False
        if self.get_j_value(self.kdj_5['j']) >= 20:
            return False
        if len(self.kline_5) < 2:
            return False
        if self.kline_5.iloc[-1]['low'] <= self.kline_5.iloc[-2]['low']:
            return False
        return True
    
    def check_long_signal_2(self) -> bool:
        """做多方式 2（金叉）"""
        if self.get_j_value(self.kdj_30['j']) >= 20:
            return False
        if not self.is_bullish_30():
            return False
        if len(self.expma13_5) < 2:
            return False
        prev = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        return prev <= 0 and curr > 0
    
    def check_short_signal_1(self) -> bool:
        """做空方式 1 - 【规则 9+10】"""
        # 【规则 9】30 分钟 J 值>80
        if self.get_j_value(self.kdj_30['j']) <= 80:
            return False
        # 【规则 9】30 分钟 EXPMA13<EXPMA26
        if not self.is_bearish_30():
            return False
        # 【规则 10-1】5 分钟 EXPMA13<EXPMA26
        if self.expma13_5.iloc[-1] >= self.expma26_5.iloc[-1]:
            return False
        # 【规则 10-1】5 分钟 J 值>80
        if self.get_j_value(self.kdj_5['j']) <= 80:
            return False
        # 【规则 10-1】K 线确认
        if len(self.kline_5) < 2:
            return False
        if self.kline_5.iloc[-1]['high'] >= self.kline_5.iloc[-2]['high']:
            return False
        return True
    
    def check_short_signal_2(self) -> bool:
        """做空方式 2（死叉） - 【规则 9+10】"""
        # 【规则 9】30 分钟 J 值>80
        if self.get_j_value(self.kdj_30['j']) <= 80:
            return False
        # 【规则 9】30 分钟 EXPMA13<EXPMA26
        if not self.is_bearish_30():
            return False
        # 【规则 10-2】死叉检查
        if len(self.expma13_5) < 2:
            return False
        prev = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        return prev >= 0 and curr < 0
    
    def open_long(self, signal_type: int):
        """开多"""
        if self.position != 0:
            return
        
        price = self.kline_5.iloc[-1]['close']
        time = self.kline_5.iloc[-1]['datetime']
        hands = int(self.config.INITIAL_CAPITAL * self.config.MAX_POSITION_RATIO / (price * 10))
        
        self.position = hands
        self.current_trade = Trade(
            entry_time=str(time),
            entry_price=price,
            direction="LONG",
            hands=hands
        )
        self.daily_trades += 1
        
        # 设置止损
        if signal_type == 1:
            sl = self.kline_5.iloc[-2]['low'] - 1
        else:
            sl = price * 0.98
        self.current_trade.stop_loss = sl
        
        print(f"[开多] {time} @ {price}, 手数={hands}, 止损={sl}")
    
    def open_short(self, signal_type: int):
        """开空"""
        if self.position != 0:
            return
        
        price = self.kline_5.iloc[-1]['close']
        time = self.kline_5.iloc[-1]['datetime']
        hands = int(self.config.INITIAL_CAPITAL * self.config.MAX_POSITION_RATIO / (price * 10))
        
        self.position = -hands
        self.current_trade = Trade(
            entry_time=str(time),
            entry_price=price,
            direction="SHORT",
            hands=hands
        )
        self.daily_trades += 1
        
        # 设置止损
        if signal_type == 1:
            sl = self.kline_5.iloc[-2]['high'] + 1
        else:
            sl = price * 1.02
        self.current_trade.stop_loss = sl
        
        print(f"[开空] {time} @ {price}, 手数={hands}, 止损={sl}")
    
    def close_position(self, price: float, reason: str):
        """平仓"""
        if self.current_trade is None:
            return
        
        time = self.kline_5.iloc[-1]['datetime']
        self.current_trade.exit_time = str(time)
        self.current_trade.exit_price = price
        self.current_trade.exit_reason = reason
        
        if self.current_trade.direction == "LONG":
            pnl = (price - self.current_trade.entry_price) * self.current_trade.hands * 10
        else:
            pnl = (self.current_trade.entry_price - price) * self.current_trade.hands * 10
        
        # 扣除手续费和滑点
        commission = (self.current_trade.entry_price + price) * self.current_trade.hands * 10 * self.config.COMMISSION_RATIO
        slip = self.config.SLIPPAGE * self.current_trade.hands * 10 * 2
        self.current_trade.pnl = pnl - commission - slip
        
        self.trades.append(self.current_trade)
        print(f"[平仓] {time} @ {price}, 盈亏={self.current_trade.pnl:.2f}, 原因={reason}")
        
        self.position = 0
        self.current_trade = None
    
    def check_exit_conditions(self):
        """检查出场条件"""
        if self.position == 0 or self.current_trade is None:
            return
        
        price = self.kline_5.iloc[-1]['close']
        
        # 止损检查
        if self.position > 0 and price <= self.current_trade.stop_loss:
            self.close_position(price, "止损")
            return
        if self.position < 0 and price >= self.current_trade.stop_loss:
            self.close_position(price, "止损")
            return
        
        # 止盈检查（均线反向交叉）
        if len(self.expma13_5) < 2:
            return
        
        prev_diff = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr_diff = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        
        if self.position > 0 and prev_diff > 0 and curr_diff <= 0:
            self.close_position(price, "止盈 (死叉)")
        elif self.position < 0 and prev_diff < 0 and curr_diff >= 0:
            self.close_position(price, "止盈 (金叉)")
    
    def run(self):
        """运行回测"""
        print(f"[回测开始] {self.symbol} | {self.start} ~ {self.end}")
        
        while True:
            self.api.wait_update()
            
            # 重置每日交易次数
            today = str(self.kline_5.iloc[-1]['datetime'])[:10]
            if today != self.last_trade_date:
                self.daily_trades = 0
                self.last_trade_date = today
            
            # 出场检查
            self.check_exit_conditions()
            
            # 入场检查
            if self.position == 0 and self.daily_trades < self.config.MAX_DAILY_TRADES:
                if self.is_bullish_30():
                    if self.check_long_signal_1():
                        self.open_long(1)
                    elif self.check_long_signal_2():
                        self.open_long(2)
                elif self.is_bearish_30():
                    if self.check_short_signal_1():
                        self.open_short(1)
                    elif self.check_short_signal_2():
                        self.open_short(2)
        
        self.api.close()
    
    def generate_report(self) -> dict:
        """生成回测报告"""
        if not self.trades:
            return {"error": "无交易记录"}
        
        total_pnl = sum(t.pnl for t in self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(self.trades) * 100 if self.trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades and sum(t.pnl for t in losing_trades) != 0 else 0
        
        max_drawdown = 0
        peak = 0
        for t in self.trades:
            peak = max(peak, t.pnl)
            drawdown = peak - t.pnl
            max_drawdown = max(max_drawdown, drawdown)
        
        report = {
            "symbol": self.symbol,
            "period": f"{self.start} ~ {self.end}",
            "total_trades": len(self.trades),
            "total_pnl": total_pnl,
            "win_rate": f"{win_rate:.2f}%",
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "trades": [t.to_dict() for t in self.trades]
        }
        
        return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="均线+KDJ 策略回测")
    parser.add_argument("--symbol", default="SHFE.rb2505", help="交易合约")
    parser.add_argument("--start", default="2025-01-01", help="开始日期")
    parser.add_argument("--end", default="2025-03-22", help="结束日期")
    args = parser.parse_args()
    
    api = TqApi(auth=TqAuth("你的天勤账号", "你的密码"))
    backtest = MA_KDJ_Backtest(api, args.symbol, args.start, args.end)
    backtest.run()
    
    report = backtest.generate_report()
    print("\n" + "="*50)
    print("回测报告")
    print("="*50)
    print(f"合约：{report['symbol']}")
    print(f"区间：{report['period']}")
    print(f"总交易：{report['total_trades']}笔")
    print(f"总盈亏：{report['total_pnl']:.2f}元")
    print(f"胜率：{report['win_rate']}")
    print(f"盈亏比：{report['profit_factor']:.2f}")
    print(f"最大回撤：{report['max_drawdown']:.2f}元")
    print("="*50)
