# -*- coding: utf-8 -*-
"""
检查 K 线数据详情
"""

from tqsdk import TqApi, TqAuth, TqBacktest
import pandas as pd
from datetime import datetime, timedelta

# 回测配置
END_DATE = datetime(2026, 3, 23)
START_DATE = END_DATE - timedelta(days=180)

# 品种配置
SYMBOLS = [
    {"code": "KQ.m@CZCE.SM", "name": "锰硅"},
    {"code": "KQ.m@CZCE.FG", "name": "玻璃"},
    {"code": "KQ.m@DCE.c", "name": "玉米"},
]

# 天勤账号
SHINNY_ACCOUNT = "13163715864"
SHINNY_PASSWORD = "Hgssh285755"

def check_kline_data(symbol_info):
    """检查 K 线数据"""
    symbol = symbol_info["code"]
    name = symbol_info["name"]
    
    print(f"\n{'='*70}")
    print(f"品种：{name} ({symbol})")
    print(f"{'='*70}")
    
    try:
        api = TqApi(
            auth=TqAuth(SHINNY_ACCOUNT, SHINNY_PASSWORD),
            backtest=TqBacktest(
                start_dt=START_DATE,
                end_dt=END_DATE
            )
        )
        
        # 获取 5 分钟 K 线
        klines_5m = api.get_kline_serial(symbol, duration_seconds=300, data_length=500)
        
        # 获取 30 分钟 K 线
        klines_30m = api.get_kline_serial(symbol, duration_seconds=1800, data_length=500)
        
        # 转换为 datetime
        klines_5m['datetime'] = pd.to_datetime(klines_5m['datetime'])
        klines_30m['datetime'] = pd.to_datetime(klines_30m['datetime'])
        
        # 统计信息
        print(f"\n【5 分钟 K 线】")
        print(f"  K 线数量：{len(klines_5m)} 根")
        print(f"  时间范围：{klines_5m['datetime'].min()} 至 {klines_5m['datetime'].max()}")
        print(f"  天数跨度：{(klines_5m['datetime'].max() - klines_5m['datetime'].min()).days} 天")
        print(f"  第一根 K 线：{klines_5m.iloc[0]['datetime']} - O:{klines_5m.iloc[0]['open']} H:{klines_5m.iloc[0]['high']} L:{klines_5m.iloc[0]['low']} C:{klines_5m.iloc[0]['close']}")
        print(f"  最后一根 K 线：{klines_5m.iloc[-1]['datetime']} - O:{klines_5m.iloc[-1]['open']} H:{klines_5m.iloc[-1]['high']} L:{klines_5m.iloc[-1]['low']} C:{klines_5m.iloc[-1]['close']}")
        
        print(f"\n【30 分钟 K 线】")
        print(f"  K 线数量：{len(klines_30m)} 根")
        print(f"  时间范围：{klines_30m['datetime'].min()} 至 {klines_30m['datetime'].max()}")
        print(f"  天数跨度：{(klines_30m['datetime'].max() - klines_30m['datetime'].min()).days} 天")
        print(f"  第一根 K 线：{klines_30m.iloc[0]['datetime']} - O:{klines_30m.iloc[0]['open']} H:{klines_30m.iloc[0]['high']} L:{klines_30m.iloc[0]['low']} C:{klines_30m.iloc[0]['close']}")
        print(f"  最后一根 K 线：{klines_30m.iloc[-1]['datetime']} - O:{klines_30m.iloc[-1]['open']} H:{klines_30m.iloc[-1]['high']} L:{klines_30m.iloc[-1]['low']} C:{klines_30m.iloc[-1]['close']}")
        
        # 检查交易时间
        print(f"\n【交易时间分析】")
        
        # 提取小时和分钟
        klines_5m['hour'] = klines_5m['datetime'].dt.hour
        klines_5m['minute'] = klines_5m['datetime'].dt.minute
        
        # 统计交易时段
        trading_hours = klines_5m.groupby(['hour', 'minute']).size()
        print(f"  交易时段分布（前 20 个）:")
        for (hour, minute), count in trading_hours.head(20).items():
            print(f"    {hour:02d}:{minute:02d} - {count} 根 K 线")
        
        # 检查夜盘
        night_trading = klines_5m[(klines_5m['hour'] >= 21) | (klines_5m['hour'] < 3)]
        print(f"\n  夜盘 K 线数量：{len(night_trading)} 根")
        if len(night_trading) > 0:
            print(f"  夜盘时间范围：{night_trading['datetime'].min()} 至 {night_trading['datetime'].max()}")
        
        # 检查日盘
        day_trading = klines_5m[(klines_5m['hour'] >= 9) & (klines_5m['hour'] < 18)]
        print(f"  日盘 K 线数量：{len(day_trading)} 根")
        
        # 检查数据连续性
        print(f"\n【数据连续性检查】")
        time_diffs = klines_5m['datetime'].diff()
        print(f"  平均时间间隔：{time_diffs.mean()}")
        print(f"  最小时间间隔：{time_diffs.min()}")
        print(f"  最大时间间隔：{time_diffs.max()}")
        
        # 检查中断
        gaps = time_diffs[time_diffs > pd.Timedelta(minutes=10)]
        if len(gaps) > 0:
            print(f"  发现 {len(gaps)} 处数据中断（间隔>10 分钟）")
            print(f"  中断位置:")
            for idx in gaps.index[:5]:
                prev_time = klines_5m.loc[idx-1, 'datetime']
                curr_time = klines_5m.loc[idx, 'datetime']
                print(f"    {prev_time} -> {curr_time} (间隔 {curr_time-prev_time})")
        
        api.close()
        
    except Exception as e:
        print(f"[ERROR] 检查失败：{str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*70)
    print("K 线数据采集情况检查")
    print("="*70)
    print(f"回测区间：{START_DATE.strftime('%Y-%m-%d')} 至 {END_DATE.strftime('%Y-%m-%d')}")
    print(f"总天数：{(END_DATE - START_DATE).days} 天")
    print("="*70)
    
    for symbol_info in SYMBOLS:
        check_kline_data(symbol_info)
    
    print("\n" + "="*70)
    print("检查完成")
    print("="*70)
