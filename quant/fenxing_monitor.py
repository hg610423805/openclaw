# -*- coding: utf-8 -*-
"""
分型实时监控
============
基于缠论分型判断，实时监控期货/股票品种
用法：python fenxing_monitor.py --symbol rb2505 --interval 5
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import datetime
import time
from typing import Optional, Dict
import pandas as pd

from chan_theory import ChanTheoryAnalyzer, Fractal


def fetch_kline_data(symbol: str, interval: int, limit: int = 100) -> pd.DataFrame:
    """
    获取 K 线数据
    
    支持数据源：
    1. Tushare (股票/期货)
    2. AkShare (免费)
    3. 本地 CSV 缓存
    
    Parameters
    ----------
    symbol : str
        品种代码，如 rb2505, IF2403, 600519.SH
    interval : int
        分钟周期：1, 5, 15, 30, 60
    limit : int
        获取 K 线数量
    
    Returns
    -------
    pd.DataFrame
        K 线数据：datetime, open, high, low, close, volume
    """
    # TODO: 根据实际需求接入数据源
    # 这里用模拟数据演示
    print(f"[数据] 获取 {symbol} {interval}分钟 K 线 x{limit} 条")
    
    import numpy as np
    data = []
    base_price = 3500 + np.random.randn() * 100
    
    for i in range(limit):
        dt = datetime.datetime.now() - datetime.timedelta(minutes=(limit - i) * interval)
        open_price = base_price + np.random.randn() * 5
        high_price = max(open_price, base_price) + abs(np.random.randn() * 8)
        low_price = min(open_price, base_price) - abs(np.random.randn() * 8)
        close_price = base_price + np.random.randn() * 5
        base_price = close_price
        
        data.append({
            'datetime': dt,
            'open': round(open_price, 2),
            'high': round(high_price, 2),
            'low': round(low_price, 2),
            'close': round(close_price, 2),
            'volume': int(np.random.rand() * 10000)
        })
    
    return pd.DataFrame(data)


def analyze_fractals(df: pd.DataFrame) -> Dict:
    """
    执行分型分析
    
    Returns
    -------
    Dict
        分析结果：
        - current_price: 当前价格
        - latest_fractal: 最新分型类型 (top/bottom/None)
        - latest_fractal_price: 最新分型价格
        - bi_direction: 当前笔方向 (up/down/None)
        - in_zhongshu: 是否在中枢内
        - zhongshu_range: 中枢区间 (zd, zg)
        - signal: 买卖点信号 (BS1/SS1/None)
    """
    analyzer = ChanTheoryAnalyzer()
    analyzer.load_klines(df)
    
    latest_kline = df.iloc[-1]
    current_price = latest_kline['close']
    
    # 最新分型
    latest_fractal = None
    latest_fractal_price = None
    if analyzer.fractals:
        latest_fractal = analyzer.fractals[-1]
        latest_fractal_price = latest_fractal.high if latest_fractal.type == Fractal.TOP else latest_fractal.low
    
    # 当前笔方向
    bi_direction = analyzer.get_current_bi_direction()
    
    # 中枢判断
    in_zhongshu = analyzer.is_in_zhongshu(current_price)
    zhongshu = analyzer.get_latest_zhongshu()
    zhongshu_range = (zhongshu.zd, zhongshu.zg) if zhongshu else (None, None)
    
    # 买卖点
    signal = analyzer.get_buy_sell_point()
    
    return {
        'current_price': current_price,
        'latest_fractal': latest_fractal.type if latest_fractal else None,
        'latest_fractal_price': latest_fractal_price,
        'bi_direction': bi_direction,
        'in_zhongshu': in_zhongshu,
        'zhongshu_range': zhongshu_range,
        'signal': signal,
        'summary': analyzer.summary()
    }


def monitor(symbol: str, interval: int, refresh_seconds: int = 60):
    """
    实时监控循环
    
    Parameters
    ----------
    symbol : str
        品种代码
    interval : int
        K 线周期 (分钟)
    refresh_seconds : int
        刷新间隔 (秒)
    """
    print(f"\n🐱 咕噜分型监控启动")
    print(f"品种：{symbol} | 周期：{interval}分钟 | 刷新：{refresh_seconds}秒")
    print("-" * 50)
    
    last_signal = None
    
    while True:
        try:
            # 获取数据
            df = fetch_kline_data(symbol, interval, limit=100)
            
            # 分析
            result = analyze_fractals(df)
            
            # 显示结果
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"\n[{ts}] {symbol} @ {result['current_price']}")
            print(f"  笔方向：{result['bi_direction'] or '无'}")
            print(f"  最新分型：{result['latest_fractal'] or '无'} @ {result['latest_fractal_price']}")
            print(f"  中枢内：{'是' if result['in_zhongshu'] else '否'} {result['zhongshu_range']}")
            
            # 信号提醒
            if result['signal'] and result['signal'] != last_signal:
                print(f"\n  🚨 信号：{result['signal']}")
                last_signal = result['signal']
            
            # 等待下次刷新
            time.sleep(refresh_seconds)
            
        except KeyboardInterrupt:
            print("\n\n监控已停止")
            break
        except Exception as e:
            print(f"[错误] {e}")
            time.sleep(refresh_seconds)


def main():
    parser = argparse.ArgumentParser(description="缠论分型实时监控")
    parser.add_argument("--symbol", type=str, required=True, help="品种代码，如 rb2505")
    parser.add_argument("--interval", type=int, default=5, help="K 线周期 (分钟), 默认 5")
    parser.add_argument("--refresh", type=int, default=60, help="刷新间隔 (秒), 默认 60")
    
    args = parser.parse_args()
    monitor(args.symbol, args.interval, args.refresh)


if __name__ == "__main__":
    main()
