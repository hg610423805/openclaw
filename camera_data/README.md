# 📷 摄像头监控系统使用指南

咕噜帮你搭建的摄像头监控系统，支持拍照、录像、动作检测和环境监控。

## 🚀 快速使用

### 拍照
```powershell
python scripts\camera_monitor.py photo
python scripts\camera_monitor.py photo my_photo.jpg
```

### 录像（默认 10 秒）
```powershell
python scripts\camera_monitor.py video
python scripts\camera_monitor.py video 30  # 录 30 秒
```

### 动作检测（默认 30 秒）
```powershell
python scripts\camera_monitor.py motion
python scripts\camera_monitor.py motion 60  # 检测 60 秒
```

### 环境监控（默认 60 秒）⭐ 推荐
```powershell
python scripts\camera_monitor.py monitor
python scripts\camera_monitor.py monitor 120  # 监控 2 分钟
```

## 📊 环境监控功能

监控模式会检测并报告以下异常：

| 异常类型 | 说明 | 警报标记 |
|----------|------|----------|
| 大幅动作 | 可能有人进入监控区域 | ⚠️ |
| 持续动作 | 连续检测到动作，可疑活动 | 🚨 |
| 光线突变 | 可能开关灯 | 💡 |

监控结束后会生成详细报告。

## 📁 数据存储

所有数据保存在 `camera_data/` 目录：

```
camera_data/
├── photos/          # 照片
├── videos/          # 视频
└── motion_logs/     # 动作检测日志
```

## ⚙️ 自定义配置

编辑 `scripts/camera_monitor.py` 修改以下参数：

```python
CAMERA_ID = 0              # 摄像头编号（多摄像头可改）
MOTION_THRESHOLD = 500     # 动作检测灵敏度（越小越敏感）
CHECK_INTERVAL = 2         # 检测间隔（秒）
```

## 🔔 定时监控（后续扩展）

可以配合 OpenClaw 的 cron 功能实现定时监控：
- 每天早上/晚上自动监控
- 离家时自动开启监控
- 检测到异常时推送通知

需要的话告诉咕噜，帮你配置！

---

*🐱 咕噜提示：注意隐私，不要在敏感场所使用哦~*
