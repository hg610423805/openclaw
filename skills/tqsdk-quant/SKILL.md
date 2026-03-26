# 天勤量化回测技能 (TqSdk Quant)

## 激活条件
当用户提到：
- 量化回测、策略回测、期货回测
- TqSdk、天勤量化、快期量化
- 写策略代码、量化策略开发
- 回测报告、量化分析

## 核心知识

### 天勤量化 (TqSdk) 关键 API

#### 1. 初始化
```python
from tqsdk import TqApi, TqAuth, TqBacktest, TqSim

# 回测模式
api = TqApi(
    auth=TqAuth("账号", "密码"),
    backtest=TqBacktest(start_dt=start_date, end_dt=end_date)
)

# 模拟交易
api = TqApi(auth=TqAuth("账号", "密码"))
```

#### 2. 获取 K 线数据
```python
# 参数：合约代码，K 线根数，duration_seconds=周期 (秒)
klines = api.get_kline_serial(symbol, data_length, duration_seconds=300)  # 5 分钟
klines_30m = api.get_kline_serial(symbol, data_length, duration_seconds=1800)  # 30 分钟
```

#### 3. 常用指标
```python
from tqsdk import tafunc

# EMA/EXPMA
ema13 = tafunc.ema(close_series, 13)

# KDJ (需要自己计算)
def calculate_kdj(df, period=9):
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    rsv = (df['close'] - low_min) / (high_max - low_min) * 100
    k = rsv.ewm(com=2, adjust=False).mean()
    d = k.ewm(com=2, adjust=False).mean()
    j = 3 * k - 2 * d
    return k, d, j
```

#### 4. 主力连续合约代码
```python
# 格式：KQ.m@交易所.品种代码 (大写)
"KQ.m@CZCE.SM"  # 锰硅主连 (郑州)
"KQ.m@CZCE.FG"  # 玻璃主连 (郑州)
"KQ.m@DCE.C"    # 玉米主连 (大连)
"KQ.m@SHFE.rb"  # 螺纹钢主连 (上海)
```

#### 5. 品种参数
```python
SYMBOL_CONFIG = {
    "SM": {"name": "锰硅", "tick": 2, "multiplier": 5, "exchange": "CZCE"},
    "FG": {"name": "玻璃", "tick": 1, "multiplier": 20, "exchange": "CZCE"},
    "C":  {"name": "玉米", "tick": 1, "multiplier": 10, "exchange": "DCE"},
    "rb": {"name": "螺纹钢", "tick": 1, "multiplier": 10, "exchange": "SHFE"},
}
```

### 策略开发规范

#### 均线+KDJ 策略模板
```python
# 30 分钟判断趋势
bullish = expma13_30 > expma26_30
bearish = expma13_30 < expma26_30

# 5 分钟找入场点
# 做多：30 分钟多头 + 30 分钟 J<20 + 5 分钟金叉或 J<20
# 做空：30 分钟空头 + 30 分钟 J>80 + 5 分钟死叉或 J>80

# 出场：5 分钟 EXPMA 反向交叉
```

#### 回测配置
```python
# 默认配置
START_DATE = datetime.now() - timedelta(days=180)  # 180 天
END_DATE = datetime.now()
INITIAL_CAPITAL = 100000  # 10 万初始资金
COMMISSION_RATIO = 0.00006  # 万分之 0.6
SLIPPAGE = 1  # 1 个 tick 滑点
```

### 常见错误避免

1. **合约代码大小写**：必须大写，如 `KQ.m@CZCE.SM` 不是 `KQ.m@CZCE.sm`
2. **Pandas 频率**：用 `'30min'` 不是 `'30T'`
3. **get_kline_serial 参数**：`api.get_kline_serial(symbol, data_length, duration_seconds=300)`
4. **日期格式**：TqBacktest 需要 `datetime` 对象，不是字符串
5. **Unicode 输出**：Windows 终端避免用 emoji，用 `[OK]` `[ERROR]` 等

### HTML 报告模板
包含：
- 核心统计（总收益、胜率、交易次数等）
- 月度收益曲线
- 品种表现排名
- 交易明细表格
- 资金曲线图

## 默认配置（用户 17699）

- **天勤账号**：13163715864
- **回测周期**：默认 180 天
- **初始资金**：100,000 元
- **关注品种**：锰硅 (SM)、玻璃 (FG)、玉米 (C)、螺纹钢 (rb)
- **策略类型**：均线+KDJ 趋势跟踪
- **报告格式**：HTML 交互式报告

## 文件位置
- 策略代码：`quant/strategies/`
- 回测结果：`quant/strategies/backtest_results/`
- 配置文件：`quant/config.py`
