# -*- coding: utf-8 -*-
"""
EXPMA 双向策略回测 - 真实数据版本
使用 TqSim 模拟账户获取天勤量化真实历史数据
回测周期：2025-03-22 至 2026-03-22（1 年）
"""

from tqsdk import TqApi, TqSim, TqAuth
from tqsdk.ta import MA  # 使用天勤内置指标
import datetime
import json
import pandas as pd
import numpy as np

def expma(series, period):
    """手动实现 EXPMA 指标"""
    return series.ewm(span=period, adjust=False).mean()

class EXPMA_BacktestReal:
    def __init__(self, symbol, start_date, end_date, initial_capital=100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        # 使用 TqSim 模拟账户 + 真实账号获取真实数据
        print(f"[{datetime.datetime.now()}] 正在通过天勤量化获取 {symbol} 真实历史数据...")
        self.api = TqApi(TqSim(), auth=TqAuth(user_name="hg610423805", password="Hgssh285755"))
        
        # 获取日线数据
        self.klines_daily = self.api.get_kline_serial(symbol, 86400, 500)
        # 获取 5 分钟数据
        self.klines_5m = self.api.get_kline_serial(symbol, 300, 10000)
        
        print(f"[{datetime.datetime.now()}] 数据获取完成 - 日线：{len(self.klines_daily)}条，5 分钟：{len(self.klines_5m)}条")
        
        # 计算 EXPMA 指标
        self.expma5_d = expma(self.klines_daily['close'], 5)
        self.expma10_d = expma(self.klines_daily['close'], 10)
        self.expma20_d = expma(self.klines_daily['close'], 20)
        
        self.expma5_5m = expma(self.klines_5m['close'], 5)
        self.expma10_5m = expma(self.klines_5m['close'], 10)
        
        # 回测结果
        self.trades = []
        self.capital_curve = []
        self.capital = initial_capital
        self.position = 0
        self.entry_price = 0
        self.entry_bar_low = 0
        self.entry_bar_high = 0
        
        # 统计指标
        self.total_profit = 0
        self.win_count = 0
        self.loss_count = 0
        self.max_drawdown = 0
        self.peak_capital = initial_capital
        self.total_trades = 0
    
    def check_daily_trend(self, idx):
        """判断日线趋势"""
        if idx < 20 or idx >= len(self.expma5_d):
            return 0
        
        e5 = self.expma5_d.iloc[idx]
        e10 = self.expma10_d.iloc[idx]
        e20 = self.expma20_d.iloc[idx]
        e5_prev = self.expma5_d.iloc[idx-1]
        e10_prev = self.expma10_d.iloc[idx-1]
        
        # 做多趋势：EXPMA5>10>20 且向上发散
        if (e5 > e10 > e20) and (e5 > e5_prev) and (e10 > e10_prev):
            return 1
        
        # 做空趋势：EXPMA5<10<20 且向下发散
        if (e5 < e10 < e20) and (e5 < e5_prev) and (e10 < e10_prev):
            return -1
        
        return 0
    
    def get_6bar_range(self, idx):
        """获取前 6 根 5 分钟 K 线的高低点"""
        if idx < 7:
            return None, None
        
        recent = self.klines_5m.iloc[idx-7:idx-1]
        high = recent['high'].max()
        low = recent['low'].min()
        return high, low
    
    def check_cross(self, idx):
        """检查 EXPMA 金叉/死叉"""
        if idx < 2 or idx >= len(self.expma5_5m):
            return 0
        
        e5_curr = self.expma5_5m.iloc[idx]
        e10_curr = self.expma10_5m.iloc[idx]
        e5_prev = self.expma5_5m.iloc[idx-1]
        e10_prev = self.expma10_5m.iloc[idx-1]
        
        # 死叉：5 从上方下穿 10
        if e5_prev > e10_prev and e5_curr < e10_curr:
            return -1
        
        # 金叉：5 从下方上穿 10
        if e5_prev < e10_prev and e5_curr > e10_curr:
            return 1
        
        return 0
    
    def run_backtest(self):
        """运行回测"""
        print(f"[{datetime.datetime.now()}] 开始回测...")
        
        for i in range(10, len(self.klines_5m)):
            curr_kline = self.klines_5m.iloc[i]
            curr_time = datetime.datetime.fromtimestamp(curr_kline['datetime'] / 1e9)
            curr_price = curr_kline['close']
            
            # 检查是否临近收盘（14:57 强制平仓）
            if curr_time.hour == 14 and curr_time.minute >= 57:
                if self.position != 0:
                    profit = (curr_price - self.entry_price) * self.position * 5
                    self.capital += profit
                    self.trades.append({
                        'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '平仓',
                        'direction': '多' if self.position > 0 else '空',
                        'price': float(curr_price),
                        'profit': float(profit),
                        'capital': float(self.capital),
                        'reason': '收盘强制平仓'
                    })
                    self.position = 0
                continue
            
            # 日线趋势（使用最近的日线数据）
            daily_idx = min(i // 48, len(self.klines_daily) - 1)
            trend = self.check_daily_trend(daily_idx)
            
            if trend == 0:
                if self.position != 0:
                    profit = (curr_price - self.entry_price) * self.position * 5
                    self.capital += profit
                    self.trades.append({
                        'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '平仓',
                        'direction': '多' if self.position > 0 else '空',
                        'price': float(curr_price),
                        'profit': float(profit),
                        'capital': float(self.capital),
                        'reason': '日线震荡'
                    })
                    self.position = 0
                continue
            
            range_high, range_low = self.get_6bar_range(i)
            if range_high is None:
                continue
            
            cross_signal = self.check_cross(i)
            
            # 做多逻辑
            if trend == 1:
                if self.position == 0 and curr_price > range_high:
                    self.position = 1
                    self.entry_price = curr_price
                    self.entry_bar_low = float(curr_kline['low'])
                    self.trades.append({
                        'open_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '开仓',
                        'direction': '多',
                        'price': float(curr_price),
                        'capital': float(self.capital),
                        'reason': f'突破前 6 根 K 线高点 {range_high:.2f}'
                    })
                
                elif self.position == 1:
                    # 止损：跌破入场 K 线最低点
                    if curr_price < self.entry_bar_low:
                        profit = (curr_price - self.entry_price) * 5
                        self.capital += profit
                        self.trades.append({
                            'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                            'type': '平仓',
                            'direction': '多',
                            'price': float(curr_price),
                            'profit': float(profit),
                            'capital': float(self.capital),
                            'reason': f'止损 {self.entry_bar_low:.2f}'
                        })
                        self.position = 0
                    
                    # 止盈：死叉出场
                    elif cross_signal == -1:
                        profit = (curr_price - self.entry_price) * 5
                        self.capital += profit
                        self.trades.append({
                            'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                            'type': '平仓',
                            'direction': '多',
                            'price': float(curr_price),
                            'profit': float(profit),
                            'capital': float(self.capital),
                            'reason': '死叉止盈'
                        })
                        self.position = 0
            
            # 做空逻辑
            elif trend == -1:
                if self.position == 0 and curr_price < range_low:
                    self.position = -1
                    self.entry_price = curr_price
                    self.entry_bar_high = float(curr_kline['high'])
                    self.trades.append({
                        'open_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '开仓',
                        'direction': '空',
                        'price': float(curr_price),
                        'capital': float(self.capital),
                        'reason': f'跌破前 6 根 K 线低点 {range_low:.2f}'
                    })
                
                elif self.position == -1:
                    # 止损：突破入场 K 线最高点
                    if curr_price > self.entry_bar_high:
                        profit = (self.entry_price - curr_price) * 5
                        self.capital += profit
                        self.trades.append({
                            'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                            'type': '平仓',
                            'direction': '空',
                            'price': float(curr_price),
                            'profit': float(profit),
                            'capital': float(self.capital),
                            'reason': f'止损 {self.entry_bar_high:.2f}'
                        })
                        self.position = 0
                    
                    # 止盈：金叉出场
                    elif cross_signal == 1:
                        profit = (self.entry_price - curr_price) * 5
                        self.capital += profit
                        self.trades.append({
                            'close_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                            'type': '平仓',
                            'direction': '空',
                            'price': float(curr_price),
                            'profit': float(profit),
                            'capital': float(self.capital),
                            'reason': '金叉止盈'
                        })
                        self.position = 0
            
            # 更新资金曲线
            self.capital_curve.append({
                'time': curr_time.strftime("%Y-%m-%d"),
                'capital': float(self.capital)
            })
            
            # 更新峰值和回撤
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            drawdown = (self.peak_capital - self.capital) / self.peak_capital
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
        
        self.calculate_stats()
        print(f"[{datetime.datetime.now()}] 回测完成！")
    
    def calculate_stats(self):
        """计算统计指标"""
        self.total_profit = self.capital - self.initial_capital
        
        # 统计盈亏交易
        closed_trades = [t for t in self.trades if t.get('profit') is not None]
        self.win_count = len([t for t in closed_trades if t['profit'] > 0])
        self.loss_count = len([t for t in closed_trades if t['profit'] <= 0])
        self.total_trades = len(closed_trades)
        self.win_rate = self.win_count / self.total_trades * 100 if self.total_trades > 0 else 0
        
        # 年化收益
        days = (datetime.datetime.strptime(self.end_date, "%Y-%m-%d") - 
                datetime.datetime.strptime(self.start_date, "%Y-%m-%d")).days
        self.annual_return = (self.total_profit / self.initial_capital) * (365 / days) * 100 if days > 0 else 0
        
        # 月度盈亏
        self.monthly_pnl = {}
        for t in closed_trades:
            month = t['close_time'][:7]  # YYYY-MM
            self.monthly_pnl[month] = self.monthly_pnl.get(month, 0) + t.get('profit', 0)
    
    def get_results(self):
        """返回回测结果"""
        return {
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': float(self.capital),
            'total_profit': float(self.total_profit),
            'total_trades': self.total_trades,
            'win_count': self.win_count,
            'loss_count': self.loss_count,
            'win_rate': round(self.win_rate, 2),
            'annual_return': round(self.annual_return, 2),
            'max_drawdown': round(self.max_drawdown * 100, 2),
            'monthly_pnl': self.monthly_pnl,
            'trades': self.trades,
            'capital_curve': self.capital_curve,
            'data_source': '天勤量化真实历史数据 (TqSim)'
        }


if __name__ == "__main__":
    START_DATE = "2025-03-22"
    END_DATE = "2026-03-22"
    INITIAL_CAPITAL = 100000
    
    # 测试品种（使用正确的郑商所合约代码）
    SYMBOLS = [
        ("CZCE.SF000", "硅铁主力连续"),
        ("CZCE.SM000", "锰硅主力连续")
    ]
    
    results = {}
    
    for symbol, name in SYMBOLS:
        print(f"\n{'='*60}")
        print(f"开始回测：{name} ({symbol})")
        print(f"{'='*60}\n")
        
        try:
            backtest = EXPMA_BacktestReal(symbol, START_DATE, END_DATE, INITIAL_CAPITAL)
            backtest.run_backtest()
            results[symbol] = backtest.get_results()
            
            print(f"\n{name} 回测结果:")
            print(f"  总盈利：{results[symbol]['total_profit']:.2f} 元")
            print(f"  年化收益：{results[symbol]['annual_return']:.2f}%")
            print(f"  胜率：{results[symbol]['win_rate']:.2f}%")
            print(f"  最大回撤：{results[symbol]['max_drawdown']:.2f}%")
        except Exception as e:
            print(f"\n[ERROR] {name} 回测失败：{e}")
            import traceback
            traceback.print_exc()
    
    # 保存结果
    with open('backtest_results_real.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n回测结果已保存到 backtest_results_real.json")
