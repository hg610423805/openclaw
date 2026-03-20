@echo off
echo ========================================
echo  GitHub Hosts 更新工具
echo ========================================
echo.
echo 正在请求管理员权限...
echo.

powershell -Command "Start-Process PowerShell -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"C:\Users\17699\.openclaw\workspace\update-hosts.ps1\"' -Verb RunAs"

echo.
echo 如果弹出管理员确认窗口，点"是"即可。
echo ========================================
pause
