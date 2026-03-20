@echo off
chcp 65001 >nul
echo === 每日新闻提醒系统 - 快速配置 ===
echo.
echo 1. 配置 KIMI API Key
echo    访问：https://platform.moonshot.cn/
echo    注册账号并获取 API Key
echo.
echo 2. 设置环境变量
echo    方法 A - 临时设置（当前会话）:
echo    set KIMI_API_KEY=你的 API key
echo.
echo    方法 B - 永久设置:
echo    右键"此电脑" - 属性 - 高级系统设置
echo    环境变量 - 系统变量 - 新建
echo    变量名：KIMI_API_KEY
echo    变量值：你的 API key
echo.
echo 3. 测试运行
python skills\daily-alert\run_alert.py
echo.
echo === 配置完成 ===
echo.
echo 定时任务已安装：每天早上 8:00 自动执行
echo 任务名称：Daily-Futures-Stock-Alert
echo.
echo 管理命令:
echo   查看任务状态：powershell Get-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"
echo   手动运行任务：powershell Start-ScheduledTask -TaskName "Daily-Futures-Stock-Alert"
echo   删除任务：powershell Unregister-ScheduledTask -TaskName "Daily-Futures-Stock-Alert" -Confirm
echo.
pause
