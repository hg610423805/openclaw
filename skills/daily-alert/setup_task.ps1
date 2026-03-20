# Windows 任务计划安装脚本
# 每天早上 8 点自动执行新闻推送

$taskName = "Daily-Futures-Stock-Alert"
$scriptPath = "C:\Users\17699\.openclaw\workspace\skills\daily-alert\fetch_news.py"
$pythonPath = "python"

Write-Host "=== 每日新闻提醒系统安装 ==="
Write-Host ""

# 检查 Python 是否可用
try {
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Host "Python 已安装：$pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python 未安装或不在 PATH 中" -ForegroundColor Red
    Write-Host "请先安装 Python 或添加到 PATH"
    exit 1
}

# 创建任务计划
Write-Host ""
Write-Host "正在创建任务计划..."
$trigger = New-ScheduledTaskTrigger -Daily -At 8am
$action = New-ScheduledTaskAction -Execute $pythonPath -Argument $scriptPath -WorkingDirectory "C:\Users\17699\.openclaw\workspace\skills\daily-alert"
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

try {
    Register-ScheduledTask -TaskName $taskName -Trigger $trigger -Action $action -Settings $settings -Principal $principal -Force | Out-Null
    Write-Host "任务计划已创建：$taskName" -ForegroundColor Green
    Write-Host "执行时间：每天早上 8:00" -ForegroundColor Green
} catch {
    Write-Host "创建任务失败：$_" -ForegroundColor Red
    Write-Host "请尝试以管理员身份运行此脚本"
    exit 1
}

# 显示任务信息
Write-Host ""
Write-Host "=== 任务信息 ==="
Get-ScheduledTask -TaskName $taskName | Select-Object TaskName, State, LastRunTime, NextRunTime

Write-Host ""
Write-Host "=== 测试运行 ==="
& $pythonPath $scriptPath

Write-Host ""
Write-Host "=== 安装完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "管理命令："
Write-Host "  查看任务：Get-ScheduledTask -TaskName '$taskName'"
Write-Host "  手动运行：Start-ScheduledTask -TaskName '$taskName'"
Write-Host "  禁用任务：Disable-ScheduledTask -TaskName '$taskName'"
Write-Host "  删除任务：Unregister-ScheduledTask -TaskName '$taskName' -Confirm"
