# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras
- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH
- home-server → 192.168.1.100, user: admin

### TTS
- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## 🐱 咕噜的配置

### TTS (语音合成)
- **服务**: Windows SAPI (系统自带)
- **首选声音**: Female Teen (少女音)
- **用途**: 晚安消息、故事讲述、重要提醒
- **备注**: ElevenLabs 待配置（需要 API Key）

### SSH
- (待添加)

### 摄像头
- **类型**: 笔记本内置摄像头 (Camera ID: 0)
- **状态**: ✅ 已测试可用
- **功能**:
  - 拍照：`python scripts/camera_monitor.py photo [filename]`
  - 录像：`python scripts/camera_monitor.py video [duration_sec]`
  - 动作检测：`python scripts/camera_monitor.py motion [duration_sec]`
  - 环境监控：`python scripts/camera_monitor.py monitor [duration_sec]`
- **数据存储**: `camera_data/` 目录
  - 照片：`camera_data/photos/`
  - 视频：`camera_data/videos/`
  - 日志：`camera_data/motion_logs/`
- **监控模式**: 可检测大幅动作、光线突变、持续可疑活动

---

Add whatever helps you do your job. This is your cheat sheet.
