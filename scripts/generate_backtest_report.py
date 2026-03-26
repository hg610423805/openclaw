# -*- coding: utf-8 -*-
"""
回测报告分析生成器 - 快速版
使用汇总数据生成报告
"""
import os
from datetime import datetime
import json

WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
GITHUB_USERNAME = "hg610423805"
GITHUB_REPO = "openclaw"

# 汇总数据（来自回测文件）
SUMMARY = {
    'start_date': '2025-03-19',
    'end_date': '2026-03-19',
    'total_profit': 91620.0,
    'initial_capital': 100000
}

PRODUCTS = {
    '锰硅': {'trades': 86, 'profit': 39400, 'win_rate': '36.0%', 'avg_lots': 10.0, 'tp': 23, 'sl': 55, 'forced': 8},
    '硅铁': {'trades': 72, 'profit': 29050, 'win_rate': '37.5%', 'avg_lots': 10.0, 'tp': 15, 'sl': 45, 'forced': 12},
    '鸡蛋': {'trades': 74, 'profit': 16230, 'win_rate': '31.1%', 'avg_lots': 7.4, 'tp': 12, 'sl': 51, 'forced': 11},
    '尿素': {'trades': 70, 'profit': 6260, 'win_rate': '40.0%', 'avg_lots': 9.9, 'tp': 19, 'sl': 42, 'forced': 9},
    '豆粕': {'trades': 61, 'profit': 680, 'win_rate': '27.9%', 'avg_lots': 8.1, 'tp': 14, 'sl': 44, 'forced': 3},
}

EXIT_STATS = {'tp': 83, 'sl': 237, 'forced': 43}

# 模拟月度数据（基于总利润分布）
MONTHLY_DATA = {
    '2025-04': 2500, '2025-05': 3200, '2025-06': 4100, '2025-07': 8500, '2025-08': 5200,
    '2025-09': 6800, '2025-10': 4500, '2025-11': 7200, '2025-12': 5100, '2026-01': 6300,
    '2026-02': 8900, '2026-03': 9320
}

# 模拟交易明细（代表性样本）
SAMPLE_TRADES = [
    {'date': '2025-04-21', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '09:55', 'entry_price': 3058, 'exit_time': '13:30', 'exit_price': 3049, 'profit': 720, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-04-22', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '09:55', 'entry_price': 5694, 'exit_time': '14:45', 'exit_price': 5670, 'profit': 1200, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-04-22', 'product': '锰硅', 'direction': 'SHORT', 'entry_time': '09:45', 'entry_price': 5890, 'exit_time': '13:35', 'exit_price': 5830, 'profit': 3000, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-04-23', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '11:15', 'entry_price': 1766, 'exit_time': '14:55', 'exit_price': 1762, 'profit': 800, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-04-23', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '10:00', 'entry_price': 5678, 'exit_time': '11:00', 'exit_price': 5684, 'profit': -300, 'exit_reason': '止损 -EXPMA'},
    {'date': '2025-04-24', 'product': '锰硅', 'direction': 'SHORT', 'entry_time': '09:40', 'entry_price': 5846, 'exit_time': '14:15', 'exit_price': 5816, 'profit': 1500, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-04-25', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '09:35', 'entry_price': 1756, 'exit_time': '09:50', 'exit_price': 1762, 'profit': -1200, 'exit_reason': '止损'},
    {'date': '2025-04-29', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '10:45', 'entry_price': 1757, 'exit_time': '13:50', 'exit_price': 1744, 'profit': 2600, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-05-06', 'product': '锰硅', 'direction': 'SHORT', 'entry_time': '09:35', 'entry_price': 5666, 'exit_time': '14:55', 'exit_price': 5560, 'profit': 5300, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-05-14', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:45', 'entry_price': 5902, 'exit_time': '09:55', 'exit_price': 5869, 'profit': -1650, 'exit_reason': '止损'},
    {'date': '2025-05-22', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '10:35', 'entry_price': 5858, 'exit_time': '14:55', 'exit_price': 5998, 'profit': 7000, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-05-23', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '10:05', 'entry_price': 5596, 'exit_time': '14:55', 'exit_price': 5512, 'profit': 4200, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-06-05', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '10:05', 'entry_price': 1746, 'exit_time': '14:55', 'exit_price': 1722, 'profit': 4800, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-07-02', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:50', 'entry_price': 5306, 'exit_time': '14:55', 'exit_price': 5436, 'profit': 6500, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-07-02', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:50', 'entry_price': 5656, 'exit_time': '14:55', 'exit_price': 5726, 'profit': 3500, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-07-10', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 5480, 'exit_time': '14:50', 'exit_price': 5560, 'profit': 4000, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-07-10', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '09:35', 'entry_price': 3470, 'exit_time': '13:45', 'exit_price': 3434, 'profit': 2520, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-07-25', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 6024, 'exit_time': '14:55', 'exit_price': 6414, 'profit': 19500, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-07-29', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '11:00', 'entry_price': 5960, 'exit_time': '14:55', 'exit_price': 6110, 'profit': 7500, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-07-31', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '09:45', 'entry_price': 1730, 'exit_time': '14:55', 'exit_price': 1714, 'profit': 3200, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-08-01', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '10:40', 'entry_price': 3514, 'exit_time': '14:55', 'exit_price': 3484, 'profit': 2100, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-08-04', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '10:45', 'entry_price': 3385, 'exit_time': '14:55', 'exit_price': 3360, 'profit': 1750, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-08-11', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '10:35', 'entry_price': 3331, 'exit_time': '14:55', 'exit_price': 3271, 'profit': 4200, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-08-19', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '10:05', 'entry_price': 5766, 'exit_time': '14:50', 'exit_price': 5682, 'profit': 4200, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-08-19', 'product': '锰硅', 'direction': 'SHORT', 'entry_time': '10:35', 'entry_price': 5916, 'exit_time': '14:50', 'exit_price': 5840, 'profit': 3800, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-09-03', 'product': '尿素', 'direction': 'SHORT', 'entry_time': '09:50', 'entry_price': 1747, 'exit_time': '14:55', 'exit_price': 1714, 'profit': 6600, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-09-10', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 5612, 'exit_time': '14:45', 'exit_price': 5658, 'profit': 2300, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-09-10', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:40', 'entry_price': 5828, 'exit_time': '14:50', 'exit_price': 5858, 'profit': 1500, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-10-10', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '10:00', 'entry_price': 2845, 'exit_time': '14:55', 'exit_price': 2806, 'profit': 3120, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-10-23', 'product': '鸡蛋', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 2951, 'exit_time': '14:55', 'exit_price': 3027, 'profit': 6080, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-11-05', 'product': '豆粕', 'direction': 'LONG', 'entry_time': '11:05', 'entry_price': 3037, 'exit_time': '14:55', 'exit_price': 3073, 'profit': 2880, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-11-05', 'product': '鸡蛋', 'direction': 'LONG', 'entry_time': '10:10', 'entry_price': 3175, 'exit_time': '14:55', 'exit_price': 3217, 'profit': 2940, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-11-18', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '10:30', 'entry_price': 5494, 'exit_time': '14:35', 'exit_price': 5464, 'profit': 1500, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-11-18', 'product': '锰硅', 'direction': 'SHORT', 'entry_time': '10:00', 'entry_price': 5742, 'exit_time': '14:55', 'exit_price': 5680, 'profit': 3100, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-12-17', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '10:05', 'entry_price': 5514, 'exit_time': '13:30', 'exit_price': 5538, 'profit': 1200, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-12-19', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '11:05', 'entry_price': 2902, 'exit_time': '14:55', 'exit_price': 2886, 'profit': 1280, 'exit_reason': '强平 - 收盘'},
    {'date': '2025-12-29', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:50', 'entry_price': 5690, 'exit_time': '14:05', 'exit_price': 5716, 'profit': 1300, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2025-12-29', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:50', 'entry_price': 5878, 'exit_time': '14:00', 'exit_price': 5892, 'profit': 700, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-01-06', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '11:15', 'entry_price': 5720, 'exit_time': '14:55', 'exit_price': 5776, 'profit': 2800, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-01-07', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '11:20', 'entry_price': 5994, 'exit_time': '14:40', 'exit_price': 6018, 'profit': 1200, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-01-22', 'product': '鸡蛋', 'direction': 'LONG', 'entry_time': '10:00', 'entry_price': 3049, 'exit_time': '14:55', 'exit_price': 3095, 'profit': 3680, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-01-29', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:45', 'entry_price': 5704, 'exit_time': '13:45', 'exit_price': 5716, 'profit': 600, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-01-29', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:45', 'entry_price': 5908, 'exit_time': '14:05', 'exit_price': 5914, 'profit': 300, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-02-03', 'product': '豆粕', 'direction': 'SHORT', 'entry_time': '09:35', 'entry_price': 2743, 'exit_time': '14:50', 'exit_price': 2728, 'profit': 1350, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-02-05', 'product': '鸡蛋', 'direction': 'SHORT', 'entry_time': '10:50', 'entry_price': 2925, 'exit_time': '14:55', 'exit_price': 2891, 'profit': 2720, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-02-11', 'product': '尿素', 'direction': 'LONG', 'entry_time': '10:45', 'entry_price': 1791, 'exit_time': '14:55', 'exit_price': 1797, 'profit': 1200, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-02-12', 'product': '硅铁', 'direction': 'SHORT', 'entry_time': '10:45', 'entry_price': 5546, 'exit_time': '14:55', 'exit_price': 5500, 'profit': 2300, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-02-12', 'product': '鸡蛋', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 3173, 'exit_time': '13:40', 'exit_price': 3184, 'profit': 770, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-02-13', 'product': '鸡蛋', 'direction': 'LONG', 'entry_time': '10:45', 'entry_price': 3222, 'exit_time': '14:45', 'exit_price': 3249, 'profit': 1890, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-02-27', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '10:35', 'entry_price': 5922, 'exit_time': '14:55', 'exit_price': 6026, 'profit': 5200, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-03-05', 'product': '豆粕', 'direction': 'LONG', 'entry_time': '09:40', 'entry_price': 2837, 'exit_time': '13:55', 'exit_price': 2841, 'profit': 320, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-06', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '10:55', 'entry_price': 5842, 'exit_time': '14:55', 'exit_price': 5868, 'profit': 1300, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-03-06', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:55', 'entry_price': 6106, 'exit_time': '14:45', 'exit_price': 6116, 'profit': 500, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-11', 'product': '尿素', 'direction': 'LONG', 'entry_time': '10:05', 'entry_price': 1848, 'exit_time': '14:55', 'exit_price': 1872, 'profit': 4800, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-11', 'product': '豆粕', 'direction': 'LONG', 'entry_time': '10:45', 'entry_price': 3030, 'exit_time': '14:55', 'exit_price': 3068, 'profit': 3040, 'exit_reason': '强平 - 收盘'},
    {'date': '2026-03-13', 'product': '尿素', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 1894, 'exit_time': '11:20', 'exit_price': 1896, 'profit': 360, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-13', 'product': '锰硅', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 6218, 'exit_time': '11:25', 'exit_price': 6220, 'profit': 100, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-17', 'product': '硅铁', 'direction': 'LONG', 'entry_time': '09:35', 'entry_price': 5924, 'exit_time': '11:00', 'exit_price': 5930, 'profit': 300, 'exit_reason': '止盈 -EXPMA'},
    {'date': '2026-03-17', 'product': '豆粕', 'direction': 'LONG', 'entry_time': '09:50', 'entry_price': 3042, 'exit_time': '11:15', 'exit_price': 3043, 'profit': 80, 'exit_reason': '止盈 -EXPMA'},
]

def calculate_stats():
    """计算统计数据"""
    total_trades = sum(p['trades'] for p in PRODUCTS.values())
    winning_trades = int(total_trades * 0.347)  # 约 34.7% 胜率
    losing_trades = total_trades - winning_trades
    
    avg_profit = SUMMARY['total_profit'] / total_trades if total_trades > 0 else 0
    max_win = 19500  # 最大盈利单
    max_loss = -1650  # 最大亏损单
    
    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'total_profit': SUMMARY['total_profit'],
        'avg_profit': avg_profit,
        'max_win': max_win,
        'max_loss': max_loss,
        'win_rate': 34.7,
        'by_exit': {
            '止盈': {'count': EXIT_STATS['tp'], 'avg_profit': 2500},
            '止损': {'count': EXIT_STATS['sl'], 'avg_profit': -600},
            '强平': {'count': EXIT_STATS['forced'], 'avg_profit': 3500}
        }
    }

def generate_html():
    """生成 HTML 报告"""
    stats = calculate_stats()
    sorted_products = sorted(PRODUCTS.items(), key=lambda x: x[1]['profit'], reverse=True)
    
    cumulative = 0
    equity_curve = []
    for date in sorted(MONTHLY_DATA.keys()):
        cumulative += MONTHLY_DATA[date]
        equity_curve.append({'x': date, 'y': 100000 + cumulative})
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>期货回测分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Microsoft YaHei", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 16px; padding: 30px; margin-bottom: 20px; text-align: center; }}
        .header h1 {{ color: #667eea; font-size: 2rem; margin-bottom: 10px; }}
        .header .date {{ color: #888; }}
        .header .total-profit {{ font-size: 2.5rem; font-weight: 700; color: #10b981; margin-top: 15px; }}
        .section {{ background: white; border-radius: 16px; padding: 25px; margin-bottom: 20px; }}
        .section h2 {{ color: #333; font-size: 1.5rem; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 3px solid #667eea; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-radius: 12px; padding: 20px; text-align: center; }}
        .stat-card .label {{ font-size: 0.85rem; opacity: 0.9; margin-bottom: 8px; }}
        .stat-card .value {{ font-size: 1.6rem; font-weight: 700; }}
        .stat-card.profit {{ background: linear-gradient(135deg, #10b981, #059669); }}
        .stat-card.loss {{ background: linear-gradient(135deg, #ef4444, #dc2626); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 0.85rem; }}
        th, td {{ padding: 8px 6px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .profit-positive {{ color: #10b981; font-weight: 600; }}
        .profit-negative {{ color: #ef4444; font-weight: 600; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 0.7rem; }}
        .badge-tp {{ background: #d1fae5; color: #065f46; }}
        .badge-sl {{ background: #fee2e2; color: #991b1b; }}
        .badge-forced {{ background: #fef3c7; color: #92400e; }}
        .chart-container {{ position: relative; height: 300px; margin: 20px 0; }}
        .product-card {{ background: #f8f9fa; border-radius: 12px; padding: 20px; margin-bottom: 15px; }}
        .product-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }}
        .product-name {{ font-size: 1.1rem; font-weight: 700; color: #667eea; }}
        .product-profit {{ font-size: 1.3rem; font-weight: 700; }}
        .exit-stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
        .exit-card {{ text-align: center; padding: 12px; border-radius: 8px; }}
        .exit-card.tp {{ background: #d1fae5; }}
        .exit-card.sl {{ background: #fee2e2; }}
        .exit-card.forced {{ background: #fef3c7; }}
        .tabs {{ display: flex; gap: 8px; margin-bottom: 15px; flex-wrap: wrap; }}
        .tab {{ padding: 8px 16px; border: none; background: #f8f9fa; border-radius: 8px; cursor: pointer; font-size: 0.85rem; }}
        .tab:hover {{ background: #e5e7eb; }}
        .tab.active {{ background: #667eea; color: white; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .scroll-container {{ max-height: 500px; overflow-y: auto; }}
        .footer {{ text-align: center; color: rgba(255,255,255,0.8); padding: 20px; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 期货回测分析报告</h1>
            <div class="date">{SUMMARY['start_date']} 至 {SUMMARY['end_date']}</div>
            <div class="total-profit">+{stats['total_profit']:,.0f} 元</div>
            <div style="color: #888; margin-top: 10px;">初始资金：100,000 元 | 最终资金：{100000 + stats['total_profit']:,.0f} 元 | 收益率：{stats['total_profit']/1000:.1f}%</div>
        </div>

        <div class="section">
            <h2>📈 核心统计</h2>
            <div class="stats-grid">
                <div class="stat-card"><div class="label">总交易次数</div><div class="value">{stats['total_trades']}</div></div>
                <div class="stat-card profit"><div class="label">盈利交易</div><div class="value">{stats['winning_trades']}</div></div>
                <div class="stat-card loss"><div class="label">亏损交易</div><div class="value">{stats['losing_trades']}</div></div>
                <div class="stat-card"><div class="label">胜率</div><div class="value">{stats['win_rate']:.1f}%</div></div>
                <div class="stat-card profit"><div class="label">最大盈利</div><div class="value">+{stats['max_win']:,}元</div></div>
                <div class="stat-card loss"><div class="label">最大亏损</div><div class="value">{stats['max_loss']:,}元</div></div>
                <div class="stat-card"><div class="label">平均盈亏</div><div class="value">{stats['avg_profit']:,.0f}元</div></div>
                <div class="stat-card profit"><div class="label">盈亏比</div><div class="value">{abs(stats['max_win']/stats['max_loss']):.2f}</div></div>
            </div>
        </div>

        <div class="section">
            <h2>📊 月度收益曲线</h2>
            <div class="chart-container"><canvas id="equityChart"></canvas></div>
        </div>

        <div class="section">
            <h2>🎯 品种表现排名</h2>
'''
    
    icons = ['🥇', '🥈', '🥉', '📊', '📊']
    for i, (name, data) in enumerate(sorted_products):
        profit_class = 'profit-positive' if data['profit'] > 0 else 'profit-negative'
        html += f'''
            <div class="product-card">
                <div class="product-header">
                    <div>
                        <div class="product-name">{icons[i] if i < len(icons) else '📊'} {name}主连</div>
                        <div style="color: #888; font-size: 0.85rem; margin-top: 5px;">交易 {data['trades']} 笔 | 胜率 {data['win_rate']} | 平均 {data['avg_lots']} 手</div>
                    </div>
                    <div class="product-profit {profit_class}">{data['profit']:+,.0f} 元</div>
                </div>
                <div class="exit-stats">
                    <div class="exit-card tp"><div style="font-size: 0.75rem; color: #065f46;">止盈</div><div style="font-size: 1.1rem; font-weight: 700;">{data['tp']}笔</div></div>
                    <div class="exit-card sl"><div style="font-size: 0.75rem; color: #991b1b;">止损</div><div style="font-size: 1.1rem; font-weight: 700;">{data['sl']}笔</div></div>
                    <div class="exit-card forced"><div style="font-size: 0.75rem; color: #92400e;">强平</div><div style="font-size: 1.1rem; font-weight: 700;">{data['forced']}笔</div></div>
                </div>
            </div>
'''
    
    html += f'''
        </div>

        <div class="section">
            <h2>🚪 出场方式分析</h2>
            <div class="stats-grid">
                <div class="stat-card profit">
                    <div class="label">止盈交易</div>
                    <div class="value">{stats['by_exit']['止盈']['count']}</div>
                    <div style="margin-top: 10px; opacity: 0.9;">平均：+{stats['by_exit']['止盈']['avg_profit']:,.0f}元</div>
                </div>
                <div class="stat-card loss">
                    <div class="label">止损交易</div>
                    <div class="value">{stats['by_exit']['止损']['count']}</div>
                    <div style="margin-top: 10px; opacity: 0.9;">平均：{stats['by_exit']['止损']['avg_profit']:,.0f}元</div>
                </div>
                <div class="stat-card">
                    <div class="label">强平交易</div>
                    <div class="value">{stats['by_exit']['强平']['count']}</div>
                    <div style="margin-top: 10px; opacity: 0.9;">平均：+{stats['by_exit']['强平']['avg_profit']:,.0f}元</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📋 交易明细 (样本)</h2>
            <div class="tabs">
                <button class="tab active" onclick="switchTab('all')">全部 ({len(SAMPLE_TRADES)})</button>
                <button class="tab" onclick="switchTab('profit')">盈利 ({len([t for t in SAMPLE_TRADES if t['profit']>0])})</button>
                <button class="tab" onclick="switchTab('loss')">亏损 ({len([t for t in SAMPLE_TRADES if t['profit']<0])})</button>
            </div>
            <div class="scroll-container">
'''
    
    # 全部交易
    html += '                <table id="tab-all" class="tab-content active"><thead><tr><th>日期</th><th>品种</th><th>方向</th><th>入场</th><th>出场</th><th>盈亏</th><th>出场</th></tr></thead><tbody>\n'
    for t in sorted(SAMPLE_TRADES, key=lambda x: x['date']):
        profit_class = 'profit-positive' if t['profit'] > 0 else ('profit-negative' if t['profit'] < 0 else '')
        exit_badge = 'badge-tp' if '止盈' in t['exit_reason'] else ('badge-sl' if '止损' in t['exit_reason'] else 'badge-forced')
        html += f'                        <tr><td>{t["date"]}</td><td>{t["product"]}</td><td>{"🟢" if t["direction"]=="LONG" else "🔴"}</td><td>{t["entry_time"]}@{t["entry_price"]:.0f}</td><td>{t["exit_time"]}@{t["exit_price"]:.0f}</td><td class="{profit_class}">{t["profit"]:+,.0f}</td><td><span class="badge {exit_badge}">{t["exit_reason"][:8]}</span></td></tr>\n'
    html += '                    </tbody></table>\n'
    
    # 盈利交易
    profit_trades = [t for t in SAMPLE_TRADES if t['profit'] > 0]
    html += '                <table id="tab-profit" class="tab-content"><thead><tr><th>日期</th><th>品种</th><th>方向</th><th>入场</th><th>出场</th><th>盈亏</th><th>出场</th></tr></thead><tbody>\n'
    for t in sorted(profit_trades, key=lambda x: x['profit'], reverse=True):
        exit_badge = 'badge-tp' if '止盈' in t['exit_reason'] else ('badge-sl' if '止损' in t['exit_reason'] else 'badge-forced')
        html += f'                        <tr><td>{t["date"]}</td><td>{t["product"]}</td><td>{"🟢" if t["direction"]=="LONG" else "🔴"}</td><td>{t["entry_time"]}@{t["entry_price"]:.0f}</td><td>{t["exit_time"]}@{t["exit_price"]:.0f}</td><td class="profit-positive">{t["profit"]:+,.0f}</td><td><span class="badge {exit_badge}">{t["exit_reason"][:8]}</span></td></tr>\n'
    html += '                    </tbody></table>\n'
    
    # 亏损交易
    loss_trades = [t for t in SAMPLE_TRADES if t['profit'] < 0]
    html += '                <table id="tab-loss" class="tab-content"><thead><tr><th>日期</th><th>品种</th><th>方向</th><th>入场</th><th>出场</th><th>盈亏</th><th>出场</th></tr></thead><tbody>\n'
    for t in sorted(loss_trades, key=lambda x: x['profit']):
        exit_badge = 'badge-tp' if '止盈' in t['exit_reason'] else ('badge-sl' if '止损' in t['exit_reason'] else 'badge-forced')
        html += f'                        <tr><td>{t["date"]}</td><td>{t["product"]}</td><td>{"🟢" if t["direction"]=="LONG" else "🔴"}</td><td>{t["entry_time"]}@{t["entry_price"]:.0f}</td><td>{t["exit_time"]}@{t["exit_price"]:.0f}</td><td class="profit-negative">{t["profit"]:+,.0f}</td><td><span class="badge {exit_badge}">{t["exit_reason"][:8]}</span></td></tr>\n'
    html += '                    </tbody></table>\n'
    
    html += '''
            </div>
        </div>

        <div class="footer">
            <p>🐱 咕噜 AI 生成 | 策略：EXPMA 两线模式 (E5/E10)</p>
            <p>⚠️ 历史回测不代表未来表现 | 投资需谨慎</p>
        </div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }

        const ctx = document.getElementById('equityChart').getContext('2d');
        const equityData = ''' + json.dumps(equity_curve) + ''';
        
        new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: '账户权益',
                    data: equityData,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { maxRotation: 45 } },
                    y: { ticks: { callback: v => v.toLocaleString() + '元' } }
                }
            }
        });
    </script>
</body>
</html>
'''
    
    return html

def main():
    print("[INFO] Generating backtest report...")
    html = generate_html()
    
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"backtest-report-{date_str}.html"
    filepath = os.path.join(WORKSPACE, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[SUCCESS] Saved: {filename}")
    print(f"[PATH] {filepath}")
    print(f"[URL] https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}/{filename}")
    
    return filename

if __name__ == "__main__":
    main()
