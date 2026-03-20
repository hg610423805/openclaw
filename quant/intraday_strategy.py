# -*- coding: utf-8 -*-
"""
日内 5 分钟均线稳定盈利策略
==========================
策略逻辑：
1. 日线 EXPMA5/10/20 发散判断方向
2. 开盘 30 分钟标记高低点
3. 第 7 根 5 分钟 K 线突破开仓
4. 开仓 K 线高低点止损
5. 5 分钟 EXPMA5/13 交叉止盈
6. 14:57 强制平仓
7. 3% 涨跌幅风控

作者：咕噜 🐱
"""

from datetime import date, datetime, time
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished, TargetPosTask
import pandas as pd
import numpy as np

# ============ 配置区 ============
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"

# 回测配置
START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)
INITIAL_CAPITAL = 1000000  # 100 万

# 交易品种（主力合约）
SYMBOLS = [
    "KQ.m@SHFE.rb",   # 螺纹钢
    "KQ.m@DCE.m",     # 豆粕
    "KQ.m@SHFE.cu",   # 铜
    "KQ.m@CFFEX.IF",  # 沪深 300
]

# 策略参数
PARAMS = {
    # 日线 EXPMA 参数
    "daily_expma_fast": 5,
    "daily_expma_mid": 10,
    "daily_expma_slow": 20,
    "expma_divergence_threshold": 0.015,  # 1.5% 间距
    
    # 5 分钟 EXPMA 参数
    "intraday_expma_fast": 5,
    "intraday_expma_slow": 13,
    
    # 时间窗口
    "open_window_bars": 6,  # 30 分钟 = 6 根 5 分钟 K 线
    "entry_bar": 7,  # 第 7 根 K 线开仓
    
    # 风控
    "max_open_range_pct": 0.03,  # 3% 涨跌幅限制
    "force_close_time": "14:57",  # 强制平仓时间
}

# 夜盘品种及时间
NIGHT_TRADING = {
    "KQ.m@SHFE.rb": "21:00",  # 螺纹钢 21:00 开盘
    "KQ.m@DCE.m": "21:00",    # 豆粕 21:00 开盘
    "KQ.m@SHFE.cu": "21:00",  # 铜 21:00 开盘
}
# ===========================


def calc_expma(series, period):
    """计算 EXPMA（指数移动平均）"""
    expma = series.copy()
    alpha = 2.0 / (period + 1)
    for i in range(1, len(expma)):
        expma.iloc[i] = alpha * expma.iloc[i] + (1 - alpha) * expma.iloc[i-1]
    expma.iloc[0] = series.iloc[0]
    return expma


def check_daily_direction(daily_klines, params):
    """
    检查日线方向
    返回：1=多头，-1=空头，0=不符合条件
    """
    if len(daily_klines) < params["daily_expma_slow"]:
        return 0
    
    close = daily_klines['close'].copy()
    
    # 计算 EXPMA
    expma5 = calc_expma(close, params["daily_expma_fast"])
    expma10 = calc_expma(close, params["daily_expma_mid"])
    expma20 = calc_expma(close, params["daily_expma_slow"])
    
    # 获取最新值
    e5 = expma5.iloc[-1]
    e10 = expma10.iloc[-1]
    e20 = expma20.iloc[-1]
    
    # 检查多头排列
    if e5 > e10 > e20:
        # 检查间距
        gap1 = (e5 - e10) / e10
        gap2 = (e10 - e20) / e20
        if gap1 > params["expma_divergence_threshold"] and gap2 > params["expma_divergence_threshold"]:
            return 1  # 多头
    
    # 检查空头排列
    if e5 < e10 < e20:
        gap1 = (e10 - e5) / e10
        gap2 = (e20 - e10) / e20
        if gap1 > params["expma_divergence_threshold"] and gap2 > params["expma_divergence_threshold"]:
            return -1  # 空头
    
    return 0  # 震荡，不交易


def get_trading_session_start(symbol, current_date):
    """获取交易 session 开始时间"""
    if symbol in NIGHT_TRADING:
        # 夜盘品种：返回夜盘开盘时间（实际上是前一天的 21:00）
        return datetime.combine(current_date, time(9, 0))  # 简化：用日盘 9:00
    else:
        return datetime.combine(current_date, time(9, 0))


class IntradayStrategy:
    """日内 5 分钟均线策略"""
    
    def __init__(self, api, symbol, params):
        self.api = api
        self.symbol = symbol
        self.params = params
        
        # 获取日线数据（用于方向判断）
        self.daily_klines = api.get_kline_serial(symbol, 86400)  # 日线
        
        # 获取 5 分钟数据
        self.klines_5m = api.get_kline_serial(symbol, 300)  # 5 分钟
        
        # 状态变量
        self.position = 0  # 持仓：0=空仓，1=多单，-1=空单
        self.entry_price = 0
        self.stop_loss = 0
        self.session_high = None
        self.session_low = None
        self.session_bars = 0
        self.current_direction = 0
        self.last_trade_date = None
        
        # 统计
        self.trades = []
        self.daily_pnl = {}
    
    def get_current_date(self):
        """获取当前交易日"""
        if len(self.klines_5m) == 0:
            return None
        dt = self.klines_5m.datetime.iloc[-1]
        if isinstance(dt, (int, float)):
            dt = pd.to_datetime(dt, unit='ns')
        return dt.date()
    
    def get_current_time(self):
        """获取当前时间"""
        if len(self.klines_5m) == 0:
            return None
        dt = self.klines_5m.datetime.iloc[-1]
        if isinstance(dt, (int, float)):
            dt = pd.to_datetime(dt, unit='ns')
        return dt.time()
    
    def is_trading_session(self):
        """判断是否在交易时段内（不做午盘）"""
        current_time = self.get_current_time()
        if current_time is None:
            return False
        
        # 早盘：9:00-11:30
        if time(9, 0) <= current_time <= time(11, 30):
            return True
        
        # 夜盘：21:00-23:00（简化）
        if time(21, 0) <= current_time <= time(23, 59):
            return True
        
        # 下午不做：13:00-15:00 只在 14:57 前平仓
        return False
    
    def is_force_close_time(self):
        """是否强制平仓时间"""
        current_time = self.get_current_time()
        if current_time is None:
            return False
        
        # 下午 14:57 强制平仓
        if time(14, 57) <= current_time <= time(15, 0):
            return True
        
        return False
    
    def reset_session(self, new_date):
        """重置 session 数据"""
        self.session_high = None
        self.session_low = None
        self.session_bars = 0
        self.last_trade_date = new_date
        
        # 更新日线方向
        self.current_direction = check_daily_direction(self.daily_klines, self.params)
        print(f"[{self.symbol}] {new_date} 日线方向：{'多' if self.current_direction == 1 else '空' if self.current_direction == -1 else '震荡'}")
    
    def check_open_range(self, high, low, open_price):
        """检查开盘 30 分钟涨跌幅是否超过阈值"""
        range_pct = (high - low) / open_price
        return range_pct <= self.params["max_open_range_pct"]
    
    def calc_entry_signal(self):
        """
        计算开仓信号
        返回：1=做多，-1=做空，0=观望
        """
        if self.session_bars < self.params["entry_bar"]:
            return 0
        
        if len(self.klines_5m) < self.params["entry_bar"]:
            return 0
        
        # 获取第 7 根 K 线（相对于 session 开始）
        session_start_idx = len(self.klines_5m) - self.session_bars
        if session_start_idx < 0:
            return 0
        
        entry_bar_idx = session_start_idx + self.params["entry_bar"] - 1
        if entry_bar_idx >= len(self.klines_5m):
            return 0
        
        entry_kline = self.klines_5m.iloc[entry_bar_idx]
        entry_close = entry_kline['close']
        entry_high = entry_kline['high']
        entry_low = entry_kline['low']
        
        # 检查突破
        if self.current_direction == 1:
            # 多头：突破高点做多
            if entry_close > self.session_high:
                if self.check_open_range(self.session_high, self.session_low, self.klines_5m.iloc[session_start_idx]['open']):
                    self.stop_loss = entry_low  # 止损设在第 7 根 K 线低点
                    return 1
        
        elif self.current_direction == -1:
            # 空头：突破低点做空
            if entry_close < self.session_low:
                if self.check_open_range(self.session_high, self.session_low, self.klines_5m.iloc[session_start_idx]['open']):
                    self.stop_loss = entry_high  # 止损设在第 7 根 K 线高点
                    return -1
        
        return 0
    
    def check_exit_signal(self):
        """
        检查止盈信号（5 分钟 EXPMA5/13 交叉）
        返回：True=平仓，False=持有
        """
        if len(self.klines_5m) < self.params["intraday_expma_slow"] + 5:
            return False
        
        close = self.klines_5m['close'].copy()
        
        # 计算 EXPMA
        expma5 = calc_expma(close, self.params["intraday_expma_fast"])
        expma13 = calc_expma(close, self.params["intraday_expma_slow"])
        
        # 检查交叉
        curr_e5 = expma5.iloc[-1]
        curr_e13 = expma13.iloc[-1]
        prev_e5 = expma5.iloc[-2]
        prev_e13 = expma13.iloc[-2]
        
        if self.position == 1:
            # 多单：死叉平仓（5 下穿 13）
            if prev_e5 >= prev_e13 and curr_e5 < curr_e13:
                print(f"[{self.symbol}] EXPMA 死叉平仓")
                return True
        
        elif self.position == -1:
            # 空单：金叉平仓（5 上穿 13）
            if prev_e5 <= prev_e13 and curr_e5 > curr_e13:
                print(f"[{self.symbol}] EXPMA 金叉平仓")
                return True
        
        return False
    
    def check_stop_loss(self, current_price):
        """检查止损"""
        if self.position == 1:
            # 多单：跌破止损
            if current_price <= self.stop_loss:
                print(f"[{self.symbol}] 触发止损 (多单)")
                return True
        
        elif self.position == -1:
            # 空单：突破止损
            if current_price >= self.stop_loss:
                print(f"[{self.symbol}] 触发止损 (空单)")
                return True
        
        return False
    
    def run(self):
        """运行策略"""
        print(f"\n{'='*60}")
        print(f"策略启动：{self.symbol}")
        print(f"回测时间：{START_DATE} 至 {END_DATE}")
        print(f"{'='*60}")
        
        target_pos = TargetPosTask(self.api, self.symbol)
        
        try:
            while True:
                self.api.wait_update()
                
                if self.api.is_changing(self.klines_5m):
                    current_date = self.get_current_date()
                    
                    # 检查是否新交易日
                    if current_date != self.last_trade_date:
                        self.reset_session(current_date)
                        continue
                    
                    # 检查是否在交易时段
                    if not self.is_trading_session():
                        # 检查强制平仓时间
                        if self.is_force_close_time() and self.position != 0:
                            print(f"[{self.symbol}] 强制平仓 (日内)")
                            target_pos.set_target_volume(0)
                            self.record_trade("FORCE_CLOSE", self.klines_5m.close.iloc[-1])
                            self.position = 0
                        continue
                    
                    current_price = self.klines_5m.close.iloc[-1]
                    current_high = self.klines_5m.high.iloc[-1]
                    current_low = self.klines_5m.low.iloc[-1]
                    
                    # 更新 session 高低点（前 6 根 K 线）
                    if self.session_bars < self.params["open_window_bars"]:
                        if self.session_high is None:
                            self.session_high = current_high
                            self.session_low = current_low
                        else:
                            self.session_high = max(self.session_high, current_high)
                            self.session_low = min(self.session_low, current_low)
                        self.session_bars += 1
                        continue
                    
                    # 已有持仓：检查出场
                    if self.position != 0:
                        # 检查止损
                        if self.check_stop_loss(current_price):
                            target_pos.set_target_volume(0)
                            self.record_trade("STOP_LOSS", current_price)
                            self.position = 0
                            continue
                        
                        # 检查止盈
                        if self.check_exit_signal():
                            target_pos.set_target_volume(0)
                            self.record_trade("TAKE_PROFIT", current_price)
                            self.position = 0
                            continue
                        
                        # 检查强制平仓
                        if self.is_force_close_time():
                            target_pos.set_target_volume(0)
                            self.record_trade("FORCE_CLOSE", current_price)
                            self.position = 0
                            continue
                    
                    # 空仓：检查开仓
                    else:
                        signal = self.calc_entry_signal()
                        if signal != 0:
                            if signal == 1:
                                print(f"[{self.symbol}] 开多 @ {current_price:.2f}, 止损={self.stop_loss:.2f}")
                                target_pos.set_target_volume(1)
                                self.entry_price = current_price
                                self.position = 1
                                self.record_trade("BUY", current_price)
                            
                            elif signal == -1:
                                print(f"[{self.symbol}] 开空 @ {current_price:.2f}, 止损={self.stop_loss:.2f}")
                                target_pos.set_target_volume(-1)
                                self.entry_price = current_price
                                self.position = -1
                                self.record_trade("SELL", current_price)
        
        except BacktestFinished:
            print(f"\n{'='*60}")
            print(f"[{self.symbol}] 回测完成！")
            
            stats = self.api._account.tqsdk_stat if hasattr(self.api._account, 'tqsdk_stat') else {}
            print(f"交易次数：{len(self.trades)}")
            
            return self.trades
    
    def record_trade(self, action, price):
        """记录交易"""
        trade = {
            'date': self.get_current_date(),
            'time': self.get_current_time(),
            'symbol': self.symbol,
            'action': action,
            'price': price,
            'position': self.position
        }
        self.trades.append(trade)


# ============ 主程序 ============
if __name__ == "__main__":
    print("=" * 60)
    print("日内 5 分钟均线策略 - 多品种回测")
    print("=" * 60)
    
    try:
        auth = TqAuth(ACCOUNT, PASSWORD)
        sim = TqSim(INITIAL_CAPITAL)
        
        api = TqApi(
            account=sim,
            backtest=TqBacktest(start_dt=START_DATE, end_dt=END_DATE),
            auth=auth
        )
        
        all_trades = {}
        
        for symbol in SYMBOLS:
            print(f"\n>>> 开始回测：{symbol}")
            strategy = IntradayStrategy(api, symbol, PARAMS)
            trades = strategy.run()
            all_trades[symbol] = trades
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("回测汇总")
        print("=" * 60)
        
        stats = sim.tqsdk_stat
        print(f"初始资金：  {stats.get('init_balance', 0):,.2f} 元")
        print(f"结束资金：  {stats.get('balance', 0):,.2f} 元")
        print(f"收益率：    {stats.get('ror', 0)*100:.2f}%")
        print(f"最大回撤：  {stats.get('max_drawdown', 0):,.2f} 元")
        print(f"夏普比率：  {stats.get('sharpe_ratio', 0):.2f}")
        
        print(f"\n各品种交易次数:")
        for symbol, trades in all_trades.items():
            print(f"  {symbol}: {len(trades)} 笔")
        
        api.close()
        
    except Exception as e:
        print(f"\n错误：{e}")
        import traceback
        traceback.print_exc()
