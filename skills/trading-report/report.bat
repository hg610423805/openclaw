@echo off
chcp 65001 >nul
echo === 期货交易报告生成器 ===
echo.
cd /d "%~dp0"
python quick_report.py
echo.
echo 正在打开报告...
start trading_report_quick.html
echo.
echo [OK] 完成！
