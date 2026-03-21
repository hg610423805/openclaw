# 财经日报自动推送脚本
# 每天早上 8 点执行，生成 H5 报告并推送链接到飞书

$ErrorActionPreference = "Stop"

Write-Host "[INFO] 开始执行财经日报生成任务..."

# 生成日报
$reportOutput = python scripts/daily-report-generator.py 2>&1

# 提取链接
$link = $reportOutput | Select-String "\[LINK\]" | ForEach-Object { $_.Line -replace '\[LINK\] ', '' }

if ($link) {
    $date = Get-Date -Format "yyyy-MM-dd"
    
    Write-Host "[INFO] 生成成功，推送链接到飞书..."
    
    # 推送消息到飞书
    $message = @"
📰 **财经日报已生成** ($date)

🔗 点击查看：$link

---

**今日内容**:
- 🛢️ 期货锰硅市场动态
- 📈 A 股 5 大板块新闻（算力/电力/储能电池/机器人/商业航天）
- 💡 策略建议

---

📅 明日 08:00 自动推送
🤖 由 咕噜 自动生成
"@
    
    openclaw message send --channel "feishu" --target "ou_2a456545aa7be2a12881fe2a3f21198e" --message $message
    
    Write-Host "[SUCCESS] 推送完成！"
} else {
    Write-Host "[ERROR] 生成失败，未获取到链接"
    exit 1
}
