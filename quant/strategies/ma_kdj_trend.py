# -*- coding: utf-8 -*-
"""
均线 + KDJ 趋势跟踪策略
- 30 分钟定方向，5 分钟入场
- EXPMA13/26 + KDJ(J 值)
- 分型止损 + 移动止损
- 自动移仓换月
"""

from tqsdk import TqApi, TqAuth, TargetPosTask
from tqsdk.indicators import MA, KDJ
from tqsdk.ta import EXPMA
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# ============== 配置 ==============
class Config:
    SYMBOL = "SHFE.rb2505"  # 主力合约（需动态获取）
    INITIAL_CAPITAL = 100000  # 初始资金 10 万
    MAX_POSITION_RATIO = 0.5  # 最大仓位 50%
    MAX_DAILY_TRADES = 3  # 每日最多交易 3 次
    CONTRACT_ROLL_DAYS = 10  # 到期前 10 天移仓
    
    # 指标参数
    EXPMA_FAST = 13
    EXPMA_SLOW = 26
    KDJ_PERIOD = 9
    
    # K 线周期
    MONITOR_INTERVAL = "30"  # 30 分钟定方向
    TRADE_INTERVAL = "5"     # 5 分钟交易
    
    # Tick 值（不同品种不同，需配置）
    TICK_SIZE = 1  # 螺纹钢 1 元/吨


# ============== 分型识别 ==============
class FractalDetector:
    """分型检测器"""
    
    def __init__(self, window: int = 5):
        self.window = window
        self.bull_fractals: List[Dict] = []  # 底分型
        self.bear_fractals: List[Dict] = []  # 顶分型
    
    def detect_bull_fractal(self, klines: List[Dict], current_idx: int) -> Optional[float]:
        """检测底分型（中间 K 线最低点最低）"""
        if current_idx < 2:
            return None
        
        current_low = klines[current_idx]['low']
        prev_low = klines[current_idx - 1]['low']
        prev2_low = klines[current_idx - 2]['low']
        
        if prev_low < prev2_low and prev_low < current_low:
            return prev_low
        return None
    
    def detect_bear_fractal(self, klines: List[Dict], current_idx: int) -> Optional[float]:
        """检测顶分型（中间 K 线最高点最高）"""
        if current_idx < 2:
            return None
        
        current_high = klines[current_idx]['high']
        prev_high = klines[current_idx - 1]['high']
        prev2_high = klines[current_idx - 2]['high']
        
        if prev_high > prev2_high and prev_high > current_high:
            return prev_high
        return None


# ============== 策略主类 ==============
class MA_KDJ_TrendStrategy:
    """均线+KDJ 趋势跟踪策略"""
    
    def __init__(self, api: TqApi, symbol: str):
        self.api = api
        self.symbol = symbol
        self.config = Config()
        
        # 账户信息
        self.account = api.get_account()
        self.initial_capital = self.config.INITIAL_CAPITAL
        self.daily_trades = 0
        self.last_trade_date = None
        
        # 目标持仓
        self.target_pos = TargetPosTask(api, symbol)
        
        # K 线数据
        self.kline_30 = api.get_kline_serial(symbol, 200, duration_seconds=1800)  # 30 分钟
        self.kline_5 = api.get_kline_serial(symbol, 200, duration_seconds=300)    # 5 分钟
        
        # 指标计算
        self.expma13_30 = EXPMA(self.kline_30['close'], self.config.EXPMA_FAST)
        self.expma26_30 = EXPMA(self.kline_30['close'], self.config.EXPMA_SLOW)
        self.kdj_30 = KDJ(self.kline_30, self.config.KDJ_PERIOD)
        
        self.expma13_5 = EXPMA(self.kline_5['close'], self.config.EXPMA_FAST)
        self.expma26_5 = EXPMA(self.kline_5['close'], self.config.EXPMA_SLOW)
        self.kdj_5 = KDJ(self.kline_5, self.config.KDJ_PERIOD)
        
        # 分型检测
        self.fractal_detector = FractalDetector()
        
        # 持仓状态
        self.position = 0  # 正数多仓，负数空仓
        self.entry_price = 0
        self.stop_loss_price = 0
        self.last_bull_fractal_low = None  # 最后一个底分型低点
        self.last_bear_fractal_high = None  # 最后一个顶分型高点
        
        # 移仓信息
        self.current_contract = symbol
        self.next_contract = None
    
    def get_current_position(self) -> int:
        """获取当前持仓"""
        positions = self.api.get_position(self.symbol)
        return positions['volume_long'] - positions['volume_short'] if positions else 0
    
    def get_available_capital(self) -> float:
        """获取可用资金"""
        self.account = self.api.get_account()
        return self.account.balance
    
    def calculate_position_size(self, price: float) -> int:
        """计算开仓手数（不超过 50% 仓位）"""
        available = self.get_available_capital() * self.config.MAX_POSITION_RATIO
        contract_unit = 10  # 螺纹钢 10 吨/手，需根据品种调整
        hands = int(available / (price * contract_unit))
        return max(0, hands)
    
    def get_main_contract(self, exchange: str, variety: str) -> str:
        """获取主力合约"""
        # 简化实现：实际需查询交易所主力合约映射
        # 这里返回示例合约
        return f"{exchange}.{variety}2505"
    
    def check_contract_roll(self) -> bool:
        """检查是否需要移仓换月"""
        # 获取合约到期日（简化：假设每月 15 日到期）
        contract_month = int(self.current_contract[-2:])
        current_day = datetime.now().day
        
        if current_day >= (15 - self.config.CONTRACT_ROLL_DAYS):
            # 需要移仓
            next_month = contract_month + 1 if contract_month < 12 else 1
            next_year = int(self.current_contract[-4:-2])
            if next_month > 12:
                next_year += 1
                next_month = 1
            self.next_contract = f"{self.current_contract[:-4]}{next_year:02d}{next_month:02d}"
            return True
        return False
    
    def force_close_position(self):
        """强制平仓（移仓时）"""
        self.target_pos.set_target_volume(0)
        self.position = 0
        self.entry_price = 0
        self.stop_loss_price = 0
        print(f"[移仓] 已平仓 {self.current_contract}")
    
    def get_j_value(self, kdj_series) -> float:
        """获取最新 KDJ 的 J 值"""
        return kdj_series.iloc[-1] if len(kdj_series) > 0 else 50
    
    def is_bullish_trend_30(self) -> bool:
        """30 分钟级别多头趋势"""
        return self.expma13_30.iloc[-1] > self.expma26_30.iloc[-1]
    
    def is_bearish_trend_30(self) -> bool:
        """30 分钟级别空头趋势"""
        return self.expma13_30.iloc[-1] < self.expma26_30.iloc[-1]
    
    def check_long_entry_condition1(self) -> bool:
        """做多方式 1 条件检查"""
        # 30 分钟 J 值<20
        j_30 = self.get_j_value(self.kdj_30['j'])
        if j_30 >= 20:
            return False
        
        # 30 分钟 EXPMA13>EXPMA26
        if not self.is_bullish_trend_30():
            return False
        
        # 5 分钟 EXPMA13>EXPMA26
        if self.expma13_5.iloc[-1] <= self.expma26_5.iloc[-1]:
            return False
        
        # 5 分钟 J 值<20
        j_5 = self.get_j_value(self.kdj_5['j'])
        if j_5 >= 20:
            return False
        
        # 当前 K 线倒数 7 秒最低点 > 上一根 K 线最低点
        if len(self.kline_5) < 2:
            return False
        
        current_low = self.kline_5.iloc[-1]['low']
        prev_low = self.kline_5.iloc[-2]['low']
        if current_low <= prev_low:
            return False
        
        return True
    
    def check_long_entry_condition2(self) -> bool:
        """做多方式 2 条件检查（金叉入场）"""
        # 30 分钟 J 值<20
        j_30 = self.get_j_value(self.kdj_30['j'])
        if j_30 >= 20:
            return False
        
        # 30 分钟 EXPMA13>EXPMA26
        if not self.is_bullish_trend_30():
            return False
        
        # 检查 5 分钟金叉
        if len(self.expma13_5) < 2 or len(self.expma26_5) < 2:
            return False
        
        # 之前死叉，现在金叉
        prev_diff = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr_diff = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        
        if prev_diff <= 0 and curr_diff > 0:
            return True
        
        return False
    
    def check_short_entry_condition1(self) -> bool:
        """做空方式 1 条件检查"""
        # 【规则 9】做空开仓条件：30 分钟 J 值>80
        j_30 = self.get_j_value(self.kdj_30['j'])
        if j_30 <= 80:
            return False
        
        # 【规则 9】做空开仓条件：30 分钟 EXPMA13<EXPMA26
        if not self.is_bearish_trend_30():
            return False
        
        # 【规则 10-1】5 分钟 EXPMA13<EXPMA26
        if self.expma13_5.iloc[-1] >= self.expma26_5.iloc[-1]:
            return False
        
        # 【规则 10-1】5 分钟 J 值>80
        j_5 = self.get_j_value(self.kdj_5['j'])
        if j_5 <= 80:
            return False
        
        # 【规则 10-1】当前 K 线倒数 7 秒最高点 < 上一根 K 线最高点
        if len(self.kline_5) < 2:
            return False
        
        current_high = self.kline_5.iloc[-1]['high']
        prev_high = self.kline_5.iloc[-2]['high']
        if current_high >= prev_high:
            return False
        
        return True
    
    def check_short_entry_condition2(self) -> bool:
        """做空方式 2 条件检查（死叉入场）"""
        # 【规则 9】做空开仓条件：30 分钟 J 值>80
        j_30 = self.get_j_value(self.kdj_30['j'])
        if j_30 <= 80:
            return False
        
        # 【规则 9】做空开仓条件：30 分钟 EXPMA13<EXPMA26
        if not self.is_bearish_trend_30():
            return False
        
        # 【规则 10-2】检查 5 分钟死叉
        if len(self.expma13_5) < 2 or len(self.expma26_5) < 2:
            return False
        
        # 之前金叉，现在死叉
        prev_diff = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr_diff = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        
        if prev_diff >= 0 and curr_diff < 0:
            return True
        
        return False
    
    def open_long_position(self, entry_type: int):
        """开多仓"""
        if self.daily_trades >= self.config.MAX_DAILY_TRADES:
            print("[交易限制] 今日已达最大交易次数")
            return
        
        current_price = self.kline_5.iloc[-1]['close']
        hands = self.calculate_position_size(current_price)
        
        if hands <= 0:
            print("[开仓] 可用资金不足")
            return
        
        self.target_pos.set_target_volume(hands)
        self.position = hands
        self.entry_price = current_price
        self.daily_trades += 1
        
        # 设置初始止损
        if entry_type == 1:
            # 方式 1：前一根 K 线最低点 - 1 tick
            prev_low = self.kline_5.iloc[-2]['low']
            self.stop_loss_price = prev_low - self.config.TICK_SIZE
        else:
            # 方式 2：底分型最低点
            self.stop_loss_price = self.last_bull_fractal_low or (current_price * 0.98)
        
        print(f"[开多] {hands}手 @ {current_price}, 止损={self.stop_loss_price}")
    
    def open_short_position(self, entry_type: int):
        """开空仓"""
        if self.daily_trades >= self.config.MAX_DAILY_TRADES:
            print("[交易限制] 今日已达最大交易次数")
            return
        
        current_price = self.kline_5.iloc[-1]['close']
        hands = self.calculate_position_size(current_price)
        
        if hands <= 0:
            print("[开仓] 可用资金不足")
            return
        
        self.target_pos.set_target_volume(-hands)
        self.position = -hands
        self.entry_price = current_price
        self.daily_trades += 1
        
        # 设置初始止损
        if entry_type == 1:
            # 方式 1：前一根 K 线最高点 + 1 tick
            prev_high = self.kline_5.iloc[-2]['high']
            self.stop_loss_price = prev_high + self.config.TICK_SIZE
        else:
            # 方式 2：顶分型最高点
            self.stop_loss_price = self.last_bear_fractal_high or (current_price * 1.02)
        
        print(f"[开空] {hands}手 @ {current_price}, 止损={self.stop_loss_price}")
    
    def update_trailing_stop_long(self):
        """更新多仓移动止损"""
        current_price = self.kline_5.iloc[-1]['close']
        
        # 检测新的底分型
        bull_fractal = self.fractal_detector.detect_bull_fractal(
            self.kline_5.to_dict('records'), 
            len(self.kline_5) - 1
        )
        
        if bull_fractal:
            if self.last_bull_fractal_low is None or bull_fractal > self.last_bull_fractal_low:
                self.last_bull_fractal_low = bull_fractal
                new_stop = bull_fractal - self.config.TICK_SIZE
                
                if new_stop > self.stop_loss_price:
                    self.stop_loss_price = new_stop
                    print(f"[移动止损] 多仓止损上移至 {self.stop_loss_price}")
    
    def update_trailing_stop_short(self):
        """更新空仓移动止损"""
        current_price = self.kline_5.iloc[-1]['close']
        
        # 检测新的顶分型
        bear_fractal = self.fractal_detector.detect_bear_fractal(
            self.kline_5.to_dict('records'), 
            len(self.kline_5) - 1
        )
        
        if bear_fractal:
            if self.last_bear_fractal_high is None or bear_fractal < self.last_bear_fractal_high:
                self.last_bear_fractal_high = bear_fractal
                new_stop = bear_fractal + self.config.TICK_SIZE
                
                if new_stop < self.stop_loss_price:
                    self.stop_loss_price = new_stop
                    print(f"[移动止损] 空仓止损下移至 {self.stop_loss_price}")
    
    def check_stop_loss_long(self, current_price: float) -> bool:
        """检查多仓止损"""
        if current_price <= self.stop_loss_price:
            print(f"[止损] 多仓触发 @ {current_price}")
            self.target_pos.set_target_volume(0)
            self.position = 0
            self.stop_loss_price = 0
            self.last_bull_fractal_low = None
            return True
        return False
    
    def check_stop_loss_short(self, current_price: float) -> bool:
        """检查空仓止损"""
        if current_price >= self.stop_loss_price:
            print(f"[止损] 空仓触发 @ {current_price}")
            self.target_pos.set_target_volume(0)
            self.position = 0
            self.stop_loss_price = 0
            self.last_bear_fractal_high = None
            return True
        return False
    
    def check_take_profit_long(self) -> bool:
        """检查多仓止盈（死叉平仓）"""
        if len(self.expma13_5) < 2 or len(self.expma26_5) < 2:
            return False
        
        prev_diff = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr_diff = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        
        if prev_diff > 0 and curr_diff <= 0:
            current_price = self.kline_5.iloc[-1]['close']
            profit = (current_price - self.entry_price) * self.position * 10
            print(f"[止盈] 多仓死叉平仓 @ {current_price}, 盈亏={profit:.2f}")
            self.target_pos.set_target_volume(0)
            self.position = 0
            self.stop_loss_price = 0
            self.last_bull_fractal_low = None
            return True
        return False
    
    def check_take_profit_short(self) -> bool:
        """检查空仓止盈（金叉平仓）"""
        if len(self.expma13_5) < 2 or len(self.expma26_5) < 2:
            return False
        
        prev_diff = self.expma13_5.iloc[-2] - self.expma26_5.iloc[-2]
        curr_diff = self.expma13_5.iloc[-1] - self.expma26_5.iloc[-1]
        
        if prev_diff < 0 and curr_diff >= 0:
            current_price = self.kline_5.iloc[-1]['close']
            profit = (self.entry_price - current_price) * abs(self.position) * 10
            print(f"[止盈] 空仓金叉平仓 @ {current_price}, 盈亏={profit:.2f}")
            self.target_pos.set_target_volume(0)
            self.position = 0
            self.stop_loss_price = 0
            self.last_bear_fractal_high = None
            return True
        return False
    
    def reset_daily_trades(self):
        """重置每日交易次数"""
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
            print(f"[新交易日] 今日交易次数重置为 0")
    
    def run(self):
        """策略主循环"""
        print(f"[策略启动] {self.symbol}")
        print(f"初始资金：{self.initial_capital}")
        
        while True:
            api.wait_update()
            
            # 重置每日交易次数
            self.reset_daily_trades()
            
            # 检查移仓
            if self.check_contract_roll() and self.position != 0:
                self.force_close_position()
                self.current_contract = self.next_contract
                self.target_pos = TargetPosTask(api, self.current_contract)
                continue
            
            current_price = self.kline_5.iloc[-1]['close']
            
            # 持仓管理
            if self.position > 0:
                # 多仓
                if not self.check_stop_loss_long(current_price):
                    self.update_trailing_stop_long()
                    self.check_take_profit_long()
            
            elif self.position < 0:
                # 空仓
                if not self.check_stop_loss_short(current_price):
                    self.update_trailing_stop_short()
                    self.check_take_profit_short()
            
            else:
                # 无持仓，检查开仓
                if self.is_bullish_trend_30():
                    # 多头趋势
                    if self.check_long_entry_condition1():
                        self.open_long_position(1)
                    elif self.check_long_entry_condition2():
                        self.open_long_position(2)
                
                elif self.is_bearish_trend_30():
                    # 空头趋势
                    if self.check_short_entry_condition1():
                        self.open_short_position(1)
                    elif self.check_short_entry_condition2():
                        self.open_short_position(2)


# ============== 主程序 ==============
if __name__ == "__main__":
    # 配置 TQSDK 认证（从 config.py 读取）
    import sys
    sys.path.insert(0, '..')
    from config import SHINNY_ACCOUNT, SHINNY_PASSWORD
    
    auth = TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD)
    
    # 创建 API 实例
    api = TqApi(auth=auth)
    
    # 获取主力合约（示例：螺纹钢）
    # 实际使用时需要根据品种动态获取主力合约
    symbol = "SHFE.rb2505"
    
    # 创建并运行策略
    strategy = MA_KDJ_TrendStrategy(api, symbol)
    strategy.run()
