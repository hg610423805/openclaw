# -*- coding: utf-8 -*-
"""
期货交易报告生成技能
从 summary.txt 解析完整交易数据，生成详细 HTML 报告
"""

import sys
import re
import json
from collections import defaultdict
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

def parse_summary(filepath):
    """解析 summary.txt 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if content.startswith('\ufeff'):
        content = content[1:]
    
    lines = content.split('\n')
    trades = []
    
    for line in lines:
        # 匹配交易行：2025-04-22 硅铁主连 SHORT 09:55@5694.0 -> 14:45@5670.0 (止盈-EXPMA(+24 点)) 10 手 +1200.0 元
        match = re.match(
            r'^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(LONG|SHORT)\s+'
            r'(\d{2}:\d{2})@([\d.]+)\s+->\s+(\d{2}:\d{2})@([\d.]+)\s+'
            r'\(([^)]+)\)\s+(\d+) 手\s+([+-]?[\d.]+) 元',
            line
        )
        
        if match:
            exit_type_raw = match.group(8)
            
            # 解析出场类型
            if '止盈' in exit_type_raw:
                exit_type = '止盈'
                exit_method = re.search(r'止盈 - ([^(]+)', exit_type_raw)
                exit_method = exit_method.group(1) if exit_method else 'EXPMA'
            elif '强平' in exit_type_raw:
                exit_type = '强平'
                exit_method = '收盘强平' if '收盘' in exit_type_raw else '系统强平'
            elif '止损' in exit_type_raw:
                exit_type = '止损'
                if '价格' in exit_type_raw:
                    exit_method = '固定止损'
                else:
                    method = re.search(r'止损 - ([^(]+)', exit_type_raw)
                    exit_method = method.group(1) if method else 'EXPMA'
            else:
                exit_type = '其他'
                exit_method = exit_type_raw
            
            trades.append({
                'date': match.group(1),
                'product': match.group(2),
                'direction': match.group(3),
                'open_time': match.group(4),
                'open_price': float(match.group(5)),
                'close_time': match.group(6),
                'close_price': float(match.group(7)),
                'exit_type': exit_type,
                'exit_method': exit_method,
                'exit_raw': exit_type_raw,
                'lots': int(match.group(9)),
                'pnl': float(match.group(10))
            })
    
    return trades

def analyze_trades(trades):
    """分析交易数据"""
    by_product = defaultdict(list)
    for t in trades:
        by_product[t['product']].append(t)
    
    # 按日期排序
    for p in by_product:
        by_product[p].sort(key=lambda x: (x['date'], x['open_time']))
    
    # 统计
    stats = {}
    for p, trade_list in by_product.items():
        total_pnl = sum(t['pnl'] for t in trade_list)
        wins = len([t for t in trade_list if t['pnl'] > 0])
        losses = len([t for t in trade_list if t['pnl'] < 0])
        
        # 出场方式统计
        exit_stats = defaultdict(int)
        for t in trade_list:
            exit_stats[t['exit_type']] += 1
        
        stats[p] = {
            'trades': trade_list,
            'total': total_pnl,
            'wins': wins,
            'losses': losses,
            'count': len(trade_list),
            'win_rate': round((wins/len(trade_list))*100, 1) if trade_list else 0,
            'exit_stats': dict(exit_stats)
        }
    
    return stats

def generate_html(stats, trades):
    """生成 HTML 报告"""
    total_pnl = sum(s['total'] for s in stats.values())
    total_trades = len(trades)
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>期货交易回测报告</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    h1 {{ text-align: center; color: #333; margin-bottom: 30px; font-size: 28px; }}
    h2 {{ color: #444; margin: 30px 0 15px; font-size: 20px; border-left: 4px solid #1890ff; padding-left: 10px; }}
    h3 {{ color: #555; margin: 20px 0 10px; font-size: 16px; }}
    .summary-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
    .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .card h3 {{ color: #666; font-size: 14px; margin-bottom: 10px; }}
    .card .value {{ font-size: 28px; font-weight: bold; }}
    .positive {{ color: #52c41a; }}
    .negative {{ color: #f5222d; }}
    .chart-container {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .product-section {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ padding: 6px 8px; text-align: left; border-bottom: 1px solid #eee; }}
    th {{ background: #fafafa; font-weight: 600; position: sticky; top: 0; }}
    tr:hover {{ background: #f5f5f5; }}
    .scroll-table {{ max-height: 500px; overflow-y: auto; }}
    .tag {{ display: inline-block; padding: 2px 6px; border-radius: 10px; font-size: 11px; }}
    .tag-LONG {{ background: #e6f7ff; color: #1890ff; }}
    .tag-SHORT {{ background: #fff7e6; color: #fa8c16; }}
    .tag-止盈 {{ background: #f6ffed; color: #52c41a; }}
    .tag-止损 {{ background: #fff1f0; color: #f5222d; }}
    .tag-强平 {{ background: #fff7e6; color: #fa8c16; }}
    .info-box {{ background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 15px; margin-bottom: 20px; }}
    .info-box p {{ color: #0050b3; margin: 5px 0; }}
    .stats-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 15px; }}
    .stat-item {{ background: #fafafa; padding: 10px; border-radius: 6px; text-align: center; }}
    .stat-item .label {{ font-size: 12px; color: #666; }}
    .stat-item .value {{ font-size: 16px; font-weight: bold; margin-top: 5px; }}
    .exit-stats {{ display: inline-block; margin-left: 10px; font-size: 12px; color: #666; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 期货交易回测报告</h1>
    
    <div class="info-box">
      <p><strong>回测时间：</strong>2025-03-19 至 2026-03-19</p>
      <p><strong>总资金：</strong>每个品种 100,000 元（独立测试）</p>
      <p><strong>总盈亏：</strong><span class="positive">+{total_pnl:,.0f}</span> 元</p>
    </div>
    
    <div class="summary-cards">
      <div class="card"><h3>总交易笔数</h3><div class="value">{total_trades}</div></div>
      <div class="card"><h3>总盈亏</h3><div class="value positive">+{total_pnl:,.0f} 元</div></div>
      <div class="card"><h3>品种数</h3><div class="value">{len(stats)}</div></div>
      <div class="card"><h3>平均胜率</h3><div class="value">{round(sum(s['win_rate'] for s in stats.values())/len(stats), 1)}%</div></div>
    </div>
'''
    
    # 每个品种一个板块
    for product, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        exit_info = ' | '.join([f"{k}:{v}" for k,v in s['exit_stats'].items()])
        
        html += f'''
    <div class="product-section">
      <h2>🎯 {product} <span class="exit-stats">({exit_info})</span></h2>
      <div class="stats-row">
        <div class="stat-item"><div class="label">交易次数</div><div class="value">{s['count']}</div></div>
        <div class="stat-item"><div class="label">总盈亏</div><div class="value {'positive' if s['total'] >= 0 else 'negative'}">{s['total']:+,.0f}元</div></div>
        <div class="stat-item"><div class="label">盈利</div><div class="value positive">{s['wins']}</div></div>
        <div class="stat-item"><div class="label">亏损</div><div class="value negative">{s['losses']}</div></div>
        <div class="stat-item"><div class="label">胜率</div><div class="value">{s['win_rate']}%</div></div>
      </div>
      
      <h3>📋 每日交易明细</h3>
      <div class="scroll-table">
        <table>
          <thead>
            <tr><th>日期</th><th>开仓</th><th>平仓</th><th>方向</th><th>手数</th><th>盈亏</th><th>累计</th><th>出场方式</th></tr>
          </thead>
          <tbody>
'''
        # 交易明细
        running_total = 0
        for t in s['trades']:
            running_total += t['pnl']
            pnl_class = 'positive' if t['pnl'] > 0 else ('negative' if t['pnl'] < 0 else '')
            pnl_sign = '+' if t['pnl'] > 0 else ''
            
            html += f'''            <tr>
              <td>{t['date']}</td>
              <td>{t['open_time']}</td>
              <td>{t['close_time']}</td>
              <td><span class="tag tag-{t['direction']}">{t['direction']}</span></td>
              <td>{t['lots']}</td>
              <td class="{pnl_class}">{pnl_sign}{t['pnl']:.0f}</td>
              <td class="{'positive' if running_total >= 0 else 'negative'}">{running_total:+,.0f}</td>
              <td><span class="tag tag-{t['exit_type']}">{t['exit_type']}</span> {t['exit_method']}</td>
            </tr>
'''
        
        html += '''          </tbody>
        </table>
      </div>
    </div>
'''
    
    html += '''
  </div>
  <script>
    // 可在此添加图表
    console.log('报告生成完成');
  </script>
</body>
</html>
'''
    
    return html

def main():
    print('=== 期货交易报告生成器 ===')
    print('')
    
    # 解析数据
    print('正在解析 summary.txt...')
    trades = parse_summary('C:/Users/17699/.openclaw/workspace/summary_clean.txt')
    print(f'找到 {len(trades)} 笔交易')
    
    # 分析
    print('正在分析...')
    stats = analyze_trades(trades)
    print(f'共 {len(stats)} 个品种')
    
    # 生成 HTML
    print('正在生成报告...')
    html = generate_html(stats, trades)
    
    # 保存
    output_path = 'C:/Users/17699/.openclaw/workspace/trading_report_final.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('')
    print(f'[OK] 报告已生成：{output_path}')
    print('')
    
    # 显示统计
    print('=== 品种统计 ===')
    for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"{p}: {s['count']}笔 | {s['total']:+,.0f}元 | 胜率{s['win_rate']}%")

if __name__ == '__main__':
    main()
