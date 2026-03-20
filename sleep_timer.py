# -*- coding: utf-8 -*-
"""
睡眠定时器 - 30分钟后停止播放音乐
"""

import time
import os
from datetime import datetime, timedelta

def stop_music():
    """停止音乐播放"""
    # 方法1: 关闭浏览器标签（Chrome/Edge）
    os.system('taskkill /F /IM chrome.exe 2>nul')
    os.system('taskkill /F /IM msedge.exe 2>nul')
    
    # 方法2: 静音系统
    # os.system('nircmd.exe mutesysvolume 1')
    
    print(f"[{datetime.now()}] 音乐已停止播放")
    print("晚安，爸爸！🌙")

def main():
    print("="*50)
    print("🎵 睡眠定时器启动")
    print("="*50)
    print(f"当前时间: {datetime.now()}")
    print(f"将在30分钟后自动停止音乐")
    print(f"停止时间: {datetime.now() + timedelta(minutes=30)}")
    print("="*50)
    
    # 等待30分钟
    print("\n⏳ 倒计时开始...")
    for i in range(30, 0, -1):
        if i % 5 == 0:  # 每5分钟显示一次
            print(f"还剩 {i} 分钟...")
        time.sleep(60)  # 等待1分钟
    
    # 停止音乐
    print("\n🔇 时间到！停止播放...")
    stop_music()

if __name__ == "__main__":
    main()
