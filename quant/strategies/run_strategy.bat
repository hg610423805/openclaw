@echo off
chcp 65001 >nul
echo ========================================
echo   均线+KDJ 趋势跟踪策略 - 快速启动
echo ========================================
echo.

:menu
echo.
echo 请选择操作:
echo   1. 回测 (单个合约)
echo   2. 回测 (批量合约)
echo   3. 实盘模拟
echo   4. 查看策略说明
echo   5. 退出
echo.
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto backtest_single
if "%choice%"=="2" goto backtest_batch
if "%choice%"=="3" goto live_sim
if "%choice%"=="4" goto readme
if "%choice%"=="5" goto end
goto menu

:backtest_single
echo.
set /p symbol=请输入合约代码 (如 rb2505): 
set /p start=请输入开始日期 (如 2025-01-01): 
set /p end=请输入结束日期 (如 2025-03-22): 
echo.
echo 正在回测 %symbol%...
python ma_kdj_trend_backtest.py --symbol SHFE.%symbol% --start %start% --end %end%
pause
goto menu

:backtest_batch
echo.
echo 批量回测：rb, hc, m, SM, SF (2024-2025)
python batch_backtest.py
pause
goto menu

:live_sim
echo.
echo ✅ 天勤账号已配置 (quant/config.py)
echo.
set /p confirm=确认启动实盘模拟？(y/n): 
if "%confirm%"=="y" (
    python ma_kdj_trend.py
) else (
    echo 已取消
)
pause
goto menu

:readme
echo.
start notepad README_MA_KDJ.md
pause
goto menu

:end
echo.
echo 再见!
pause
