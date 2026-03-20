# 📰 每日新闻自动提醒系统

## 功能说明

每天早上 8 点自动推送：
1. **期货锰硅** 过去 24 小时重大消息
2. **A 股板块**（算力/电力/储能/机器人/商业航天）过去 24 小时重大消息

## 安装步骤

### 1. 安装依赖
```bash
cd skills/daily-alert
pip install -r requirements.txt
```

### 2. 配置 Windows 任务计划（推荐）
以管理员身份运行 PowerShell：
```powershell
cd C:\Users\17699\.openclaw\workspace\skills\daily-alert
powershell -ExecutionPolicy Bypass -File setup_task.ps1
```

### 3. 手动测试
```bash
python fetch_news.py
```

## 配置新闻源

由于各网站 API 政策不同，建议配置以下免费源：

### 期货新闻源
- 东方财富期货 RSS：`http://app.finance.eastmoney.com/rss.aspx`
- 新浪财经期货：手动访问 `https://finance.sina.com.cn/future/`
- 期货日报：`http://www.qhrb.com.cn/`

### A 股新闻源
- 财联社电报：`https://www.cls.cn/telegraph`
- 东方财富快讯：`https://news.eastmoney.com/kx/`
- 证券时报：`http://www.stcn.com/`

## 输出格式

```
📊 期货锰硅日报
==================================================
生成时间：2026-03-20 08:00
消息范围：过去 24 小时

📰 相关新闻：3 条

1. 锰硅期货主力合约大涨 2%
   时间：2026-03-19 15:30 | 来源：东方财富
   影响：短期 | 幅度：±1.0% | 建议：做多

2. ...

📈 A 股板块日报
==================================================
...
```

## 消息推送

### 方式 1：本地文件
报告保存在：`skills/daily-alert/daily_report.txt`

### 方式 2：飞书推送（需配置）
编辑 `config.json` 添加飞书 Webhook

### 方式 3：微信/邮件（后续扩展）

## 注意事项

1. **API 限制**：部分网站有反爬，建议降低抓取频率
2. **消息准确性**：自动分析仅供参考，需人工判断
3. **周末节假日**：期货市场休市时标注提醒

## 故障排除

**Q: 任务没有执行？**
- 检查任务计划：`Get-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"`
- 手动运行测试：`Start-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"`

**Q: 没有抓取到新闻？**
- 检查网络连接
- 更换新闻源 URL
- 查看 `daily_report.txt` 详细日志

**Q: 想修改推送时间？**
- 禁用原任务：`Disable-ScheduledTask -TaskName "..."`
- 修改 `setup_task.ps1` 中的时间
- 重新运行安装脚本
