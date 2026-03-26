# Session: 2026-03-22 均线+KDJ 策略创建

## 任务
创建基于均线与 KDJ 的 TQsdk 交易策略

## 策略规则
- **监控周期**: 30 分钟 K 线定方向
- **交易周期**: 5 分钟 K 线入场
- **指标**: EXPMA13/26 + KDJ(J 值)
- **方向判断**: 30 分钟 EXPMA13>26 只做多，反之只做空
- **入场方式**: 
  - 方式 1: 双周期 J 值极值 + 均线同向 + K 线确认
  - 方式 2: 30 分钟 J 值极值 + 5 分钟均线交叉
- **止损**: 前 K 线极值±1tick 或分型极值
- **移动止损**: 新分型优于前分型时更新
- **止盈**: 5 分钟均线反向交叉
- **限制**: 每日≤3 次交易，仓位≤50%，到期前 10 天移仓

## 已创建文件
```
quant/strategies/
├── ma_kdj_trend.py          # 策略主文件 (17KB)
├── ma_kdj_trend_backtest.py # 回测脚本 (12KB)
├── run_strategy.bat         # 快速启动
└── README_MA_KDJ.md         # 策略说明
```

## 使用方法
```bash
cd quant/strategies
run_strategy.bat
```

或命令行:
```bash
python ma_kdj_trend_backtest.py --symbol rb2505 --start 2025-01-01 --end 2025-03-22
```

## 待配置
- [ ] 天勤账号密码 (ma_kdj_trend.py 第 365 行)
- [ ] 主力合约映射表
- [ ] 各品种 Tick 值和合约乘数

## 下一步
- 运行回测验证策略效果
- 根据回测结果优化参数
- 接入实盘（如需）
