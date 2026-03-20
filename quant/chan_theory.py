# -*- coding: utf-8 -*-
"""
缠论分析模块
============
实现缠论核心概念：分型、笔、线段、中枢、买卖点
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple


class KLine:
    """单根 K 线"""
    def __init__(self, datetime, open, high, low, close, volume=0):
        self.datetime = datetime
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
    
    def __repr__(self):
        return f"KLine({self.datetime}, O={self.open}, H={self.high}, L={self.low}, C={self.close})"


class Fractal:
    """分型"""
    TOP = "top"      # 顶分型
    BOTTOM = "bottom"  # 底分型
    
    def __init__(self, fractal_type: str, high_kline: KLine, low_kline: KLine, index: int):
        self.type = fractal_type
        self.high_kline = high_kline    # 分型区间最高 K 线
        self.low_kline = low_kline      # 分型区间最低 K 线
        self.index = index              # 在 K 线序列中的位置
        self.high = high_kline.high
        self.low = low_kline.low
    
    def __repr__(self):
        return f"Fractal({self.type}, idx={self.index}, H={self.high}, L={self.low})"


class Bi:
    """笔"""
    def __init__(self, start_fractal: Fractal, end_fractal: Fractal, index: int):
        self.start = start_fractal
        self.end = end_fractal
        self.index = index
        self.direction = "up" if start_fractal.type == Fractal.BOTTOM else "down"
        self.high = max(start_fractal.high, end_fractal.high)
        self.low = min(start_fractal.low, end_fractal.low)
    
    def __repr__(self):
        return f"Bi({self.direction}, idx={self.index}, {self.start.index}->{self.end.index})"


class Zhongshu:
    """中枢"""
    def __init__(self, start_bi: Bi, end_bi: Bi, index: int):
        self.start_bi = start_bi
        self.end_bi = end_bi
        self.index = index
        self.bis = []  # 组成中枢的笔
        
        # 计算中枢区间
        self.zg = min(bi.high for bi in self.bis) if self.bis else 0  # 中枢高点
        self.zd = max(bi.low for bi in self.bis) if self.bis else 0   # 中枢低点
    
    def add_bi(self, bi: Bi):
        self.bis.append(bi)
        if self.bis:
            high_points = [bi.high for bi in self.bis]
            low_points = [bi.low for bi in self.bis]
            self.zg = min(high_points)
            self.zd = max(low_points)
    
    def __repr__(self):
        return f"Zhongshu(idx={self.index}, ZD={self.zd}, ZG={self.zg}, bis={len(self.bis)})"


class ChanTheoryAnalyzer:
    """
    缠论分析器
    ==========
    核心功能：
    1. K 线包含处理
    2. 分型识别
    3. 笔的划分
    4. 线段划分
    5. 中枢识别
    6. 买卖点判断
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {
            "merge_interval": 60,
            "fractal_min_bars": 5,
            "bi_min_bars": 4,
            "xd_min_bis": 3,
        }
        
        self.raw_klines = []      # 原始 K 线
        self.merged_klines = []   # 包含处理后的 K 线
        self.fractals = []        # 分型列表
        self.bis = []             # 笔列表
        self.xianduan = []        # 线段列表
        self.zhongshus = []       # 中枢列表
    
    def load_klines(self, klines: pd.DataFrame):
        """
        加载 K 线数据
        
        Parameters
        ----------
        klines : pd.DataFrame
            K 线数据，包含 columns: datetime, open, high, low, close, volume
        """
        self.raw_klines = []
        for _, row in klines.iterrows():
            kline = KLine(
                datetime=row['datetime'],
                open=row['open'],
                high=row['high'],
                low=row['low'],
                close=row['close'],
                volume=row.get('volume', 0)
            )
            self.raw_klines.append(kline)
        
        # 执行包含处理
        self._merge_klines()
        
        # 识别分型
        self._find_fractals()
        
        # 划分笔
        self._divide_bis()
        
        # 识别中枢
        self._find_zhongshus()
    
    def _merge_klines(self):
        """
        K 线包含处理
        ==========
        规则：
        1. 向上处理：取两根 K 线的高点最大值，低点最大值
        2. 向下处理：取两根 K 线的高点最小值，低点最小值
        """
        if not self.raw_klines:
            return
        
        self.merged_klines = [self.raw_klines[0]]
        direction = None  # 当前方向：1=向上，-1=向下
        
        for i in range(1, len(self.raw_klines)):
            curr = self.raw_klines[i]
            prev = self.merged_klines[-1]
            
            # 判断包含关系
            if (curr.high >= prev.high and curr.low <= prev.low) or \
               (curr.high <= prev.high and curr.low >= prev.low):
                # 有包含关系，需要合并
                if direction is None:
                    # 第一组包含，根据前一根 K 线判断方向
                    if len(self.merged_klines) > 1:
                        prev_prev = self.merged_klines[-2]
                        direction = 1 if prev.high > prev_prev.high else -1
                    else:
                        direction = 1 if curr.high > prev.high else -1
                
                if direction == 1:
                    # 向上合并：高高高，低高低
                    new_high = max(prev.high, curr.high)
                    new_low = max(prev.low, curr.low)
                else:
                    # 向下合并：高低高，低低低
                    new_high = min(prev.high, curr.high)
                    new_low = min(prev.low, curr.low)
                
                # 创建合并后的 K 线
                merged = KLine(
                    datetime=curr.datetime,
                    open=prev.open,
                    high=new_high,
                    low=new_low,
                    close=curr.close,
                    volume=prev.volume + curr.volume
                )
                self.merged_klines[-1] = merged
            else:
                # 无包含关系，更新方向
                if curr.high > prev.high:
                    direction = 1
                elif curr.low < prev.low:
                    direction = -1
                
                self.merged_klines.append(curr)
    
    def _find_fractals(self):
        """
        识别分型
        =======
        顶分型：中间 K 线高点最高，且左右两侧 K 线高点都低于它
        底分型：中间 K 线低点最低，且左右两侧 K 线低点都高于它
        """
        self.fractals = []
        min_bars = self.config.get("fractal_min_bars", 5)
        
        for i in range(2, len(self.merged_klines) - 2):
            k_prev2 = self.merged_klines[i - 2]
            k_prev1 = self.merged_klines[i - 1]
            k_curr = self.merged_klines[i]
            k_next1 = self.merged_klines[i + 1]
            k_next2 = self.merged_klines[i + 2]
            
            # 顶分型判断
            if (k_curr.high > k_prev1.high and k_curr.high > k_next1.high and
                k_curr.high >= k_prev2.high and k_curr.high >= k_next2.high):
                fractal = Fractal(
                    fractal_type=Fractal.TOP,
                    high_kline=k_curr,
                    low_kline=min([k_prev2, k_prev1, k_curr, k_next1, k_next2], key=lambda k: k.low),
                    index=i
                )
                self.fractals.append(fractal)
            
            # 底分型判断
            elif (k_curr.low < k_prev1.low and k_curr.low < k_next1.low and
                  k_curr.low <= k_prev2.low and k_curr.low <= k_next2.low):
                fractal = Fractal(
                    fractal_type=Fractal.BOTTOM,
                    high_kline=max([k_prev2, k_prev1, k_curr, k_next1, k_next2], key=lambda k: k.high),
                    low_kline=k_curr,
                    index=i
                )
                self.fractals.append(fractal)
    
    def _divide_bis(self):
        """
        划分笔
        =====
        规则：
        1. 顶分型和底分型交替出现
        2. 顶底之间至少有 4 根 K 线
        3. 顶必须高于底（向上笔），底必须低于顶（向下笔）
        """
        if len(self.fractals) < 2:
            return
        
        self.bis = []
        bi_index = 0
        
        i = 0
        while i < len(self.fractals) - 1:
            curr_fractal = self.fractals[i]
            next_fractal = self.fractals[i + 1]
            
            # 检查是否是交替的分型（顶 - 底 或 底 - 顶）
            if curr_fractal.type != next_fractal.type:
                # 检查 K 线数量
                kline_diff = abs(next_fractal.index - curr_fractal.index)
                if kline_diff >= self.config.get("bi_min_bars", 4):
                    # 检查价格有效性
                    if curr_fractal.type == Fractal.BOTTOM:
                        # 向上笔：底分型低点 < 顶分型高点
                        if curr_fractal.low < next_fractal.high:
                            bi = Bi(curr_fractal, next_fractal, bi_index)
                            self.bis.append(bi)
                            bi_index += 1
                            i += 1
                            continue
                    else:
                        # 向下笔：顶分型高点 > 底分型低点
                        if curr_fractal.high > next_fractal.low:
                            bi = Bi(curr_fractal, next_fractal, bi_index)
                            self.bis.append(bi)
                            bi_index += 1
                            i += 1
                            continue
            i += 1
    
    def _find_zhongshus(self):
        """
        识别中枢
        ==========
        规则：至少 3 笔重叠，形成价格区间
        """
        if len(self.bis) < 3:
            return
        
        self.zhongshus = []
        zhongshu_index = 0
        
        i = 0
        while i < len(self.bis) - 2:
            # 尝试从第 i 笔开始找中枢
            potential_bis = [self.bis[i]]
            
            for j in range(i + 1, len(self.bis)):
                # 检查是否与前面所有笔有重叠
                current_high = min(bi.high for bi in potential_bis + [self.bis[j]])
                current_low = max(bi.low for bi in potential_bis + [self.bis[j]])
                
                if current_high > current_low:
                    # 有重叠，加入
                    potential_bis.append(self.bis[j])
                    
                    if len(potential_bis) >= 3:
                        # 形成中枢
                        zhongshu = Zhongshu(potential_bis[0], potential_bis[-1], zhongshu_index)
                        for bi in potential_bis:
                            zhongshu.add_bi(bi)
                        self.zhongshus.append(zhongshu)
                        zhongshu_index += 1
                        i = j  # 跳到最后一笔
                        break
                else:
                    # 无重叠，重新开始
                    break
            
            i += 1
    
    def get_current_bi_direction(self) -> Optional[str]:
        """获取当前笔的方向"""
        if not self.bis:
            return None
        return self.bis[-1].direction
    
    def get_latest_zhongshu(self) -> Optional[Zhongshu]:
        """获取最新的中枢"""
        if not self.zhongshus:
            return None
        return self.zhongshus[-1]
    
    def is_in_zhongshu(self, price: float) -> bool:
        """判断当前价格是否在最后一个中枢内"""
        zhongshu = self.get_latest_zhongshu()
        if not zhongshu:
            return False
        return zhongshu.zd <= price <= zhongshu.zg
    
    def get_buy_sell_point(self) -> Optional[str]:
        """
        判断当前可能的买卖点
        ==================
        返回："BS1", "BS2", "BS3", "SS1", "SS2", "SS3", 或 None
        """
        if len(self.bis) < 4 or len(self.zhongshus) < 1:
            return None
        
        latest_bi = self.bis[-1]
        prev_bi = self.bis[-2]
        zhongshu = self.zhongshus[-1]
        
        # 一类买点：趋势背驰后的反转（简化版：新低后快速拉回中枢）
        if latest_bi.direction == "up" and prev_bi.direction == "down":
            if prev_bi.low < zhongshu.zd and latest_bi.high > zhongshu.zd:
                return "BS1"
        
        # 一类卖点：顶背驰后的下跌
        if latest_bi.direction == "down" and prev_bi.direction == "up":
            if prev_bi.high > zhongshu.zg and latest_bi.low < zhongshu.zg:
                return "SS1"
        
        return None
    
    def to_dataframe(self) -> pd.DataFrame:
        """将分析结果转换为 DataFrame"""
        data = []
        for kline in self.merged_klines:
            data.append({
                'datetime': kline.datetime,
                'open': kline.open,
                'high': kline.high,
                'low': kline.low,
                'close': kline.close,
                'volume': kline.volume
            })
        return pd.DataFrame(data)
    
    def summary(self) -> Dict:
        """返回分析摘要"""
        return {
            "raw_klines": len(self.raw_klines),
            "merged_klines": len(self.merged_klines),
            "fractals": len(self.fractals),
            "bis": len(self.bis),
            "zhongshus": len(self.zhongshus),
            "current_bi_direction": self.get_current_bi_direction(),
            "latest_zhongshu": str(self.get_latest_zhongshu()) if self.get_latest_zhongshu() else None,
            "potential_bs_point": self.get_buy_sell_point()
        }


# ============ 使用示例 ============
if __name__ == "__main__":
    # 创建测试数据
    import datetime
    
    test_data = []
    base_price = 3500
    for i in range(100):
        dt = datetime.datetime(2024, 1, 1, 9, 0) + datetime.timedelta(minutes=i*10)
        open_price = base_price + np.random.randn() * 10
        high_price = open_price + abs(np.random.randn() * 15)
        low_price = open_price - abs(np.random.randn() * 15)
        close_price = base_price + np.random.randn() * 10
        base_price = close_price
        
        test_data.append({
            'datetime': dt,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': int(np.random.rand() * 10000)
        })
    
    df = pd.DataFrame(test_data)
    
    # 执行缠论分析
    analyzer = ChanTheoryAnalyzer()
    analyzer.load_klines(df)
    
    print("缠论分析结果:")
    print(analyzer.summary())
