# -*- coding: utf-8 -*-
"""
均线+KDJ 策略 - 批量回测脚本
按品种分开测试，生成独立报告
"""

from tqsdk import TqApi, TqAuth, TqBacktest, TqSim
from tqsdk.ta import EXPMA, KDJ
import pandas as pd
import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import sys

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from symbols_config import SYMBOL_CONFIG, get_full_symbol

# 导入主策略配置
sys.path.insert(0, '..')
from config import SHINNY_ACCOUNT, SHINNY_PASSWORD


@dataclass
class Trade:
    """交易记录"""
    entry_time: str
    entry_price: float
    direction: str  # LONG/SHORT
    hands: int
    exit_time: str
    exit_price: float
    pnl: float
    exit_reason: str  # 止损/止盈/移仓
    entry_reason: str  # 入场原因
    commission: float
    slippage: float
    stop_loss_price: float
    take_profit_price: float = 0
    
    def to_dict(self):
        return asdict(self)


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, symbol: str, start_date: str, end_date: str, 
                 initial_capital: float = 100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # 获取品种信息
        symbol_code = symbol.split('.')[-1].lower()
        # 去掉数字部分
        import re
        code_only = re.sub(r'\d+', '', symbol_code)
        self.symbol_info = SYMBOL_CONFIG.get(code_only, {
            "tick": 1,
            "multiplier": 10,
            "commission_rate": 0.0001
        })
        
        self.tick = self.symbol_info["tick"]
        self.multiplier = self.symbol_info["multiplier"]
        self.commission_rate = self.symbol_info["commission_rate"]
        
        # 策略参数
        self.expma_fast = 13
        self.expma_slow = 26
        self.kdj_period = 9
        self.max_daily_trades = 3
        self.max_position_ratio = 0.5
        
        # 状态
        self.trades: List[Trade] = []
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.daily_trades = 0
        self.last_trade_date = None
        self.current_trade: Optional[Trade] = None
        
        # 分型记录
        self.last_bull_fractal_low = None
        self.last_bear_fractal_high = None
        
        # 权益曲线
        self.equity_curve = []
        
    def run(self) -> Dict:
        """运行回测"""
        print(f"\n{'='*60}")
        print(f"回测：{self.symbol}")
        print(f"区间：{self.start_date} ~ {self.end_date}")
        print(f"{'='*60}")
        
        # 创建 API 实例（回测模式 + TqSim 模拟账户）
        sim = TqSim(init_balance=self.initial_capital)
        api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=TqBacktest(
                start_dt=self.start_date,
                end_dt=self.end_date
            ),
            _sim=sim
        )
        
        # 获取 K 线数据
        kline_30 = api.get_kline_serial(self.symbol, 500, duration_seconds=1800)
        kline_5 = api.get_kline_serial(self.symbol, 500, duration_seconds=300)
        
        # 计算指标
        expma13_30 = EXPMA(kline_30['close'], self.expma_fast)
        expma26_30 = EXPMA(kline_30['close'], self.expma_slow)
        kdj_30 = KDJ(kline_30, self.kdj_period)
        
        expma13_5 = EXPMA(kline_5['close'], self.expma_fast)
        expma26_5 = EXPMA(kline_5['close'], self.expma_slow)
        kdj_5 = KDJ(kline_5, self.kdj_period)
        
        print(f"K 线数据：{len(kline_5)}条 (5 分钟)")
        print(f"开始回测...")
        
        # 回测主循环
        for i in range(100, len(kline_5)):
            # 重置每日交易次数
            current_date = str(kline_5.iloc[i]['datetime'])[:10]
            if current_date != self.last_trade_date:
                self.daily_trades = 0
                self.last_trade_date = current_date
            
            # 获取当前价格
            current_price = kline_5.iloc[i]['close']
            current_time = str(kline_5.iloc[i]['datetime'])
            
            # 更新权益曲线
            if self.position != 0 and self.current_trade:
                if self.position > 0:
                    unrealized_pnl = (current_price - self.entry_price) * self.position * self.multiplier
                else:
                    unrealized_pnl = (self.entry_price - current_price) * abs(self.position) * self.multiplier
                equity = self.initial_capital + sum(t.pnl for t in self.trades) + unrealized_pnl
            else:
                equity = self.initial_capital + sum(t.pnl for t in self.trades)
            self.equity_curve.append({"time": current_time, "equity": equity})
            
            # 持仓管理
            if self.position != 0 and self.current_trade:
                # 检查止损
                if self.position > 0 and current_price <= self.stop_loss:
                    self._close_position(current_price, current_time, "止损")
                    continue
                elif self.position < 0 and current_price >= self.stop_loss:
                    self._close_position(current_price, current_time, "止损")
                    continue
                
                # 检查止盈（均线反向交叉）
                if i >= 2:
                    prev_diff = expma13_5.iloc[i-1] - expma26_5.iloc[i-1]
                    curr_diff = expma13_5.iloc[i] - expma26_5.iloc[i]
                    
                    if self.position > 0 and prev_diff > 0 and curr_diff <= 0:
                        self._close_position(current_price, current_time, "止盈 (死叉)")
                        continue
                    elif self.position < 0 and prev_diff < 0 and curr_diff >= 0:
                        self._close_position(current_price, current_time, "止盈 (金叉)")
                        continue
                
                # 更新移动止损
                self._update_trailing_stop(kline_5, i)
            
            # 开仓检查
            elif self.daily_trades < self.max_daily_trades:
                # 30 分钟方向判断
                j_30 = kdj_30['j'].iloc[i] if i < len(kdj_30) else 50
                is_bullish = expma13_30.iloc[i] > expma26_30.iloc[i]
                is_bearish = expma13_30.iloc[i] < expma26_30.iloc[i]
                
                # 做多检查
                if is_bullish and j_30 < 20:
                    entry_reason = None
                    
                    # 方式 1: 双均线多 + J<20 + K 线确认
                    if (expma13_5.iloc[i] > expma26_5.iloc[i] and 
                        kdj_5['j'].iloc[i] < 20 and
                        i >= 1 and kline_5.iloc[i]['low'] > kline_5.iloc[i-1]['low']):
                        entry_reason = "方式 1: 双周期 J<20+ 均线多 +K 线强势"
                    
                    # 方式 2: 金叉入场
                    elif i >= 1:
                        prev_diff = expma13_5.iloc[i-1] - expma26_5.iloc[i-1]
                        curr_diff = expma13_5.iloc[i] - expma26_5.iloc[i]
                        if prev_diff <= 0 and curr_diff > 0:
                            entry_reason = "方式 2: 5 分钟金叉"
                    
                    if entry_reason:
                        self._open_long(current_price, current_time, entry_reason, 
                                      kline_5, i, expma13_5, expma26_5)
                
                # 做空检查
                elif is_bearish and j_30 > 80:
                    entry_reason = None
                    
                    # 方式 1: 双均线空 + J>80 + K 线确认
                    if (expma13_5.iloc[i] < expma26_5.iloc[i] and 
                        kdj_5['j'].iloc[i] > 80 and
                        i >= 1 and kline_5.iloc[i]['high'] < kline_5.iloc[i-1]['high']):
                        entry_reason = "方式 1: 双周期 J>80+ 均线空 +K 线弱势"
                    
                    # 方式 2: 死叉入场
                    elif i >= 1:
                        prev_diff = expma13_5.iloc[i-1] - expma26_5.iloc[i-1]
                        curr_diff = expma13_5.iloc[i] - expma26_5.iloc[i]
                        if prev_diff >= 0 and curr_diff < 0:
                            entry_reason = "方式 2: 5 分钟死叉"
                    
                    if entry_reason:
                        self._open_short(current_price, current_time, entry_reason,
                                       kline_5, i)
        
        api.close()
        
        # 生成报告
        return self._generate_report()
    
    def _open_long(self, price: float, time: str, reason: str, 
                   kline_5, idx, expma13_5, expma26_5):
        """开多"""
        hands = int(self.initial_capital * self.max_position_ratio / (price * self.multiplier))
        if hands <= 0:
            return
        
        self.position = hands
        self.entry_price = price
        
        # 设置止损
        if "方式 1" in reason:
            sl = kline_5.iloc[idx-1]['low'] - self.tick
        else:
            # 方式 2: 底分型
            sl = self.last_bull_fractal_low or (price * 0.98)
        
        self.stop_loss = sl
        
        self.current_trade = Trade(
            entry_time=time,
            entry_price=price,
            direction="LONG",
            hands=hands,
            exit_time="",
            exit_price=0,
            pnl=0,
            exit_reason="",
            entry_reason=reason,
            commission=0,
            slippage=0,
            stop_loss_price=sl
        )
        
        self.daily_trades += 1
        print(f"  [开多] {time} @ {price} | 手数={hands} | 止损={sl} | 原因={reason[:20]}")
    
    def _open_short(self, price: float, time: str, reason: str, kline_5, idx):
        """开空"""
        hands = int(self.initial_capital * self.max_position_ratio / (price * self.multiplier))
        if hands <= 0:
            return
        
        self.position = -hands
        self.entry_price = price
        
        # 设置止损
        if "方式 1" in reason:
            sl = kline_5.iloc[idx-1]['high'] + self.tick
        else:
            # 方式 2: 顶分型
            sl = self.last_bear_fractal_high or (price * 1.02)
        
        self.stop_loss = sl
        
        self.current_trade = Trade(
            entry_time=time,
            entry_price=price,
            direction="SHORT",
            hands=hands,
            exit_time="",
            exit_price=0,
            pnl=0,
            exit_reason="",
            entry_reason=reason,
            commission=0,
            slippage=0,
            stop_loss_price=sl
        )
        
        self.daily_trades += 1
        print(f"  [开空] {time} @ {price} | 手数={hands} | 止损={sl} | 原因={reason[:20]}")
    
    def _close_position(self, price: float, time: str, reason: str):
        """平仓"""
        if not self.current_trade:
            return
        
        self.current_trade.exit_time = time
        self.current_trade.exit_price = price
        self.current_trade.exit_reason = reason
        
        # 计算盈亏
        if self.position > 0:
            gross_pnl = (price - self.entry_price) * self.position * self.multiplier
        else:
            gross_pnl = (self.entry_price - price) * abs(self.position) * self.multiplier
        
        # 手续费和滑点
        commission = (self.entry_price + price) * abs(self.position) * self.multiplier * self.commission_rate
        slippage = self.tick * abs(self.position) * self.multiplier * 2
        
        self.current_trade.pnl = gross_pnl - commission - slippage
        self.current_trade.commission = commission
        self.current_trade.slippage = slippage
        
        self.trades.append(self.current_trade)
        print(f"  [平仓] {time} @ {price} | 盈亏={self.current_trade.pnl:.2f} | 原因={reason}")
        
        self.position = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.current_trade = None
    
    def _update_trailing_stop(self, kline_5, idx):
        """更新移动止损"""
        if idx < 2:
            return
        
        if self.position > 0:
            # 检测底分型
            prev_low = kline_5.iloc[idx-1]['low']
            prev2_low = kline_5.iloc[idx-2]['low']
            curr_low = kline_5.iloc[idx]['low']
            
            if prev_low < prev2_low and prev_low < curr_low:
                # 底分型形成
                if self.last_bull_fractal_low is None or prev_low > self.last_bull_fractal_low:
                    self.last_bull_fractal_low = prev_low
                    new_sl = prev_low - self.tick
                    if new_sl > self.stop_loss:
                        self.stop_loss = new_sl
                        self.current_trade.stop_loss_price = new_sl
        
        elif self.position < 0:
            # 检测顶分型
            prev_high = kline_5.iloc[idx-1]['high']
            prev2_high = kline_5.iloc[idx-2]['high']
            curr_high = kline_5.iloc[idx]['high']
            
            if prev_high > prev2_high and prev_high > curr_high:
                # 顶分型形成
                if self.last_bear_fractal_high is None or prev_high < self.last_bear_fractal_high:
                    self.last_bear_fractal_high = prev_high
                    new_sl = prev_high + self.tick
                    if new_sl < self.stop_loss:
                        self.stop_loss = new_sl
                        self.current_trade.stop_loss_price = new_sl
    
    def _generate_report(self) -> Dict:
        """生成回测报告"""
        if not self.trades:
            return {
                "symbol": self.symbol,
                "period": f"{self.start_date} ~ {self.end_date}",
                "total_trades": 0,
                "total_pnl": 0,
                "error": "无交易记录"
            }
        
        # 基础统计
        total_pnl = sum(t.pnl for t in self.trades)
        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(self.trades) * 100
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades and sum(t.pnl for t in losing_trades) != 0 else 0
        
        # 最大回撤
        peak = self.initial_capital
        max_drawdown = 0
        for t in self.trades:
            peak = max(peak, peak + t.pnl)
            drawdown = (peak - (self.initial_capital + sum(x.pnl for x in self.trades[:self.trades.index(t)+1]))) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        # 交易时长统计
        holding_periods = []
        for t in self.trades:
            if t.entry_time and t.exit_time:
                try:
                    entry = pd.to_datetime(t.entry_time)
                    exit = pd.to_datetime(t.exit_time)
                    holding_periods.append((exit - entry).total_seconds() / 3600)  # 小时
                except:
                    pass
        
        avg_holding = sum(holding_periods) / len(holding_periods) if holding_periods else 0
        
        # 入场方式统计
        entry_reasons = {}
        for t in self.trades:
            reason = t.entry_reason.split(':')[0] if ':' in t.entry_reason else t.entry_reason
            entry_reasons[reason] = entry_reasons.get(reason, 0) + 1
        
        # 出场原因统计
        exit_reasons = {}
        for t in self.trades:
            exit_reasons[t.exit_reason] = exit_reasons.get(t.exit_reason, 0) + 1
        
        # 手续费统计
        total_commission = sum(t.commission for t in self.trades)
        total_slippage = sum(t.slippage for t in self.trades)
        
        report = {
            "symbol": self.symbol,
            "symbol_name": self.symbol_info.get("name", "未知"),
            "period": f"{self.start_date} ~ {self.end_date}",
            "initial_capital": self.initial_capital,
            
            # 核心指标
            "total_trades": len(self.trades),
            "total_pnl": total_pnl,
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_drawdown, 2),
            
            # 交易统计
            "avg_holding_hours": round(avg_holding, 2),
            "total_commission": round(total_commission, 2),
            "total_slippage": round(total_slippage, 2),
            
            # 入场方式
            "entry_reasons": entry_reasons,
            
            # 出场原因
            "exit_reasons": exit_reasons,
            
            # 权益曲线
            "equity_curve": self.equity_curve[-100:],  # 最后 100 个点
            
            # 交易明细
            "trades": [t.to_dict() for t in self.trades]
        }
        
        return report


def batch_backtest(symbols: List[str], start_date: str, end_date: str) -> Dict:
    """批量回测"""
    results = {}
    
    for symbol in symbols:
        engine = BacktestEngine(symbol, start_date, end_date)
        result = engine.run()
        results[symbol] = result
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="批量回测")
    parser.add_argument("--symbols", default="rb,sm,sf,fg,m,rm,ur,ma", 
                       help="品种列表，逗号分隔")
    parser.add_argument("--start", default="2025-01-01", help="开始日期")
    parser.add_argument("--end", default="2025-03-22", help="结束日期")
    parser.add_argument("--output", default="backtest_results", help="输出目录")
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output, exist_ok=True)
    
    # 解析品种列表
    symbol_codes = args.symbols.split(',')
    
    # 生成完整合约代码
    symbols = []
    for code in symbol_codes:
        symbols.append(get_full_symbol(code.strip(), "2505"))
    
    print(f"\n{'='*60}")
    print(f"批量回测")
    print(f"品种：{', '.join(symbol_codes)}")
    print(f"区间：{args.start} ~ {args.end}")
    print(f"{'='*60}")
    
    # 批量回测
    results = batch_backtest(symbols, args.start, args.end)
    
    # 保存结果
    for symbol, result in results.items():
        filename = f"{args.output}/{symbol.replace('.', '_')}_result.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n已保存：{filename}")
    
    # 保存汇总
    summary = {
        "backtest_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbols": symbol_codes,
        "period": f"{args.start} ~ {args.end}",
        "results": results
    }
    
    with open(f"{args.output}/summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print("批量回测完成！")
    print(f"{'='*60}")
n{'='*60}")
    print("批量回测完成！")
    print(f"{'='*60}")
