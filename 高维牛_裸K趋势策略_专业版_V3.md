# 高维牛裸K日内5分钟趋势交易策略
# 基于《通向稳定盈利之路》《期货资金管理》核心精髓

> 版本：V3.0 高维牛专业版
> 核心：走势结构 + 裸K形态 + 量价配合 + 资金管理
> 周期：5分钟K线
> 品种：螺纹钢(RB)、热卷(HC)、焦炭(J)、甲醇(MA)
> 作者：咕噜 AI（学习高维牛系列文档）
> 日期：2026-03-19

---

## 一、核心理念（高维牛核心思想）

### 1.1 稳定盈利的终极奥义

> **"做期货就是做概率，做走势结构，做确定性"**
> 
> 高维牛核心观点：
> 1. **结构简单** - 交易系统要简单，信号明确
> 2. **操作简单** - 执行信号不犹豫
> 3. **心理简单** - 做到不贪不惧，无我交易

### 1.2 走势结构的绝对性

```
走势类型：
├── 上涨：高点不断太高，低点不断太高
├── 下跌：高点不断降低，低点不断降低  
└── 盘整：高点不创新高，低点不创新低

核心：走势终将完美
     - 上涨结束后，要么下跌要么盘整
     - 下跌结束后，要么上涨要么盘整
     - 盘整结束后，必然选择方向
```

### 1.3 资金管理是生命线

| 原则 | 具体做法 | 重要性 |
|------|----------|--------|
| **轻仓** | 单笔风险≤2%，建议1% | ⭐⭐⭐⭐⭐ |
| **顺势** | 只做趋势明确的方向 | ⭐⭐⭐⭐⭐ |
| **止损** | 绝不允许扛单 | ⭐⭐⭐⭐⭐ |
| **持仓** | 让利润奔跑 | ⭐⭐⭐⭐ |
| **休息** | 连续亏损必须停止 | ⭐⭐⭐ |

---

## 二、裸K核心元素（必须掌握）

### 2.1 K线基础

```
单根K线含义：
- 大阳线（>5%）：多方强势
- 大阴线（>5%）：空方强势
- 十字星：多空平衡，可能转折
- 上影线：上方有压力
- 下影线：下方有支撑
```

### 2.2 包含关系处理（关键！）

```
包含关系：两K线，一方包含另一方

向上处理（上涨趋势中）：
- 合并：取最高点的最高、收盘价的更高
- 结果：形成更强的K线

向下处理（下跌趋势中）：
- 合并：取最低点的最低、收盘价的更低  
- 结果：形成更强的K线
```

### 2.3 顶底分型（最关键信号）

```
顶分型（卖出信号）：
     ┌─┐
   ┌─┘ └─┐
  ─┘     └─  ← 中间K线最高
   └─┐ ┌─┘
     └─┘

条件：中间K线最高点最高 + 收盘价最低

底分型（买入信号）：
     └─┘
   ┌─┐ └─┐
  ─┘     └─  ← 中间K线最低
   ┌─┐ ┌─┘
     └─┘

条件：中间K线最低点最低 + 收盘价最高
```

---

## 三、入场条件（5分钟级别·高确定性）

### 3.1 趋势判断（必须先确认趋势）

```
多头趋势（满足≥3个条件）：
□ MA20方向向上
□ 价格在MA20均线上方
□ 低点不断太高（连接最近两个低点，后者高于前者）
□ 上涨角度>45度

空头趋势（满足≥3个条件）：
□ MA20方向向下
□ 价格在MA20均线下方
□ 高点不断降低（连接最近两个高点，后者低于前者）
□ 下跌角度>45度

无趋势（MA20走平）：禁止交易！
```

### 3.2 入场信号（精确点位）

#### 信号A：分型突破（首选高确定性）

```
【做多】
条件：
1. 确认多头趋势
2. 出现底分型
3. 底分型后价格突破最高点（收盘价突破）
4. 突破时成交量放大（量能确认）

入场点：突破K线的收盘价
止损点：底分型最低点下方0.5%

【做空】
条件：
1. 确认空头趋势
2. 出现顶分型
3. 顶分型后价格跌破最低点（收盘价跌破）
4. 跌破时成交量放大

入场点：跌破K线的收盘价
止损点：顶分型最高点上方0.5%
```

#### 信号B：回踩确认（稳健型）

```
【做多回踩】
1. 确认上涨趋势
2. 价格回踩MA20/MA60均线
3. 出现看涨K线组合（锤子、吞没、早晨之星）
4. 在均线支撑位企稳

入场点：K线企稳后收盘价
止损点：均线下方1%

【做空回抽】
1. 确认下跌趋势
2. 价格回抽MA20/MA60均线
3. 出现看跌K线组合（射击之星、吞没、黄昏星）
4. 在均线压力位受阻

入场点：K线受阻后收盘价
止损点：均线上方1%
```

#### 信号C：突破前高/低（动量型）

```
【突破高点做多】
1. 价格突破最近3根5分钟K线最高点
2. 突破时成交量>近期平均量能1.5倍
3. 突破K线实体部分>50%

入场点：突破K线收盘价
止损点：突破K线最低点下方0.5%

【跌破低点做空】
1. 价格跌破最近3根5分钟K线最低点
2. 跌破时成交量放大
3. 跌破K线实体部分>50%

入场点：跌破K线收盘价
止损点：跌破K线最高点上方0.5%
```

### 3.3 过滤条件（提高准确率）

```
【禁止入场】
□ 震荡行情（MA20走平）
□ 夜盘开盘30分钟内
□ 午盘收盘前15分钟
□ 涨停/跌停附近3跳内
□ 持仓量急剧下降
□ 心情不好/状态不佳

【优先入场】
□ 突破重要压力/支撑位
□ 教科书级标准形态
□ 连续下跌/上涨后的反转
□ 均线多头/空头排列
```

---

## 四、仓位管理（专业版）

### 4.1 账户分级与仓位

| 账户规模 | 单笔风险 | 最大持仓 | 单日止损 |
|----------|----------|----------|----------|
| 1-3万    | 1%       | 1个合约  | 3%       |
| 3-10万   | 1%       | 2个合约  | 3%       |
| 10-50万  | 0.8%     | 3个合约  | 2.5%     |
| 50万以上 | 0.5%     | 5个合约  | 2%       |

### 4.2 手数精确计算

```python
# 公式
单笔风险金额 = 账户权益 × 风险比例
止损价差 = |入场价 - 止损价|
每手风险 = 止损价差 × 合约乘数 × 保证金比例
开仓手数 = 单笔风险金额 / 每手风险

# 示例（螺纹钢）
账户：100,000元  风险比例：1% = 1000元
入场价：4200    止损价：4160  价差：40点
每手风险：40 × 10 × 10% = 40元
开仓手数：1000 / 40 = 25手（实际不超过10手）
```

### 4.3 加仓规则（趋势延续时）

```
第1次加仓：浮盈3%后，加原仓位50%
第2次加仓：再浮盈3%后，加原仓位30%
止损移动：第一次加仓后，移动到保本
总仓位：不超过60%
```

---

## 五、出场规则（精确止盈止损）

### 5.1 止损规则

```
【硬止损】（无条件执行）
- 收盘跌破MA20 → 无条件平仓
- 底分型最低点被跌破 → 平多
- 顶分型最高点被涨破 → 平空
- 单笔亏损>2% → 必须平仓

【软止损】
- 浮盈回撤50% → 移动到保本
- 达到目标位 → 部分止盈
```

### 5.2 止盈规则（分批离场）

```
【方案A：固定目标】
- 第1目标：+2% 止盈1/3
- 第2目标：+4% 止盈1/3  
- 第3目标：+6% 止盈最后1/3

【方案B：移动止盈】
- 浮盈>3%，价格跌破MA5 → 止盈1/3
- 浮盈>5%，价格跌破MA10 → 止盈1/3
- 浮盈>8%，价格跌破MA20 → 全部平仓

【方案C：形态终结】
- 出现反向顶/底分型
- 趋势破坏（高低点被突破）
- 巨量反转（量能异常放大）
```

### 5.3 时间规则

```
【日内规则】
- 14:45后：只平仓不开新仓
- 夜盘21:00-21:30：不新开仓
- 02:30前：必须全部平仓

【持仓规则】
- 有浮盈尽量持到底
- 收盘前5分钟检查：浮盈<1%必须平
- 周末：不超过20%仓位
```

---

## 六、风控体系（生命线）

### 6.1 每日风控

```
单日亏损≥2% → 停止当日交易
单日交易>5次 → 停止交易
连续2天亏损 → 强制休息1天
```

### 6.2 每周风控

```
周亏损≥5% → 停止本周交易
周交易>20次 → 仓位减半
```

### 6.3 每月风控

```
月亏损≥10% → 停止本月交易
月回撤≥15% → 全面检修交易系统
```

### 6.4 十大禁止（高压线）

```
❌ 逆势抄底摸顶
❌ 亏损加仓（摊平成本）
❌ 死扛不止损
❌ 重仓（>30%）
❌ 频繁交易（>10次/日）
❌ 情绪化交易
❌ 报复性交易
❌ 听消息交易
❌ 臆想交易
❌ 不复盘总结
```

---

## 七、天勤量化完整代码

```python
# -*- coding: utf-8 -*-
"""
高维牛裸K日内5分钟趋势策略 - 专业版
基于走势结构 + 裸K形态 + 量价配合
天勤量化 TQSDK
"""

from tqsdk import TqApi, TqAuth
from tqsdk.ta import MA, MACD, BOLL
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import sys

class GaoWeiNiuStrategy:
    """高维牛裸K趋势策略"""
    
    def __init__(self, config):
        # 基础配置
        self.api = TqApi(auth=TqAuth(config['account'], config['password']))
        self.symbols = config.get('symbols', ['SHFE.rb2505'])
        self.account_equity = config['account_equity']
        
        # 策略参数
        self.risk_ratio = config.get('risk_ratio', 0.01)        # 1%风险
        self.max_position = config.get('max_position', 30)      # 最大30%仓位
        self.max_daily_loss = config.get('max_daily_loss', 0.02)  # 日最大2%
        self.stop_loss_pct = config.get('stop_loss_pct', 0.005)  # 0.5%止损
        
        # 均线周期
        self.ma_period = config.get('ma_period', 20)
        
        # 止盈目标
        self.tp_levels = config.get('tp_levels', [0.02, 0.04, 0.06])
        
        # 状态
        self.positions = {}
        self.daily_pnl = 0
        self.daily_trades = 0
        
    # ==================== 核心计算 ====================
    
    def get_klines(self, symbol, period=5*60*1000, length=100):
        """获取K线"""
        return self.api.get_kline_serial(symbol, period, length)
    
    def calc_ma(self, klines, period=20):
        """计算均线"""
        return MA(klines, period)
    
    def check_trend(self, klines):
        """判断趋势"""
        ma = self.calc_ma(klines, self.ma_period)
        ma_val = ma.iloc[-1]['MA']
        current = klines.iloc[-1]['close']
        
        # 取最近两个低点
        if len(klines) >= 20:
            lows = klines['low'].tail(10)
            # 简单的趋势判断
            if current > ma_val and ma_val > ma.iloc[-5]['MA']:
                return 'uptrend'
            elif current < ma_val and ma_val < ma.iloc[-5]['MA']:
                return 'downtrend'
        return 'sideway'
    
    def find_fractal(self, klines):
        """
        识别顶底分型
        返回: 'bottom', 'top', 'none'
        """
        if len(klines) < 5:
            return 'none'
        
        # 最近5根K线
        recent = klines.tail(5).reset_index(drop=True)
        
        # 中间K线
        mid = recent.iloc[2]
        before = recent.iloc[1]
        after = recent.iloc[3]
        
        # 底分型
        if (mid['low'] < before['low'] and 
            mid['low'] < after['low'] and
            mid['close'] > before['close'] and 
            mid['close'] > after['close']):
            return 'bottom'
        
        # 顶分型
        if (mid['high'] > before['high'] and 
            mid['high'] > after['high'] and
            mid['close'] < before['close'] and 
            mid['close'] < after['close']):
            return 'top'
        
        return 'none'
    
    def check_breakout(self, klines, direction='up'):
        """检查突破"""
        if len(klines) < 4:
            return False, 0
        
        recent = klines.tail(3)
        
        if direction == 'up':
            high = recent['high'].max()
            current_close = klines.iloc[-1]['close']
            return current_close > high, high
        else:
            low = recent['low'].min()
            current_close = klines.iloc[-1]['close']
            return current_close < low, low
    
    def check_volume(self, klines):
        """量能检查"""
        if len(klines) < 20:
            return False
        
        avg_vol = klines['volume'].iloc[-20:].mean()
        current_vol = klines.iloc[-1]['volume']
        return current_vol > avg_vol * 1.5
    
    # ==================== 交易信号 ====================
    
    def get_entry_signal(self, symbol):
        """获取入场信号"""
        klines = self.get_klines(symbol)
        
        # 1. 趋势判断
        trend = self.check_trend(klines)
        
        # 2. 分型识别
        fractal = self.find_fractal(klines)
        
        # 3. 突破检查
        up_break, up_level = self.check_breakout(klines, 'up')
        down_break, down_level = self.check_breakout(klines, 'down')
        
        # 4. 量能确认
        vol_ok = self.check_volume(klines)
        
        current = klines.iloc[-1]['close']
        
        # ===== 入场条件 =====
        
        # 做多：上涨趋势 + 底分型 + 突破 + 量能
        if (trend == 'uptrend' and 
            fractal == 'bottom' and 
            up_break and 
            vol_ok):
            
            # 止损：底分型最低点
            stop = klines.tail(5)['low'].min() * 0.995
            
            return {
                'direction': 'long',
                'entry': current,
                'stop_loss': stop,
                'signal': f'上涨趋势+底分型突破+放量'
            }
        
        # 做空：下跌趋势 + 顶分型 + 跌破 + 量能
        if (trend == 'downtrend' and 
            fractal == 'top' and 
            down_break and 
            vol_ok):
            
            # 止损：顶分型最高点
            stop = klines.tail(5)['high'].max() * 1.005
            
            return {
                'direction': 'short',
                'entry': current,
                'stop_loss': stop,
                'signal': f'下跌趋势+顶分型跌破+放量'
            }
        
        return None
    
    def get_exit_signal(self, symbol):
        """获取出场信号"""
        if symbol not in self.positions:
            return None
        
        pos = self.positions[symbol]
        klines = self.get_klines(symbol)
        current = klines.iloc[-1]['close']
        
        entry = pos['entry']
        direction = pos['direction']
        
        # 计算盈亏
        if direction == 'long':
            pnl_pct = (current - entry) / entry
        else:
            pnl_pct = (entry - current) / entry
        
        # 1. 止损
        if direction == 'long' and current < pos['stop_loss']:
            return {'action': 'stop_loss', 'reason': '触发止损'}
        if direction == 'short' and current > pos['stop_loss']:
            return {'action': 'stop_loss', 'reason': '触发止损'}
        
        # 2. 止盈
        for i, tp in enumerate(self.tp_levels):
            tp_key = f'tp{i}_done'
            if pnl_pct >= tp and not pos.get(tp_key, False):
                return {
                    'action': 'partial_tp', 
                    'level': i+1, 
                    'target': tp,
                    'reason': f'止盈{i+1}'
                }
        
        # 3. 趋势破坏
        trend = self.check_trend(klines)
        if direction == 'long' and trend != 'uptrend':
            return {'action': 'trend_break', 'reason': '趋势破坏'}
        if direction == 'short' and trend != 'downtrend':
            return {'action': 'trend_break', 'reason': '趋势破坏'}
        
        return None
    
    # ==================== 仓位计算 ====================
    
    def calc_position_size(self, symbol, risk_amount, stop_price):
        """计算开仓手数"""
        quote = self.api.get_quote(symbol)
        entry = quote.last_price
        price_diff = abs(entry - stop_price)
        
        if price_diff == 0:
            price_diff = entry * self.stop_loss_pct
        
        contract = self.api.get_contract(symbol)
        multiplier = contract.volume_tick
        margin = contract.margin
        
        size = risk_amount / (price_diff * multiplier * margin)
        
        # 限制最大手数
        max_size = (self.account_equity * self.max_position / 100) / (entry * margin)
        
        return min(int(size), int(max_size))
    
    # ==================== 交易执行 ====================
    
    def open_position(self, symbol, signal):
        """开仓"""
        if not self.can_trade():
            return
        
        entry = signal['entry']
        stop = signal['stop_loss']
        
        risk_amount = self.account_equity * self.risk_ratio
        size = self.calc_position_size(symbol, risk_amount, stop)
        
        if size == 0:
            return
        
        # 开仓
        if signal['direction'] == 'long':
            self.api.insert_order(symbol, 'BUY', 'OPEN', size, entry)
        else:
            self.api.insert_order(symbol, 'SELL', 'OPEN', size, entry)
        
        # 记录
        self.positions[symbol] = {
            'direction': signal['direction'],
            'entry': entry,
            'stop_loss': stop,
            'size': size,
            'signal': signal['signal'],
            'entry_time': datetime.now()
        }
        
        print(f"开仓: {symbol} {signal['direction']} {size}手 @ {entry} 信号:{signal['signal']}")
        self.daily_trades += 1
    
    def close_position(self, symbol, exit_info):
        """平仓"""
        if symbol not in self.positions:
            return
        
        pos = self.positions[symbol]
        quote = self.api.get_quote(symbol)
        current = quote.last_price
        
        # 平仓
        if pos['direction'] == 'long':
            self.api.insert_order(symbol, 'SELL', 'CLOSE', pos['size'], current)
            pnl = (current - pos['entry']) * pos['size']
        else:
            self.api.insert_order(symbol, 'BUY', 'CLOSE', pos['size'], current)
            pnl = (pos['entry'] - current) * pos['size']
        
        self.daily_pnl += pnl
        print(f"平仓: {symbol} {exit_info['action']} {exit_info['reason']} 盈亏: {pnl:.2f}")
        
        del self.positions[symbol]
    
    def can_trade(self):
        """检查是否可交易"""
        # 日亏损限制
        if self.daily_pnl < -self.account_equity * self.max_daily_loss:
            print(f"日亏损达到上限，停止交易")
            return False
        
        # 交易次数限制
        if self.daily_trades >= 5:
            print(f"今日交易次数已达上限")
            return False
        
        return True
    
    def run(self):
        """主循环"""
        print("="*60)
        print("高维牛裸K日内5分钟趋势策略启动")
        print("="*60)
        
        while True:
            try:
                for symbol in self.symbols:
                    # 检查持仓
                    pos = self.api.get_position(symbol)
                    net = pos.pos_long - pos.pos_short
                    
                    if net == 0:
                        # 无持仓，检查入场
                        if self.can_trade():
                            signal = self.get_entry_signal(symbol)
                            if signal:
                                self.open_position(symbol, signal)
                    else:
                        # 有持仓，检查出场
                        if symbol in self.positions:
                            exit_sig = self.get_exit_signal(symbol)
                            if exit_sig:
                                self.close_position(symbol, exit_sig)
                
                import time
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("策略停止")
                break
            except Exception as e:
                print(f"错误: {e}")
                import time
                time.sleep(30)


# ==================== 启动 ====================

if __name__ == "__main__":
    config = {
        'account': '你的天勤账号',
        'password': '你的密码',
        'account_equity': 100000,    # 10万
        'risk_ratio': 0.01,          # 1%
        'max_position': 30,           # 30%
        'max_daily_loss': 0.02,       # 2%
        
        'symbols': [
            'SHFE.rb2505',   # 螺纹钢
            'SHFE.hc2505',  # 热卷
            'DCE.j2505',    # 焦炭
            'CZCE.ma2505',  # 甲醇
        ],
        
        'ma_period': 20,
        'stop_loss_pct': 0.005,
        'tp_levels': [0.02, 0.04, 0.06],
    }
    
    strategy = GaoWeiNiuStrategy(config)
    strategy.run()
```

---

## 十、矢量型交易策略（死鱼2核心精髓）

### 10.1 矢量型核心理念

> **"走势结构不变，矢量2"** - 死鱼2

矢量型交易的核心：
- **矢量方向**：价格运动的方向（向上/向下）
- **矢量力度**：价格运动的动能（强弱）
- **结构不变**：在趋势延续中，矢量方向保持不变

### 10.2 矢量判断标准

```
矢量向上（做多条件）：
□ 每一波上涨的高点都高于上一波
□ 每一波下跌的低点都高于上一波
□ 均线多头排列（MA5>MA10>MA20>MA60）
□ 成交量在上涨时放大

矢量向下（做空条件）：
□ 每一波下跌的低点都低于上一波
□ 每一波上涨的高点都低于上一波
□ 均线空头排列（MA5<MA10<MA20<MA60）
□ 成交量在下跌时放大
```

### 10.3 矢量衰竭信号

```
上涨矢量衰竭：
1. 价格创新高，但MACD不创新高（顶背离）
2. 上涨速度明显放缓（角度变小）
3. 成交量萎缩
4. 出现射击之星/十字星

下跌矢量衰竭：
1. 价格创新低，但MACD不创新低（底背离）
2. 下跌速度明显放缓
3. 成交量萎缩
4. 出现锤子/十字星
```

### 10.4 矢量交易入场点

```
【顺势矢量入场】
1. 确认矢量方向（连续3波同向运动）
2. 等待回调结束（回调不破前低/高）
3. 出现反转K线（锤子/吞没）
4. 突破回调区间高点/低点

【转折矢量入场】
1. 出现矢量衰竭信号
2. 出现标准顶/底分型
3. 突破关键支撑/压力位
4. 放量确认
```

### 10.5 矢量型四天两倍战法（随风核心）

> 源自Q089：矢量型四天两倍

```
核心逻辑：
- 第一天：确认趋势方向
- 第二天：回调后继续上涨/下跌
- 第三天：加速行情（放量）
- 第四天：趋势延续或反转

关键点：
1. 趋势明确后回调不破支撑
2. 再次启动时成交量放大
3. 突破前高/低时入场
4. 止损设在回调最低点
```

### 10.6 矢量策略参数

```python
# 矢量确认参数
VECTOR_LOOKBACK = 5  # 查看最近5波
VECTOR_MOMENTUM = 0.6  # 力度阈值

# 矢量衰竭参数  
DIVERGENCE_THRESHOLD = 0.1  # 背离阈值
VOLUME_DROP_RATIO = 0.7  # 量能萎缩比例
```

---

## 八、交易检查清单

### 交易前
- [ ] 趋势方向明确吗？
- [ ] 入场信号≥3个条件满足？
- [ ] 仓位计算正确？
- [ ] 止损位明确？

### 交易后
- [ ] 按系统执行？
- [ ] 止损坚决？
- [ ] 记录交易日志？
- [ ] 每日复盘？

---

## 九、总结

高维牛核心思想：
1. **走势结构**是根本 - 学会看趋势
2. **裸K形态**是信号 - 顶底分型最可靠
3. **量价配合**是确认 - 放量突破更有效
4. **资金管理**是生命 - 轻仓才能活得久

**稳定盈利 = 简单的系统 + 严格的执行 + 良好的心态**

---

这个版本够专业吗？请爸爸确认一下核心逻辑。🐱