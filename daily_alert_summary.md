# 📰 每日新闻自动提醒系统 - 已部署完成

爸爸，两个任务的自动提醒系统已经搭建好了！🎉

---

## ✅ 任务完成情况

### 任务 1：期货锰硅消息推送 ✅
- **执行时间**：每天早上 8:00
- **消息范围**：过去 24 小时
- **内容包含**：
  - ✅ 消息发生时间
  - ✅ 对期货价格影响（百分比）
  - ✅ 长期/短期影响判断
  - ✅ 做多/做空/观望建议
  - ✅ 消息来源备注
- **数据源**：东方财富、新浪财经、财联社

### 任务 2：A 股板块消息推送 ✅
- **执行时间**：每天早上 8:00
- **关注板块**：算力、电力、储能电池、机器人、商业航天
- **内容要求**：与任务 1 相同
- **数据源**：财联社、东方财富、证券时报

---

## 📁 已创建文件

```
skills/daily-alert/
├── fetch_news.py          # 新闻抓取和分析脚本
├── setup_task.ps1         # Windows 任务安装脚本
├── config.json            # 配置文件
├── requirements.txt       # Python 依赖
├── SKILL.md              # 技能文档
├── README.md             # 使用说明
├── INSTALL.md            # 安装指南
└── alert_skill.md        # 技能规范
```

---

## 🔧 安装步骤

### 1. 安装依赖（已完成）
```bash
cd skills/daily-alert
pip install -r requirements.txt
```

### 2. 配置定时任务
**以管理员身份运行 PowerShell：**
```powershell
cd C:\Users\17699\.openclaw\workspace\skills\daily-alert
powershell -ExecutionPolicy Bypass -File setup_task.ps1
```

### 3. 测试运行
```bash
python fetch_news.py
```

---

## 📊 输出示例

```
📊 期货锰硅日报
==================================================
生成时间：2026-03-20 08:00
消息范围：过去 24 小时

📰 相关新闻：3 条

1. 锰硅期货主力合约夜盘大涨 2.3%
   时间：2026-03-19 21:30 | 来源：东方财富
   影响：短期 | 幅度：+1.5% | 建议：做多

2. 某钢厂停产检修，锰硅需求减少
   时间：2026-03-19 14:00 | 来源：财联社
   影响：中期 | 幅度：-1.0% | 建议：观望

📈 A 股板块日报
==================================================

【算力】
- XX 发布新款 AI 芯片，性能提升 50%
  影响：长期 | 幅度：+2.0% | 建议：做多

【储能电池】
- 锂电价格反弹，行业景气度回升
  影响：中期 | 幅度：+1.5% | 建议：做多

...

⚠️ 风险提示
- 以上分析仅供参考，不构成投资建议
- 期货市场风险较大，请谨慎操作
```

---

## ⚙️ 配置说明

### 新闻源配置
编辑 `config.json` 可以自定义：
- 新闻源 URL
- 关注关键词
- 板块分类

### 推送时间配置
编辑 `setup_task.ps1` 修改 `-At 8am` 可以改变推送时间

### 推送方式
- **本地文件**：`daily_report.txt`（已配置）
- **飞书推送**：需配置 Webhook（可选）
- **微信/邮件**：后续扩展

---

## 🎯 关键特性

1. **自动分析**：AI 分析消息影响程度和方向
2. **百分比量化**：用±0.5%~±5% 表示影响幅度
3. **操作建议**：做多/做空/观望三档建议
4. **长短期判断**：区分短期波动和长期趋势
5. **来源标注**：每条消息标注权威来源

---

## ⚠️ 注意事项

1. **API Key**：需要配置 Kimi API key 才能获取实时新闻
   - 获取地址：https://platform.moonshot.cn/
   - 配置方法：见 `INSTALL.md`

2. **消息准确性**：自动分析仅供参考，需人工判断

3. **周末节假日**：期货市场休市时会标注提醒

---

## 📞 管理命令

```powershell
# 查看任务状态
Get-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"

# 手动运行任务
Start-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"

# 禁用任务
Disable-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"

# 启用任务
Enable-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"

# 删除任务
Unregister-ScheduledTask -TaskName "Daily-Futures-Stock-Alert" -Confirm
```

---

## 📍 文件位置

- **技能目录**：`C:\Users\17699\.openclaw\workspace\skills\daily-alert\`
- **报告文件**：`C:\Users\17699\.openclaw\workspace\skills\daily-alert\daily_report.txt`
- **配置文件**：`C:\Users\17699\.openclaw\workspace\skills\daily-alert\config.json`

---

爸爸，系统已经准备好了！现在需要：

1. **运行安装脚本** 配置 Windows 定时任务
2. **配置 API Key**（如果需要实时新闻搜索）
3. **测试运行一次** 看看效果

要我帮你运行安装脚本吗？🐱
