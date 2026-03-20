# 交易报告生成技能

## 功能

一键生成期货交易回测报告，包含：
- 总览统计（总盈亏、交易数、胜率）
- 按品种分类统计
- 每个品种的完整交易明细
- 交互式图表

## 使用方法

### 快速生成
```bash
cd skills/trading-report
python quick_report.py
```

### 输出位置
`C:\Users\17699\.openclaw\workspace\trading_report_quick.html`

### 自动打开
```bash
python quick_report.py && start trading_report_quick.html
```

## 输入数据

需要 `analysis_data.json` 文件，包含：
- trades: 交易列表
- 每笔交易包含：date, product, direction, lots, pnl

## 输出内容

1. **总览卡片**
   - 总交易笔数
   - 总盈亏
   - 品种数
   - 平均胜率

2. **每个品种独立板块**
   - 统计卡片（次数、盈亏、盈利、亏损、胜率）
   - 完整交易明细表格（日期、方向、手数、盈亏、累计）

3. **交互功能**
   - 表格可滚动
   - 悬停高亮
   - 颜色标识盈亏

## 扩展功能

如需添加开仓时间、止损止盈信息，使用完整版：
```bash
python generate_report_v2.py
```

需要从 summary.txt 原始文件解析详细信息。

## 快速命令

创建批处理文件 `report.bat`：
```batch
@echo off
cd skills/trading-report
python quick_report.py
start trading_report_quick.html
```

以后只需运行 `report.bat` 即可！
