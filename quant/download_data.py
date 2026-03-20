# -*- coding: utf-8 -*-
"""
期货历史数据下载脚本
====================
功能：下载 10 个期货主连品种的 2025 年全年 5 分钟 K 线数据，保存到本地 CSV

作者：咕噜 🐱
"""

from datetime import datetime, date
from tqsdk import TqApi, TqAuth, TqSim
import pandas as pd
import os
import time

# ============ 配置区 ============
ACCOUNT = "13163715864"
PASSWORD = "Hgssh285755"

# 10 个期货主连品种（覆盖不同板块）
SYMBOLS = [
    # 黑色系
    "KQ.m@SHFE.rb",   # 螺纹钢
    "KQ.m@SHFE.hc",   # 热卷
    "KQ.m@SHFE.i",    # 铁矿石
    
    # 有色金属
    "KQ.m@SHFE.cu",   # 铜
    "KQ.m@SHFE.al",   # 铝
    "KQ.m@SHFE.zn",   # 锌
    
    # 农产品
    "KQ.m@DCE.m",     # 豆粕
    "KQ.m@DCE.y",     # 豆油
    "KQ.m@CZCE.CF",   # 棉花
    
    # 能源化工
    "KQ.m@SHFE.bu",   # 沥青
]

# 时间范围
YEAR = 2025
START_DATE = f"{YEAR}-01-01"
END_DATE = f"{YEAR}-12-31"

# 数据周期（秒）
INTERVAL = 300  # 5 分钟

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===========================


def symbol_to_filename(symbol):
    """将合约代码转换为文件名"""
    # KQ.m@SHFE.rb -> rb_SHFE
    parts = symbol.split("@")
    if len(parts) == 2:
        exchange = parts[1].split(".")[0]
        code = parts[1].split(".")[1]
        return f"{code}_{exchange}_{INTERVAL}s.csv"
    return symbol.replace("@", "_").replace(".", "_") + f"_{INTERVAL}s.csv"


def download_symbol_data(api, symbol, start_date, end_date):
    """
    下载单个品种的历史数据
    返回：DataFrame 或 None（失败）
    """
    print(f"\n⬇️  下载：{symbol}")
    print(f"   时间：{start_date} 至 {end_date}")
    
    try:
        # 获取 K 线数据
        klines = api.get_kline_serial(symbol, INTERVAL)
        
        # 过滤时间范围
        if len(klines) == 0:
            print(f"   ❌ 无数据")
            return None
        
        # 转换时间列为可读格式
        klines['datetime'] = pd.to_datetime(klines['datetime'], unit='ns')
        
        # 过滤日期范围
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1)
        
        mask = (klines['datetime'] >= start_dt) & (klines['datetime'] < end_dt)
        filtered = klines[mask].copy()
        
        if len(filtered) == 0:
            print(f"   ⚠️  时间范围内无数据")
            return None
        
        print(f"   ✅ 下载完成：{len(filtered)} 根 K 线")
        return filtered
        
    except Exception as e:
        print(f"   ❌ 错误：{e}")
        return None


def save_to_csv(df, symbol, output_dir):
    """保存数据到 CSV"""
    filename = symbol_to_filename(symbol)
    filepath = os.path.join(output_dir, filename)
    
    # 选择要保存的列
    columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'open_oi']
    available_cols = [c for c in columns if c in df.columns]
    
    df[available_cols].to_csv(filepath, index=False, encoding='utf-8')
    print(f"   💾 已保存：{filepath}")
    return filepath


def verify_data(filepath):
    """验证下载的数据"""
    try:
        df = pd.read_csv(filepath)
        print(f"   📊 验证：{len(df)} 行，{len(df.columns)} 列")
        
        # 检查数据质量
        if len(df) > 0:
            print(f"      首条：{df['datetime'].iloc[0]}")
            print(f"      末条：{df['datetime'].iloc[-1]}")
            print(f"      品种：{filepath.split('/')[-1]}")
        return True
    except Exception as e:
        print(f"   ❌ 验证失败：{e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("📥 期货历史数据下载工具")
    print("=" * 60)
    print(f"年份：{YEAR}")
    print(f"周期：{INTERVAL}秒 (5 分钟)")
    print(f"品种数：{len(SYMBOLS)}")
    print(f"输出目录：{OUTPUT_DIR}")
    print("=" * 60)
    
    # 初始化 API
    print("\n🔌 连接天勤服务器...")
    try:
        auth = TqAuth(ACCOUNT, PASSWORD)
        api = TqApi(auth=auth)
        print("✅ 连接成功")
    except Exception as e:
        print(f"❌ 连接失败：{e}")
        return
    
    # 下载数据
    success_count = 0
    failed_symbols = []
    
    for i, symbol in enumerate(SYMBOLS, 1):
        print(f"\n[{i}/{len(SYMBOLS)}] 处理：{symbol}")
        
        # 下载
        df = download_symbol_data(api, symbol, START_DATE, END_DATE)
        
        if df is not None and len(df) > 0:
            # 保存
            filepath = save_to_csv(df, symbol, OUTPUT_DIR)
            
            # 验证
            if verify_data(filepath):
                success_count += 1
            else:
                failed_symbols.append(symbol)
        else:
            failed_symbols.append(symbol)
        
        # 避免请求过快（可选）
        if i < len(SYMBOLS):
            time.sleep(1)
    
    # 汇总
    print("\n" + "=" * 60)
    print("📊 下载汇总")
    print("=" * 60)
    print(f"成功：{success_count}/{len(SYMBOLS)}")
    print(f"失败：{len(failed_symbols)}")
    
    if failed_symbols:
        print(f"\n失败的品种：")
        for s in failed_symbols:
            print(f"  - {s}")
    
    print(f"\n💾 数据目录：{OUTPUT_DIR}")
    
    # 列出所有文件
    print(f"\n📁 已保存的文件:")
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith('.csv'):
            filepath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(filepath) / 1024  # KB
            print(f"   {f} ({size:.1f} KB)")
    
    api.close()
    print("\n✅ 完成！")


if __name__ == "__main__":
    main()
