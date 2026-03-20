#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摄像头监控系统 - 咕噜的监控助手 🐱
功能：拍照、录像、动作检测、环境异常报告
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
from pathlib import Path

# 配置
CAMERA_ID = 0  # 笔记本内置摄像头
BASE_DIR = Path(__file__).parent.parent / "camera_data"
PHOTOS_DIR = BASE_DIR / "photos"
VIDEOS_DIR = BASE_DIR / "videos"
MOTION_DIR = BASE_DIR / "motion_logs"

# 动作检测阈值
MOTION_THRESHOLD = 500  # 像素变化阈值
CHECK_INTERVAL = 2  # 检测间隔（秒）

def init_dirs():
    """初始化目录"""
    for d in [PHOTOS_DIR, VIDEOS_DIR, MOTION_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    return True

def take_photo(filename=None):
    """拍照"""
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        return None, "摄像头无法打开"
    
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None, "拍照失败"
    
    if filename is None:
        filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    
    filepath = PHOTOS_DIR / filename
    cv2.imwrite(str(filepath), frame)
    return str(filepath), "拍照成功"

def record_video(duration=10, filename=None):
    """录像"""
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        return None, "摄像头无法打开"
    
    if filename is None:
        filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
    
    filepath = VIDEOS_DIR / filename
    
    # 获取帧尺寸
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(str(filepath), fourcc, fps, (width, height))
    
    start = time.time()
    frame_count = 0
    
    while time.time() - start < duration:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            frame_count += 1
        time.sleep(0.05)  # 约 20fps
    
    cap.release()
    out.release()
    
    return str(filepath), f"录像完成：{frame_count}帧"

def detect_motion(duration=30, sensitivity=MOTION_THRESHOLD):
    """
    动作检测
    返回：检测到的动作次数、日志文件路径
    """
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        return 0, None, "摄像头无法打开"
    
    # 读取第一帧作为背景
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return 0, None, "无法读取画面"
    
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    
    motion_count = 0
    motion_events = []
    start_time = time.time()
    
    log_file = MOTION_DIR / f"motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"动作检测日志 - 开始时间：{datetime.now().isoformat()}\n")
        f.write(f"灵敏度阈值：{sensitivity}\n\n")
        
        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # 计算帧差
            frame_diff = cv2.absdiff(prev_gray, gray)
            _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=2)
            
            # 查找轮廓
            contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > sensitivity:
                    motion_detected = True
                    break
            
            if motion_detected:
                motion_count += 1
                timestamp = datetime.now().isoformat()
                motion_events.append(timestamp)
                f.write(f"[{timestamp}] 检测到动作！\n")
                print(f"⚠️  [{timestamp}] 检测到动作！")
            
            prev_gray = gray
            time.sleep(CHECK_INTERVAL)
        
        f.write(f"\n检测结束：{datetime.now().isoformat()}\n")
        f.write(f"总动作次数：{motion_count}\n")
    
    cap.release()
    return motion_count, str(log_file), "检测完成"

def monitor_environment(duration=60):
    """
    环境监控 - 检测异常并报告
    检测内容：
    - 大幅动作（可能有人进入）
    - 光线突变（可能开关灯）
    - 持续动作（可疑活动）
    """
    cap = cv2.VideoCapture(CAMERA_ID)
    if not cap.isOpened():
        return "摄像头无法打开"
    
    ret, prev_frame = cap.read()
    if not ret:
        cap.release()
        return "无法读取画面"
    
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    prev_brightness = np.mean(prev_gray)
    
    alerts = []
    start_time = time.time()
    consecutive_motion = 0
    
    report = {
        "start_time": datetime.now().isoformat(),
        "duration": duration,
        "alerts": [],
        "summary": ""
    }
    
    print(f"🐱 咕噜开始环境监控，持续{duration}秒...")
    
    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        current_brightness = np.mean(gray)
        
        # 动作检测
        frame_diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        total_motion_area = sum(cv2.contourArea(c) for c in contours)
        
        # 光线检测
        brightness_change = abs(current_brightness - prev_brightness)
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 大幅动作警报
        if total_motion_area > 5000:
            alert = f"[{timestamp}] ⚠️ 大幅动作 detected! 可能有人进入监控区域"
            alerts.append(alert)
            print(alert)
            consecutive_motion += 1
        elif total_motion_area > MOTION_THRESHOLD:
            consecutive_motion += 1
            # 持续动作警报
            if consecutive_motion >= 3:
                alert = f"[{timestamp}] 🚨 持续动作！可疑活动可能"
                alerts.append(alert)
                print(alert)
                consecutive_motion = 0
        else:
            consecutive_motion = 0
        
        # 光线突变警报
        if brightness_change > 30:
            direction = "变亮" if current_brightness > prev_brightness else "变暗"
            alert = f"[{timestamp}] 💡 光线{direction}！可能开关灯"
            alerts.append(alert)
            print(alert)
        
        prev_gray = gray
        prev_brightness = current_brightness
        time.sleep(CHECK_INTERVAL)
    
    cap.release()
    
    # 生成报告
    report["alerts"] = alerts
    if len(alerts) == 0:
        report["summary"] = "✅ 监控期间未发现异常"
    else:
        report["summary"] = f"⚠️ 共检测到 {len(alerts)} 起异常事件"
    
    return report

if __name__ == "__main__":
    import sys
    
    init_dirs()
    
    if len(sys.argv) < 2:
        print("用法：python camera_monitor.py <command> [args]")
        print("命令:")
        print("  photo [filename]     - 拍照")
        print("  video [duration]     - 录像（默认 10 秒）")
        print("  motion [duration]    - 动作检测（默认 30 秒）")
        print("  monitor [duration]   - 环境监控（默认 60 秒）")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "photo":
        filename = sys.argv[2] if len(sys.argv) > 2 else None
        path, msg = take_photo(filename)
        print(f"{msg}: {path}" if path else msg)
    
    elif cmd == "video":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        path, msg = record_video(duration)
        print(f"{msg}: {path}" if path else msg)
    
    elif cmd == "motion":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        count, log, msg = detect_motion(duration)
        print(f"{msg} - 检测到 {count} 次动作，日志：{log}")
    
    elif cmd == "monitor":
        duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        report = monitor_environment(duration)
        print("\n" + "="*50)
        print("📊 监控报告")
        print("="*50)
        print(f"开始时间：{report['start_time']}")
        print(f"持续时间：{report['duration']}秒")
        print(f"\n{report['summary']}")
        if report['alerts']:
            print("\n异常事件列表:")
            for alert in report['alerts']:
                print(f"  {alert}")
    
    else:
        print(f"未知命令：{cmd}")
