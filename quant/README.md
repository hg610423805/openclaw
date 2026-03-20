# 咕噜的量化交易框架 🐱📈

基于天勤量化 (TQSDK 3.9.1) 的股票/期货量化交易系统，集成缠论分析。

---

## 📁 文件结构

```
quant/
├── README.md              # 本文件
├── config.py              # 配置文件（账户、参数）
├── chan_theory.py         # 缠论分析模块
├── fenxing_monitor.py     # 分型实时监控脚本
├── strategy_template.py   # 策略模板（缠论策略）
├── quick_backtest.py      # 快速回测示例（双均线）
└── strategies/            # 你的自定义策略（待创建）
    ├── my_strategy_1.py
    └── ...
```

---

## 🚀 快速开始

### 1. 配置账户

编辑 `config.py`，填写你的账户信息：

```python
# 快期账户（必须，用于获取行情）
SHINNY_ACCOUNT = "你的快期账户"
SHINNY_PASSWORD = "你的密码"

# 期货账户（实盘时需要）
BROKER_NAME = "H 宏源期货"
FUTURES_ACCOUNT = "你的期货账号"
FUTURES_PASSWORD = "你的期货密码"
```

**注册快期账户**: https://account.shinnytech.com/

---

### 2. 运行分型监控

```powershell
cd quant
py fenxing_monitor.py --symbol rb2505 --interval 5 --refresh 60
```

**参数说明:**
- `--symbol`: 品种代码 (如 rb2505, IF2403)
- `--interval`: K 线周期 (分钟), 默认 5
- `--refresh`: 刷新间隔 (秒), 默认 60

---

### 3. 运行第一个回测

```powershell
cd quant
py quick_backtest.py
```

这会运行一个双均线策略回测（螺纹钢主力合约）。

---

### 4. 运行缠论策略

```powershell
# 回测模式
py strategy_template.py --symbol KQ.m@SHFE.rb --backtest --start-date 2024-01-01 --end-date 2024-06-30

# 实盘模式（先配置好期货账户！）
py strategy_template.py --symbol KQ.m@SHFE.rb --interval 60
```

---

## 📊 可用合约

在 `config.py` 的 `WATCHLIST` 中查看：

| 代码 | 名称 | 交易所 |
|------|------|--------|
| `IF` | 沪深 300 股指 | CFFEX |
| `RB` | 螺纹钢 | SHFE |
| `CU` | 铜 | SHFE |
| `AU` | 黄金 | SHFE |
| `M` | 豆粕 | DCE |
| `CF` | 棉花 | CZCE |

**格式说明:**
- `KQ.m@SHFE.rb` = 螺纹钢主力合约（自动换月）
- `SHFE.rb2405` = 螺纹钢 2405 合约（固定）

---

## 🧠 缠论模块

`chan_theory.py` 实现了缠论核心功能：

```python
from chan_theory import ChanTheoryAnalyzer

analyzer = ChanTheoryAnalyzer()
analyzer.load_klines(kline_dataframe)

# 获取分析结果
summary = analyzer.summary()
print(summary)
# 输出：
# {
#   'fractals': 分型数量,
#   'bis': 笔数量,
#   'zhongshus': 中枢数量,
#   'current_bi_direction': 当前笔方向,
#   'potential_bs_point': 'BS1' 或 'SS1' 等买卖点
# }
```

**缠论功能:**
- ✅ K 线包含处理
- ✅ 分型识别（顶/底分型）
- ✅ 笔的划分
- ✅ 中枢识别
- ✅ 买卖点判断（一类/二类/三类）

---

## 📈 策略开发模板

创建自己的策略：

```python
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, TargetPosTask
from chan_theory import ChanTheoryAnalyzer

api = TqApi(TqSim(), backtest=TqBacktest(...), auth=TqAuth("账户", "密码"))
klines = api.get_kline_serial("KQ.m@SHFE.rb", 60)
analyzer = ChanTheoryAnalyzer()

while True:
    api.wait_update()
    
    if api.is_changing(klines):
        # 更新缠论分析
        analyzer.load_klines(klines)
        summary = analyzer.summary()
        
        # 你的策略逻辑
        if summary['potential_bs_point'] == 'BS1':
            # 一类买点，开多
            pass
        
        # 或使用其他指标
        ma = klines.close.rolling(20).mean().iloc[-1]
        if klines.close.iloc[-1] > ma:
            # 价格在均线上方
            pass
```

---

## 🔧 常用命令

```powershell
# 查看已安装的包
py -m pip list | findstr tqsdk

# 升级 TQSDK
py -m pip install tqsdk -U -i https://pypi.tuna.tsinghua.edu.cn/simple

# 查看合约列表（在 Python 中）
from tqsdk import TqApi, TqAuth
api = TqApi(auth=TqAuth("账户", "密码"))
quotes = api.get_quote_list()
```

---

## ⚠️ 注意事项

1. **账户安全**: `config.py` 包含敏感信息，不要上传到 GitHub！
2. **回测 vs 实盘**: 回测结果不代表实盘表现，注意滑点和手续费
3. **风险控制**: 实盘前务必充分回测，设置止损
4. **网络要求**: 需要稳定的网络连接访问天勤服务器

---

## 📚 学习资源

- **TQSDK 官方文档**: https://doc.shinnytech.com/tqsdk/latest/
- **缠论原文**: 《缠中说禅》博客
- **期货公司列表**: https://www.shinnytech.com/articles/reference/tqsdk-brokers

---

## 🐱 关于咕噜

这是爸爸（用户）的专属量化助手咕噜开发的交易框架。

**有问题随时问咕噜！** 🐱📈
