# Windows 任务计划安装脚本 - 简化版

$taskName = "Daily-Futures-Stock-Alert"
$scriptPath = "C:\Users\17699\.openclaw\workspace\skills\daily-alert\auto_news.py"

Write-Host "=== 每日新闻提醒系统安装 ==="
Write-Host ""

# 创建任务计划
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$action = New-ScheduledTaskAction -Execute "python" -Argument $scriptPath -WorkingDirectory "C:\Users\17699\.openclaw\workspace\skills\daily-alert"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Force

Write-Host ""
Write-Host "=== 安装完成 ==="
Write-Host "任务名称：$taskName"
Write-Host "执行时间：每天早上 8:00"
Write-Host ""
Write-Host "测试运行中..."
python $scriptPath
