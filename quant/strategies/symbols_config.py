# -*- coding: utf-8 -*-
"""
品种配置 - Tick 值和合约乘数
来源：天勤量化官方文档
"""

# 品种参数配置
# 格式：品种代码 -> {tick 值，合约乘数，交易所，手续费率}
SYMBOL_CONFIG = {
    # 黑色系
    "rb": {
        "name": "螺纹钢",
        "tick": 1,           # 1 元/吨
        "multiplier": 10,    # 10 吨/手
        "exchange": "SHFE",  # 上期所
        "commission_rate": 0.0001,  # 万分之一
        "margin_rate": 0.10  # 保证金 10%
    },
    
    # 农产品
    "m": {
        "name": "豆粕",
        "tick": 1,           # 1 元/吨
        "multiplier": 10,    # 10 吨/手
        "exchange": "DCE",   # 大商所
        "commission_rate": 0.00006,  # 万分之 0.6
        "margin_rate": 0.08
    },
    
    "rm": {
        "name": "菜粕",
        "tick": 1,           # 1 元/吨
        "multiplier": 10,    # 10 吨/手
        "exchange": "CZCE",  # 郑商所
        "commission_rate": 0.00006,
        "margin_rate": 0.08
    },
    
    # 建材
    "fg": {
        "name": "玻璃",
        "tick": 1,           # 1 元/吨
        "multiplier": 20,    # 20 吨/手
        "exchange": "CZCE",
        "commission_rate": 0.00006,
        "margin_rate": 0.10
    },
    
    # 铁合金
    "sf": {
        "name": "硅铁",
        "tick": 2,           # 2 元/吨
        "multiplier": 5,     # 5 吨/手
        "exchange": "DCE",
        "commission_rate": 0.00006,
        "margin_rate": 0.10
    },
    
    "sm": {
        "name": "锰硅",
        "tick": 2,           # 2 元/吨
        "multiplier": 5,     # 5 吨/手
        "exchange": "DCE",
        "commission_rate": 0.00006,
        "margin_rate": 0.10
    },
    
    # 煤化工
    "ur": {
        "name": "尿素",
        "tick": 1,           # 1 元/吨
        "multiplier": 20,    # 20 吨/手
        "exchange": "CZCE",
        "commission_rate": 0.00006,
        "margin_rate": 0.10
    },
    
    "ma": {
        "name": "甲醇",
        "tick": 1,           # 1 元/吨
        "multiplier": 10,    # 10 吨/手
        "exchange": "CZCE",
        "commission_rate": 0.00006,
        "margin_rate": 0.10
    },
}

def get_symbol_info(symbol_code: str) -> dict:
    """获取品种信息"""
    code = symbol_code.lower()
    if code in SYMBOL_CONFIG:
        return SYMBOL_CONFIG[code]
    raise ValueError(f"未知品种：{symbol_code}")

def get_full_symbol(symbol_code: str, contract_month: str = "2505") -> str:
    """获取完整合约代码"""
    info = get_symbol_info(symbol_code)
    exchange = info["exchange"]
    return f"{exchange}.{symbol_code.lower()}{contract_month}"
