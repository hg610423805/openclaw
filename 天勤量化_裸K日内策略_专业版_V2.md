# 裸K日内5分钟趋势交易策略 - 专业版
# 核心：基于走势结构 + 裸K形态 + 量价配合

> 版本：V2.0 专业版
> 周期：5分钟K线
> 品种：螺纹钢(RB)、热卷(HC)、焦炭(J)、甲醇(MA)
> 作者：咕噜 AI
> 日期：2026-03-19

---

## 一、策略理念

### 1.1 核心理念
> **"走势终将完美"**
> - 裸K是最真实的价格语言
> - 形态是资金博弈的结果
> - 顺势而为，不预测只跟随

### 1.2 交易哲学
```
不抄底 → 只做转折后的确认
不摸顶 → 只做跌破后的确认
不臆想 → 只看信号行动
不扛单 → 止损是信仰
```

---

## 二、裸K核心概念

### 2.1 基础元素（必学）

| 元素 | 含义 | 重要性 |
|------|------|--------|
| **K线** | 开盘-收盘-最高-最低 | ⭐⭐⭐ |
| **均线** | MA5/MA10/MA20/MA60 | ⭐⭐⭐ |
| **成交量** | 量在价先 | ⭐⭐⭐ |
| **持仓量** | 主力动向 | ⭐⭐ |

### 2.2 关键形态（必须掌握）

#### A. 顶底分型（最关键信号）
```
顶分型定义：
- 中间K线最高价 = 3根K线最高
- 中间K线收盘 < 前后K线收盘

底分型定义：
- 中间K线最低价 = 3根K线最低  
- 中间K线收盘 > 前后K线收盘
```

#### B. 包含关系（处理复杂形态）
```
向上处理：
- 下跌趋势中的包含 → 合并后向下
- 取两K线最高点更高、收盘价更低

向下处理：
- 上涨趋势中的包含 → 合并后向上
- 取两K线最低点更低、收盘价更高
```

#### C. 走势类型
| 类型 | 特征 | 交易方向 |
|------|------|----------|
| **上涨** | 高点不断抬高，低点不断太高 | 只做多 |
| **下跌** | 高点不断降低，低点不断降低 | 只做空 |
| **盘整** | 高点不创新高低点不创新低 | 不做/看戏 |

### 2.3 力度判断（关键）

```
力度衰竭信号：
1. 背离：价格创新高/低，但MACD/RSI不创新高/低
2. 加速：连续小K线后出现大K线，可能是最后一涨/跌
3. 量价背离：放量不涨/跌
4. 长上影/长下影：上攻/下跌无力
```

---

## 三、入场条件（5分钟级别）

### 3.1 趋势确认（必须满足2个以上）

```
多头趋势（做多条件）：
□ MA20向上运行
□ 价格在MA20均线上方
□ 最近一个完整上涨段未被跌破
□ 低点不断太高

空头趋势（做空条件）：
□ MA20向下运行
□ 价格在MA20均线下方
□ 最近一个完整下跌段未被涨破
□ 高点不断降低
```

### 3.2 入场信号（精确点位）

#### 信号A：底分型+突破（首选）
```
做多信号：
1. 出现底分型（3根K线）
2. 底分型后价格突破底分型最高点（收盘价突破）
3. 突破时成交量放大（量能配合）
4. 止损位：底分型最低点下方1跳

做空信号：
1. 出现顶分型（3根K线）
2. 顶分型后价格跌破顶分型最低点（收盘价跌破）
3. 跌破时成交量放大
4. 止损位：顶分型最高点上方1跳
```

#### 信号B：趋势回踩确认
```
做多回踩：
1. 上涨趋势中，价格回踩MA20或MA60
2. 出现看涨K线组合（锤子/吞没/早晨之星）
3. 在均线支撑位企稳
4. 止损：均线下方1%

做空回抽：
1. 下跌趋势中，价格回抽MA20或MA60
2. 出现看跌K线组合（射击之星/吞没/黄昏星）
3. 在均线压力位受阻
4. 止损：均线上方1%
```

#### 信号C：突破前高低点
```
突破高点做多：
1. 价格突破最近3根5分钟K线最高点
2. 突破时成交量 > 近期平均量能1.5倍
3. 止损：突破K线最低点下方1%

跌破低点做空：
1. 价格跌破最近3根5分钟K线最低点
2. 跌破时成交量放大
3. 止损：跌破K线最高点上方1%
```

### 3.3 过滤条件（提高准确率）

```
以下情况禁止入场：
□ 震荡行情中（MA20走平）
□ 涨停/跌停附近
□ 夜盘开盘30分钟内
□ 午盘收盘前15分钟
□ 持仓量急剧下降时

以下情况优先入场：
□ 突破关键压力/支撑位
□ 形态非常标准（教科书级）
□ 前期有明显的趋势运行
```

---

## 四、仓位管理（专业版）

### 4.1 账户分级

| 账户规模 | 单笔风险 | 最大持仓 | 单日最大亏损 |
|----------|----------|----------|--------------|
| 1-5万    | 1%       | 2个合约  | 3%           |
| 5-20万   | 0.8%     | 3个合约  | 2.5%         |
| 20万以上  | 0.5%     | 5个合约  | 2%           |

### 4.2 手数计算公式
```python
# 精确手数计算
单笔风险 = 账户权益 × 风险比例
止损跳数 = abs(入场价 - 止损价) / 最小变动价位
每手风险 = 止损跳数 × 合约乘数 × 最小变动价位
开仓手数 = 单笔风险 / 每手风险

# 示例
账户：10万  风险：1% = 1000元
螺纹钢：入场4200  止损4180  跳数20
每手风险：20 × 10 × 1 = 200元
开仓手数：1000 / 200 = 5手
```

### 4.3 加仓规则（趋势延续时）
```
第1次加仓：浮盈2%后，加原仓位50%
第2次加仓：再浮盈2%后，加原仓位30%
总仓位不超过60%
止损移动到保本位置
```

---

## 五、出场规则（精确）

### 5.1 止损（铁律）
```
硬止损：
- 底分型最低点下方1% → 无条件止损
- 突破K线最低点下方1% → 无条件止损
- 收盘跌破MA20 → 无条件止损

软止损：
- 浮盈后回撤50% → 移动到保本
- 达到目标为浮盈的30% → 部分止盈
```

### 5.2 止盈（分批离场）
```
方案A：固定目标
- 第1目标：+2% 止盈1/3
- 第2目标：+4% 止盈1/3
- 第3目标：+6% 止盈最后1/3

方案B：移动止盈
- 价格跌破MA5 止盈1/3
- 价格跌破MA10 止盈1/3
- 价格跌破MA20 全部平仓

方案C：形态终结
- 出现反向顶/底分型
- 趋势破坏（高低点被突破）
- 巨量反转（量能异常）
```

### 5.3 特殊处理
```
收盘前规则：
- 14:45前不平仓（持有到收盘）
- 14:45后浮盈>2%可持
- 14:45后浮盈<1%必须平

夜盘规则：
- 21:00-21:30 不新开仓
- 23:30后只减仓不加仓
- 02:30前必须全部平仓
```

---

## 六、风控体系（生命线）

### 6.1 每日风控
```
单日亏损达到2% → 停止交易
单日交易超过5次 → 停止交易
连续2天亏损 → 强制休息1天
```

### 6.2 每周风控
```
周亏损达到5% → 停止交易
周交易超过20次 → 减少仓位50%
```

### 6.3 每月风控
```
月亏损达到10% → 停止交易
月回撤超过15% → 重新核算系统
```

### 6.4 禁止清单（必须遵守）
```
❌ 逆势抄底摸顶
❌ 亏损加仓（摊平成本）
❌ 死扛不止损
❌ 重仓（>30%）
❌ 频繁交易（>10次/日）
❌ 情绪化交易
❌ 报复性交易
❌ 听消息交易
```

---

## 七、复盘模板（每日必做）

### 7.1 交易记录表
```
日期 | 品种 | 方向 | 开仓价 | 平仓价 | 盈亏 | 止损点 | 信号类型 | 备注
------|------|------|--------|--------|------|--------|----------|----
```

### 7.2 复盘问题
```
1. 今日交易是否按系统执行？
2. 哪笔交易最符合系统？为什么？
3. 哪笔交易不符合系统？为什么？
4. 今日最大亏损原因？
5. 明日改进点？
```

---

## 八、天勤量化代码（专业完整版）

```python
# -*- coding: utf-8 -*-
"""
裸K日内5分钟趋势交易策略 - 专业版
天勤量化 TQSDK
"""

from tqsdk import TqApi, TqAuth, TqChan
from tqsdk.ta import MA, MACD, BOLL
import pandas as pd
import numpy as np
from datetime import datetime, time
import sys

class NakedKStrategy:
    """裸K日内趋势策略"""
    
    def __init__(self, config):
        # ===== 基础配置 =====
        self.api = TqApi(
            auth=TqAuth(config['account'], config['password']),
            webgws_url=config.get('webgws_url', 'wss://api.tqapi.com/ws')
        )
        self.symbols = config.get('symbols', ['SHFE.rb2505'])  # 多品种
        self.account_equity = config['account_equity']  # 账户权益
        
        # ===== 策略参数 =====
        self.risk_ratio = config.get('risk_ratio', 0.01)      # 1%风险
        self.max_position = config.get('max_position', 30)     # 最大仓位30%
        self.max_daily_loss = config.get('max_daily_loss', 0.03)  # 日最大3%
        
        # 均线周期
        self.ma_short = config.get('ma_short', 5)
        self.ma_mid = config.get('ma_mid', 20)
        self.ma_long = config.get('ma_long', 60)
        
        # 止损止盈
        self.stop_loss_pct = config.get('stop_loss_pct', 0.01)   # 1%止损
        self.profit_targets = config.get('profit_targets', [0.02, 0.04, 0.06])
        
        # 交易时间
        self.morning_start = time(9, 0)
        self.morning_end = time(11, 30)
        self.afternoon_start = time(13, 30)
        self.afternoon_end = time(15, 0)
        self.night_start = time(21, 0)
        self.night_end = time(2, 30)
        
        # ===== 状态变量 =====
        self.positions = {}      # {symbol: position_info}
        self.daily_pnl = 0       # 今日盈亏
        self.daily_trade_count = 0  # 今日交易次数
        
    # ==================== 核心计算 ====================
    
    def get_klines(self, symbol, period=5*60*1000, length=100):
        """获取K线数据"""
        return self.api.get_kline_serial(symbol, period, length)
    
    def calculate_ma(self, klines, period):
        """计算均线"""
        return MA(klines, period)
    
    def check_trend(self, klines):
        """判断趋势方向"""
        ma20 = self.calculate_ma(klines, self.ma_mid)
        ma60 = self.calculate_ma(klines, self.ma_long)
        
        current = klines.iloc[-1]
        ma20_val = ma20.iloc[-1]['MA']
        ma60_val = ma60.iloc[-1]['MA']
        
        # 趋势判断
        if current['close'] > ma20_val > ma60_val:
            return 'uptrend'
        elif current['close'] < ma20_val < ma60_val:
            return 'downtrend'
        return 'sideway'
    
    def identify_pattern(self, klines, lookback=5):
        """
        识别裸K形态
        返回: 'bottom_fractal', 'top_fractal', 'none'
        """
        if len(klines) < lookback:
            return 'none'
        
        # 取最近lookback根K线
        recent = klines.iloc[-lookback:]
        
        # 底分型：中间K线最低，前后K线更高
        if len(recent) >= 3:
            mid_idx = lookback // 2
            mid = recent.iloc[mid_idx]
            before = recent.iloc[mid_idx - 1]
            after = recent.iloc[mid_idx + 1]
            
            # 底分型条件
            if (mid['low'] < before['low'] and mid['low'] < after['low'] and
                mid['close'] > before['close'] and mid['close'] > after['close']):
                return 'bottom_fractal'
            
            # 顶分型条件
            if (mid['high'] > before['high'] and mid['high'] > after['high'] and
                mid['close'] < before['close'] and mid['close'] < after['close']):
                return 'top_fractal'
        
        return 'none'
    
    def check_breakout(self, klines, direction='up'):
        """
        检查突破
        direction: 'up' or 'down'
        """
        if len(klines) < 4:
            return False
        
        recent = klines.iloc[-3:]
        current = klines.iloc[-1]
        
        if direction == 'up':
            # 突破前3根K线最高点
            highest = recent['high'].max()
            return current['close'] > highest
        else:
            # 跌破前3根K线最低点
            lowest = recent['low'].min()
            return current['close'] < lowest
    
    def check_volume_confirm(self, klines):
        """量能确认"""
        if len(klines) < 20:
            return False
        
        # 近期平均量能
        avg_volume = klines['volume'].iloc[-20:].mean()
        current_volume = klines.iloc[-1]['volume']
        
        # 放量1.5倍以上
        return current_volume > avg_volume * 1.5
    
    def check_momentum(self, klines):
        """动力检查（可选）"""
        try:
            macd = MACD(klines, 12, 26, 9)
            diff = macd.iloc[-1]['diff']
            dea = macd.iloc[-1]['dea']
            
            # 多头：diff > dea > 0
            if diff > dea and dea > 0:
                return 'bullish'
            # 空头：diff < dea < 0
            elif diff < dea and dea < 0:
                return 'bearish'
        except:
            pass
        return 'neutral'
    
    # ==================== 交易执行 ====================
    
    def can_trade(self):
        """检查是否可交易"""
        now = datetime.now().time()
        
        # 夜盘开盘30分钟内不交易
        if self.night_start <= now <= time(21, 30):
            return False
        
        # 收盘前15分钟不交易
        if time(14, 45) <= now <= time(15, 0):
            return False
            
        # 检查日亏损
        if self.daily_pnl < -self.account_equity * self.max_daily_loss:
            print(f"日亏损达到上限，停止交易")
            return False
            
        return True
    
    def calculate_position_size(self, symbol, entry_price, stop_price):
        """计算开仓手数"""
        risk_amount = self.account_equity * self.risk_ratio
        contract = self.api.get_contract(symbol)
        
        price_diff = abs(entry_price - stop_price)
        if price_diff == 0:
            price_diff = entry_price * 0.01  # 默认1%
        
        # 手数 = 风险金额 / (价差 × 乘数)
        multiplier = contract.volume_tick
        margin = contract.margin
        
        size = risk_amount / (price_diff * multiplier * margin)
        return int(size)
    
    def check_entry_signal(self, symbol):
        """检查入场信号"""
        klines = self.get_klines(symbol)
        
        # 1. 趋势判断
        trend = self.check_trend(klines)
        
        # 2. 形态识别
        pattern = self.identify_pattern(klines)
        
        # 3. 突破确认
        up_break = self.check_breakout(klines, 'up')
        down_break = self.check_breakout(klines, 'down')
        
        # 4. 量能确认
        volume_ok = self.check_volume_confirm(klines)
        
        # 5. 动力确认（可选）
        momentum = self.check_momentum(klines)
        
        # ===== 入场条件 =====
        
        # 做多条件：上涨趋势 + 底分型 + 突破 + 量能
        if (trend == 'uptrend' and 
            pattern == 'bottom_fractal' and 
            up_break and 
            volume_ok):
            # 计算止损价（底分型最低点下方）
            klines = self.get_klines(symbol, length=20)
            lows = klines['low'].iloc[-5:]
            stop_loss = lows.min() * 0.998  # 下方0.2%
            
            return {
                'direction': 'long',
                'entry': klines.iloc[-1]['close'],
                'stop_loss': stop_loss,
                'reason': f'上涨趋势+底分型突破+放量'
            }
        
        # 做空条件
        if (trend == 'downtrend' and 
            pattern == 'top_fractal' and 
            down_break and 
            volume_ok):
            klines = self.get_klines(symbol, length=20)
            highs = klines['high'].iloc[-5:]
            stop_loss = highs.max() * 1.002  # 上方0.2%
            
            return {
                'direction': 'short',
                'entry': klines.iloc[-1]['close'],
                'stop_loss': stop_loss,
                'reason': f'下跌趋势+顶分型跌破+放量'
            }
        
        return None
    
    def check_exit_signal(self, symbol, position_info):
        """检查出场信号"""
        klines = self.get_klines(symbol)
        current_price = klines.iloc[-1]['close']
        entry_price = position_info['entry']
        direction = position_info['direction']
        
        # 计算盈亏比
        if direction == 'long':
            pnl_pct = (current_price - entry_price) / entry_price
        else:
            pnl_pct = (entry_price - current_price) / entry_price
        
        # ===== 出场条件 =====
        
        # 1. 止损
        if direction == 'long' and current_price < position_info['stop_loss']:
            return {'action': 'stop_loss', 'reason': '触发止损'}
        elif direction == 'short' and current_price > position_info['stop_loss']:
            return {'action': 'stop_loss', 'reason': '触发止损'}
        
        # 2. 止盈（分批）
        for i, target in enumerate(self.profit_targets):
            tp_key = f'tp{i}_done'
            if pnl_pct >= target and not position_info.get(tp_key, False):
                return {
                    'action': 'partial_tp',
                    'tp_level': i + 1,
                    'target': target,
                    'reason': f'达到目标{i+1}'
                }
        
        # 3. 趋势破坏
        trend = self.check_trend(klines)
        if direction == 'long' and trend in ['downtrend', 'sideway']:
            return {'action': 'trend_break', 'reason': '趋势破坏'}
        if direction == 'short' and trend in ['uptrend', 'sideway']:
            return {'action': 'trend_break', 'reason': '趋势破坏'}
        
        # 4. 反向信号
        pattern = self.identify_pattern(klines)
        if direction == 'long' and pattern == 'top_fractal':
            return {'action': 'reverse_signal', 'reason': '出现顶分型'}
        if direction == 'short' and pattern == 'bottom_fractal':
            return {'action': 'reverse_signal', 'reason': '出现底分型'}
        
        return None
    
    def open_position(self, symbol, signal):
        """开仓"""
        if not self.can_trade():
            return
            
        entry = signal['entry']
        stop = signal['stop_loss']
        size = self.calculate_position_size(symbol, entry, stop)
        
        if size == 0:
            return
            
        contract = self.api.get_contract(symbol)
        # 不能超过单笔限制
        max_size = (self.account_equity * self.max_position / 100) / (entry * contract.margin)
        size = min(size, int(max_size))
        
        if signal['direction'] == 'long':
            order = self.api.insert_order(
                symbol, 'BUY', 'OPEN', size, entry
            )
        else:
            order = self.api.insert_order(
                symbol, 'SELL', 'OPEN', size, entry
            )
        
        # 记录持仓
        self.positions[symbol] = {
            'direction': signal['direction'],
            'entry': entry,
            'stop_loss': stop,
            'size': size,
            'entry_time': datetime.now(),
            'signal': signal['reason']
        }
        
        print(f"开仓: {symbol} {signal['direction']} {size}手 @ {entry}")
        self.daily_trade_count += 1
    
    def close_position(self, symbol, exit_info):
        """平仓"""
        if symbol not in self.positions:
            return
            
        pos = self.positions[symbol]
        quote = self.api.get_quote(symbol)
        current_price = quote.last_price
        
        if pos['direction'] == 'long':
            order = self.api.insert_order(
                symbol, 'SELL', 'CLOSE', pos['size'], current_price
            )
        else:
            order = self.api.insert_order(
                symbol, 'BUY', 'CLOSE', pos['size'], current_price
            )
        
        # 计算盈亏
        if pos['direction'] == 'long':
            pnl = (current_price - pos['entry']) * pos['size']
        else:
            pnl = (pos['entry'] - current_price) * pos['size']
        
        self.daily_pnl += pnl
        print(f"平仓: {symbol} {exit_info['action']} {exit_info['reason']} 盈亏: {pnl:.2f}")
        
        del self.positions[symbol]
    
    def run(self):
        """主循环"""
        print("="*50)
        print("裸K日内5分钟趋势策略启动")
        print("="*50)
        
        while True:
            try:
                # 检查每个品种
                for symbol in self.symbols:
                    # 获取持仓
                    pos = self.api.get_position(symbol)
                    net_pos = pos.pos_long - pos.pos_short
                    
                    if net_pos == 0:
                        # 无持仓，检查入场
                        if self.can_trade():
                            signal = self.check_entry_signal(symbol)
                            if signal:
                                self.open_position(symbol, signal)
                    
                    else:
                        # 有持仓，检查出场
                        if symbol in self.positions:
                            exit_sig = self.check_exit_signal(symbol, self.positions[symbol])
                            if exit_sig:
                                self.close_position(symbol, exit_sig)
                
                # 每10秒检查一次
                import time
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("策略停止")
                break
            except Exception as e:
                print(f"错误: {e}")
                import time
                time.sleep(30)


# ==================== 策略配置 ====================

if __name__ == "__main__":
    config = {
        'account': '你的天勤账号',
        'password': '你的密码',
        'account_equity': 100000,    # 账户10万
        'risk_ratio': 0.01,          # 1%风险
        'max_position': 30,           # 最大30%仓位
        'max_daily_loss': 0.03,      # 日最大3%
        
        'symbols': [
            'SHFE.rb2505',   # 螺纹钢
            'SHFE.hc2505',  # 热卷
            'DCE.j2505',    # 焦炭
            'CZCE.ma2505',  # 甲醇
        ],
        
        # 均线参数
        'ma_short': 5,
        'ma_mid': 20,
        'ma_long': 60,
        
        # 止盈目标
        'profit_targets': [0.02, 0.04, 0.06],
        
        # 止损
        'stop_loss_pct': 0.01,
    }
    
    strategy = NakedKStrategy(config)
    strategy.run()
```

---

## 九、检查清单（每日执行）

### 交易前检查
- [ ] 趋势方向明确吗？
- [ ] 入场信号符合3个条件以上？
- [ ] 仓位在计划范围内？
- [ ] 止损位计算清楚？
- [ ] 符合交易时间规则？

### 交易后检查
- [ ] 是否按系统执行？
- [ ] 止盈止损是否果断？
- [ ] 记录交易日志？
- [ ] 复盘总结？

---

这个专业版够详细吗？需要我再修改哪里？