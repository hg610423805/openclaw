# -*- coding: utf-8 -*-
"""
EXPMA 双向策略回测 - 硅铁 & 锰硅（简化版，不依赖 TqApi 实时连接）
回测周期：2025-03-22 至 2026-03-22（1 年）
使用本地数据或模拟数据生成回测报告
"""

import datetime
import json
import random
import numpy as np
import pandas as pd

def generate_mock_data(symbol, start_date, end_date):
    """生成模拟 K 线数据用于回测演示"""
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    
    # 基础价格
    base_price = 8000 if 'SF' in symbol else 7500  # 硅铁约 8000，锰硅约 7500
    
    # 生成日线数据
    daily_data = []
    curr_price = base_price
    curr_date = start
    
    while curr_date <= end:
        # 跳过周末
        if curr_date.weekday() < 5:
            change = random.uniform(-0.02, 0.02)
            open_price = curr_price
            close_price = curr_price * (1 + change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.01))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.01))
            
            daily_data.append({
                'datetime': curr_date.timestamp() * 1e9,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': random.randint(1000, 10000)
            })
            
            curr_price = close_price
        
        curr_date += datetime.timedelta(days=1)
    
    # 生成 5 分钟数据（简化：每根日线生成 48 根 5 分钟 K 线）
    five_min_data = []
    for day in daily_data:
        day_date = datetime.datetime.fromtimestamp(day['datetime'] / 1e9)
        open_price = day['open']
        close_price = day['close']
        high_price = day['high']
        low_price = day['low']
        
        # 简单模拟日内波动
        for i in range(48):
            time_offset = i * 300  # 5 分钟
            progress = i / 48
            curr_open = open_price + (close_price - open_price) * progress
            change = random.uniform(-0.005, 0.005)
            curr_close = curr_open * (1 + change)
            
            five_min_data.append({
                'datetime': (day_date + datetime.timedelta(minutes=i*5)).timestamp() * 1e9,
                'open': curr_open,
                'high': max(curr_open, curr_close) * (1 + random.uniform(0, 0.002)),
                'low': min(curr_open, curr_close) * (1 - random.uniform(0, 0.002)),
                'close': curr_close,
                'volume': random.randint(50, 500)
            })
    
    return pd.DataFrame(daily_data), pd.DataFrame(five_min_data)

def expma(series, period):
    """EXPMA 指标"""
    return series.ewm(span=period, adjust=False).mean()

class EXPMA_Backtest:
    def __init__(self, symbol, start_date, end_date, initial_capital=100000):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.initial_capital = initial_capital
        
        print(f"[{datetime.datetime.now()}] 正在生成 {symbol} 模拟数据...")
        self.klines_daily, self.klines_5m = generate_mock_data(symbol, start_date, end_date)
        print(f"[{datetime.datetime.now()}] 数据生成完成 - 日线：{len(self.klines_daily)}条，5 分钟：{len(self.klines_5m)}条")
        
        self.expma5_d = expma(self.klines_daily['close'], 5)
        self.expma10_d = expma(self.klines_daily['close'], 10)
        self.expma20_d = expma(self.klines_daily['close'], 20)
        
        self.expma5_5m = expma(self.klines_5m['close'], 5)
        self.expma10_5m = expma(self.klines_5m['close'], 10)
        
        self.trades = []
        self.capital_curve = []
        self.capital = initial_capital
        self.position = 0
        self.entry_price = 0
        self.entry_bar_low = 0
        self.entry_bar_high = 0
        
        self.total_profit = 0
        self.win_count = 0
        self.loss_count = 0
        self.max_drawdown = 0
        self.peak_capital = initial_capital
        self.total_trades = 0
    
    def check_daily_trend(self, idx):
        if idx < 20 or idx >= len(self.expma5_d):
            return 0
        
        e5 = self.expma5_d.iloc[idx]
        e10 = self.expma10_d.iloc[idx]
        e20 = self.expma20_d.iloc[idx]
        e5_prev = self.expma5_d.iloc[idx-1]
        e10_prev = self.expma10_d.iloc[idx-1]
        
        if (e5 > e10 > e20) and (e5 > e5_prev) and (e10 > e10_prev):
            return 1
        if (e5 < e10 < e20) and (e5 < e5_prev) and (e10 < e10_prev):
            return -1
        return 0
    
    def get_6bar_range(self, idx):
        if idx < 7:
            return None, None
        
        recent = self.klines_5m.iloc[idx-7:idx-1]
        high = recent['highest'] if 'highest' in recent.columns else recent['high'].max()
        low = recent['lowest'] if 'lowest' in recent.columns else recent['low'].min()
        return high, low
    
    def check_cross(self, idx):
        if idx < 2 or idx >= len(self.expma5_5m):
            return 0
        
        e5_curr = self.expma5_5m.iloc[idx]
        e10_curr = self.expma10_5m.iloc[idx]
        e5_prev = self.expma5_5m.iloc[idx-1]
        e10_prev = self.expma10_5m.iloc[idx-1]
        
        if e5_prev > e10_prev and e5_curr < e10_curr:
            return -1
        if e5_prev < e10_prev and e5_curr > e10_curr:
            return 1
        return 0
    
    def run_backtest(self):
        print(f"[{datetime.datetime.now()}] 开始回测...")
        
        for i in range(10, len(self.klines_5m)):
            curr_kline = self.klines_5m.iloc[i]
            curr_time = datetime.datetime.fromtimestamp(curr_kline['datetime'] / 1e9)
            curr_price = curr_kline['close']
            
            # 添加 highest/lowest 字段
            if 'highest' not in curr_kline:
                curr_kline = curr_kline.copy()
                curr_kline['highest'] = curr_kline['high']
                curr_kline['lowest'] = curr_kline['low']
            
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
            
            if trend == 1:
                if self.position == 0 and curr_price > range_high:
                    self.position = 1
                    self.entry_price = curr_price
                    self.entry_bar_low = float(curr_kline['lowest'])
                    self.trades.append({
                        'open_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '开仓',
                        'direction': '多',
                        'price': float(curr_price),
                        'capital': float(self.capital),
                        'reason': f'突破前 6 根 K 线高点 {range_high:.2f}'
                    })
                
                elif self.position == 1:
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
            
            elif trend == -1:
                if self.position == 0 and curr_price < range_low:
                    self.position = -1
                    self.entry_price = curr_price
                    self.entry_bar_high = float(curr_kline['highest'])
                    self.trades.append({
                        'open_time': curr_time.strftime("%Y-%m-%d %H:%M"),
                        'type': '开仓',
                        'direction': '空',
                        'price': float(curr_price),
                        'capital': float(self.capital),
                        'reason': f'跌破前 6 根 K 线低点 {range_low:.2f}'
                    })
                
                elif self.position == -1:
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
            
            self.capital_curve.append({
                'time': curr_time.strftime("%Y-%m-%d"),
                'capital': float(self.capital)
            })
            
            if self.capital > self.peak_capital:
                self.peak_capital = self.capital
            drawdown = (self.peak_capital - self.capital) / self.peak_capital
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown
        
        self.calculate_stats()
        print(f"[{datetime.datetime.now()}] 回测完成！")
    
    def calculate_stats(self):
        self.total_profit = self.capital - self.initial_capital
        
        closed_trades = [t for t in self.trades if t.get('profit') is not None]
        self.win_count = len([t for t in closed_trades if t['profit'] > 0])
        self.loss_count = len([t for t in closed_trades if t['profit'] <= 0])
        self.total_trades = len(closed_trades)
        self.win_rate = self.win_count / self.total_trades * 100 if self.total_trades > 0 else 0
        
        days = (datetime.datetime.strptime(self.end_date, "%Y-%m-%d") - 
                datetime.datetime.strptime(self.start_date, "%Y-%m-%d")).days
        self.annual_return = (self.total_profit / self.initial_capital) * (365 / days) * 100 if days > 0 else 0
        
        self.monthly_pnl = {}
        for t in closed_trades:
            month = t['close_time'][:7]
            self.monthly_pnl[month] = self.monthly_pnl.get(month, 0) + t.get('profit', 0)
    
    def get_results(self):
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
            'capital_curve': self.capital_curve
        }


if __name__ == "__main__":
    START_DATE = "2025-03-22"
    END_DATE = "2026-03-22"
    INITIAL_CAPITAL = 100000
    
    SYMBOLS = [
        ("CZCE.SF000", "硅铁主力连续"),
        ("CZCE.SM000", "锰硅主力连续")
    ]
    
    results = {}
    
    for symbol, name in SYMBOLS:
        print(f"\n{'='*60}")
        print(f"开始回测：{name} ({symbol})")
        print(f"{'='*60}\n")
        
        backtest = EXPMA_Backtest(symbol, START_DATE, END_DATE, INITIAL_CAPITAL)
        backtest.run_backtest()
        results[symbol] = backtest.get_results()
        
        print(f"\n{name} 回测结果:")
        print(f"  总盈利：{results[symbol]['total_profit']:.2f} 元")
        print(f"  年化收益：{results[symbol]['annual_return']:.2f}%")
        print(f"  胜率：{results[symbol]['win_rate']:.2f}%")
        print(f"  最大回撤：{results[symbol]['max_drawdown']:.2f}%")
    
    with open('backtest_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n回测结果已保存到 backtest_results.json")
