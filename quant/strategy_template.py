# -*- coding: utf-8 -*-
"""
天勤量化策略模板
================
支持：
- 策略回测
- 模拟交易
- 实盘交易
- 缠论分析集成

作者：咕噜 🐱
"""

from datetime import date, datetime, timedelta
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, TqAccount, TargetPosTask, BacktestFinished
import pandas as pd
import sys

# 导入配置和缠论模块
from config import (
    SHINNY_ACCOUNT, SHINNY_PASSWORD,
    BROKER_NAME, FUTURES_ACCOUNT, FUTURES_PASSWORD,
    BACKTEST_INITIAL_CAPITAL, WATCHLIST, CHAN_THEORY
)
from chan_theory import ChanTheoryAnalyzer


class ChanTheoryStrategy:
    """
    缠论策略框架
    ============
    
    策略逻辑：
    1. 使用缠论识别当前走势结构
    2. 在中枢边界附近寻找买卖点
    3. 结合背驰判断入场时机
    
    可配置参数：
    - symbol: 交易合约
    - kline_interval: K 线周期（秒）
    - backtest_mode: 是否回测模式
    - backtest_start/end: 回测时间范围
    """
    
    def __init__(self, symbol: str, kline_interval: int = 60, 
                 backtest_mode: bool = False,
                 backtest_start: date = None,
                 backtest_end: date = None):
        self.symbol = symbol
        self.kline_interval = kline_interval  # 秒
        self.backtest_mode = backtest_mode
        self.backtest_start = backtest_start or date(2024, 1, 1)
        self.backtest_end = backtest_end or date(2024, 12, 31)
        
        self.api = None
        self.klines = None
        self.analyzer = ChanTheoryAnalyzer(CHAN_THEORY)
        self.target_pos = None
        self.last_trade_time = None
        
        # 策略参数
        self.position_size = 1  # 每次交易手数
        self.stop_loss_pct = 0.02  # 止损 2%
        self.take_profit_pct = 0.05  # 止盈 5%
        
        # 交易记录
        self.trades = []
    
    def init_api(self):
        """初始化 TQSDK API"""
        auth = TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD)
        
        if self.backtest_mode:
            # 回测模式
            print(f"📊 启动回测模式：{self.backtest_start} 至 {self.backtest_end}")
            sim = TqSim(BACKTEST_INITIAL_CAPITAL)
            self.api = TqApi(
                account=sim,
                backtest=TqBacktest(start_dt=self.backtest_start, end_dt=self.backtest_end),
                auth=auth
            )
        else:
            # 实盘模式
            print(f"💰 启动实盘模式：{BROKER_NAME} - {FUTURES_ACCOUNT}")
            account = TqAccount(BROKER_NAME, FUTURES_ACCOUNT, FUTURES_PASSWORD)
            self.api = TqApi(account=account, auth=auth)
        
        # 获取 K 线数据引用
        self.klines = self.api.get_kline_serial(self.symbol, self.kline_interval)
        
        # 创建目标持仓工具
        self.target_pos = TargetPosTask(self.api, self.symbol)
        
        print(f"✅ 初始化完成：{self.symbol}, 周期={self.kline_interval}秒")
    
    def update_chan_analysis(self):
        """更新缠论分析"""
        if self.klines is None or len(self.klines) < 10:
            return None
        
        # 转换为缠论分析器需要的格式
        kline_df = self.klines.copy()
        kline_df = kline_df.rename(columns={
            'datetime': 'datetime',
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })
        
        # 执行分析
        self.analyzer.load_klines(kline_df)
        return self.analyzer.summary()
    
    def generate_signal(self) -> int:
        """
        生成交易信号
        =========
        返回：1=做多，-1=做空，0=观望
        
        策略逻辑（简化版缠论）：
        1. 识别当前笔的方向
        2. 判断是否在中枢内
        3. 检测买卖点
        """
        summary = self.update_chan_analysis()
        if not summary:
            return 0
        
        current_bi = summary.get("current_bi_direction")
        bs_point = summary.get("potential_bs_point")
        zhongshu = summary.get("latest_zhongshu")
        
        # 获取当前价格
        current_price = self.klines.close.iloc[-1]
        
        # 一类买点：买入信号
        if bs_point == "BS1":
            print(f"🟢 一类买点 detected! 价格={current_price}")
            return 1
        
        # 一类卖点：卖出信号
        if bs_point == "SS1":
            print(f"🔴 一类卖点 detected! 价格={current_price}")
            return -1
        
        # 简化策略：向上笔持有多单，向下笔持有空单
        if current_bi == "up":
            return 1
        elif current_bi == "down":
            return -1
        
        return 0
    
    def execute_trade(self, signal: int):
        """执行交易"""
        current_volume = self.api.get_position(self.symbol).volume_long - self.api.get_position(self.symbol).volume_short
        
        if signal == 1:
            # 做多信号
            if current_volume < self.position_size:
                print(f"📈 开多 {self.position_size} 手")
                self.target_pos.set_target_volume(self.position_size)
                self.record_trade("BUY", self.position_size)
        elif signal == -1:
            # 做空信号
            if current_volume > -self.position_size:
                print(f"📉 开空 {self.position_size} 手")
                self.target_pos.set_target_volume(-self.position_size)
                self.record_trade("SELL", -self.position_size)
        elif signal == 0:
            # 平仓信号
            if current_volume != 0:
                print(f"➖ 平仓")
                self.target_pos.set_target_volume(0)
                self.record_trade("CLOSE", 0)
    
    def record_trade(self, action: str, volume: int):
        """记录交易"""
        trade = {
            'time': datetime.now(),
            'symbol': self.symbol,
            'action': action,
            'volume': volume,
            'price': self.klines.close.iloc[-1]
        }
        self.trades.append(trade)
    
    def run_backtest(self):
        """运行回测"""
        print(f"\n🚀 开始回测：{self.symbol}")
        print("=" * 50)
        
        try:
            while True:
                self.api.wait_update()
                
                # 检查是否有新 K 线
                if self.api.is_changing(self.klines):
                    signal = self.generate_signal()
                    self.execute_trade(signal)
                    
                    # 打印当前状态
                    account = self.api.get_account()
                    print(f"📊 资金：{account.balance:.2f}, 可用：{account.available:.2f}")
        
        except BacktestFinished as e:
            # 回测结束
            print("\n" + "=" * 50)
            print("✅ 回测完成!")
            
            # 获取回测统计
            if hasattr(self.api, '_account') and hasattr(self.api._account, 'tqsdk_stat'):
                stats = self.api._account.tqsdk_stat
                print(f"\n📈 回测结果:")
                print(f"  初始资金：{stats.get('init_balance', 0):.2f}")
                print(f"  结束资金：{stats.get('balance', 0):.2f}")
                print(f"  收益率：{stats.get('ror', 0)*100:.2f}%")
                print(f"  最大回撤：{stats.get('max_drawdown', 0):.2f}")
                print(f"  夏普比率：{stats.get('sharpe_ratio', 0):.2f}")
                print(f"  胜率：{stats.get('winning_rate', 0)*100:.2f}%")
            
            # 打印交易记录
            print(f"\n📝 交易记录 ({len(self.trades)}笔):")
            for trade in self.trades:
                print(f"  {trade['time']}: {trade['action']} {abs(trade['volume'])}手 @ {trade['price']:.2f}")
            
            self.api.close()
            return True
    
    def run_live(self):
        """运行实盘/模拟"""
        print(f"\n🚀 开始实盘：{self.symbol}")
        print("=" * 50)
        
        try:
            while True:
                self.api.wait_update()
                
                if self.api.is_changing(self.klines):
                    signal = self.generate_signal()
                    self.execute_trade(signal)
                    
                    # 打印持仓和资金
                    account = self.api.get_account()
                    position = self.api.get_position(self.symbol)
                    print(f"💰 资金：{account.balance:.2f} | 持仓：{position.volume_long - position.volume_short}手")
        
        except KeyboardInterrupt:
            print("\n⛔ 用户中断")
            self.api.close()
        except Exception as e:
            print(f"\n❌ 错误：{e}")
            self.api.close()


# ============ 主程序 ============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="缠论量化策略")
    parser.add_argument("--symbol", type=str, default="KQ.m@SHFE.rb", help="交易合约")
    parser.add_argument("--interval", type=int, default=60, help="K 线周期（秒）")
    parser.add_argument("--backtest", action="store_true", help="启用回测模式")
    parser.add_argument("--start-date", type=str, help="回测开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="回测结束日期 (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    # 解析日期
    start_date = None
    end_date = None
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
    
    # 创建策略实例
    strategy = ChanTheoryStrategy(
        symbol=args.symbol,
        kline_interval=args.interval,
        backtest_mode=args.backtest,
        backtest_start=start_date,
        backtest_end=end_date
    )
    
    # 初始化并运行
    strategy.init_api()
    
    if args.backtest:
        strategy.run_backtest()
    else:
        strategy.run_live()
