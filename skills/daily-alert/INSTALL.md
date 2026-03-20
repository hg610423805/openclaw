# 📰 每日新闻提醒 - 安装指南

## ✅ 已完成

- [x] 创建新闻抓取脚本 (`fetch_news.py`)
- [x] 创建 Windows 任务计划脚本 (`setup_task.ps1`)
- [x] 配置 HEARTBEAT.md 定时任务
- [x] 创建技能文档 (SKILL.md)
- [x] 创建配置文件 (config.json)

## 🔧 需要配置

### 1. Web Search API Key（必需）

要获取实时新闻，需要配置 Kimi API：

**方法 A：环境变量**
```bash
# Windows PowerShell
$env:KIMI_API_KEY="your-api-key-here"
```

**方法 B：Gateway 配置**
编辑 Gateway 配置文件，添加：
```json
{
  "tools": {
    "web": {
      "search": {
        "kimi": {
          "apiKey": "your-api-key-here"
        }
      }
    }
  }
}
```

获取 API Key：https://platform.moonshot.cn/

### 2. 安装 Windows 任务计划

**以管理员身份运行 PowerShell：**
```powershell
cd C:\Users\17699\.openclaw\workspace\skills\daily-alert
powershell -ExecutionPolicy Bypass -File setup_task.ps1
```

**验证安装：**
```powershell
Get-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"
```

### 3. 测试运行

**手动测试脚本：**
```bash
cd skills/daily-alert
python fetch_news.py
```

**手动触发任务：**
```powershell
Start-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"
```

## 📋 输出位置

- **本地报告**：`skills/daily-alert/daily_report.txt`
- **飞书推送**：需配置 Webhook（可选）

## 🎯 使用说明

### 自动执行
每天早上 8:00 自动运行，生成报告

### 手动查询
- `/daily-alert` - 获取今日新闻
- `期货消息` - 获取期货相关新闻
- `A 股消息` - 获取 A 股板块新闻

## ⚠️ 注意事项

1. **API 限制**：免费 API 有调用次数限制
2. **消息准确性**：自动分析仅供参考
3. **周末节假日**：期货市场休市时会标注

## 🔍 故障排除

**Q: 没有抓取到新闻？**
- 检查网络连接
- 配置 API Key
- 查看 `daily_report.txt` 日志

**Q: 任务没有执行？**
- 检查任务状态：`Get-ScheduledTask -TaskName "..."`
- 查看历史：`Get-ScheduledTaskInfo -TaskName "..."`

**Q: 想修改推送时间？**
- 编辑 `setup_task.ps1` 中的 `-At 8am`
- 重新运行安装脚本

## 📞 支持

问题反馈：查看 `README.md` 或联系管理员
