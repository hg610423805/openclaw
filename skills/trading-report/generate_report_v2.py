# -*- coding: utf-8 -*-
"""
期货交易报告生成技能 v2
从 analysis_data.json + summary.txt 生成完整报告
"""

import sys
import re
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def parse_summary_raw(filepath):
    """解析 summary.txt 原始文件"""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    trades = []
    
    for line in lines:
        # 匹配：2025-04-22 XXXX SHORT 09:55@5694.0 -> 14:45@5670.0 (XXX) 10 手 +1200.0 元
        match = re.match(
            r'^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(LONG|SHORT)\s+'
            r'(\d{2}:\d{2})@[\d.]+\s+->\s+(\d{2}:\d{2})@[\d.]+\s+'
            r'\(([^)]+)\)\s+(\d+) 手\s+([+-]?[\d.]+) 元',
            line
        )
        
        if match:
            exit_raw = match.group(6)
            
            if '止盈' in exit_raw:
                exit_type = '止盈'
                exit_method = 'EXPMA' if 'EXPMA' in exit_raw else '其他'
            elif '强平' in exit_raw:
                exit_type = '强平'
                exit_method = '收盘'
            elif '止损' in exit_raw:
                exit_type = '止损'
                exit_method = '固定' if '价格' in exit_raw else 'EXPMA'
            else:
                exit_type = '其他'
                exit_method = exit_raw
            
            trades.append({
                'date': match.group(1),
                'product': match.group(2),
                'direction': match.group(3),
                'open_time': match.group(4),
                'close_time': match.group(5),
                'exit_type': exit_type,
                'exit_method': exit_method,
                'lots': int(match.group(7)),
                'pnl': float(match.group(8))
            })
    
    return trades

def analyze_trades(trades):
    """分析交易"""
    by_product = defaultdict(list)
    for t in trades:
        by_product[t['product']].append(t)
    
    for p in by_product:
        by_product[p].sort(key=lambda x: (x['date'], x['open_time']))
    
    stats = {}
    for p, trade_list in by_product.items():
        total = sum(t['pnl'] for t in trade_list)
        wins = len([t for t in trade_list if t['pnl'] > 0])
        losses = len([t for t in trade_list if t['pnl'] < 0])
        
        exit_stats = defaultdict(int)
        for t in trade_list:
            exit_stats[t['exit_type']] += 1
        
        stats[p] = {
            'trades': trade_list,
            'total': total,
            'wins': wins,
            'losses': losses,
            'count': len(trade_list),
            'win_rate': round((wins/len(trade_list))*100, 1) if trade_list else 0,
            'exit_stats': dict(exit_stats)
        }
    
    return stats

def generate_html(stats):
    """生成 HTML"""
    total_pnl = sum(s['total'] for s in stats.values())
    total_trades = sum(s['count'] for s in stats.values())
    avg_win_rate = round(sum(s['win_rate'] for s in stats.values())/len(stats), 1) if stats else 0
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>期货交易回测报告</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: sans-serif; background: #f5f5f5; padding: 20px; }}
    .container {{ max-width: 1400px; margin: 0 auto; }}
    h1 {{ text-align: center; margin: 30px 0; }}
    h2 {{ border-left: 4px solid #1890ff; padding-left: 10px; margin: 30px 0 15px; }}
    h3 {{ margin: 20px 0 10px; }}
    .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
    .card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .card .label {{ color: #666; font-size: 13px; }}
    .card .value {{ font-size: 24px; font-weight: bold; margin-top: 8px; }}
    .pos {{ color: #52c41a; }}
    .neg {{ color: #f5222d; }}
    .section {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px; margin-bottom: 20px; }}
    .stat {{ background: #fafafa; padding: 10px; border-radius: 6px; text-align: center; }}
    .stat .l {{ font-size: 12px; color: #666; }}
    .stat .v {{ font-size: 16px; font-weight: bold; margin-top: 5px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
    th, td {{ padding: 6px 8px; border-bottom: 1px solid #eee; text-align: left; }}
    th {{ background: #fafafa; position: sticky; top: 0; }}
    tr:hover {{ background: #f5f5f5; }}
    .scroll {{ max-height: 500px; overflow-y: auto; }}
    .tag {{ padding: 2px 6px; border-radius: 10px; font-size: 11px; display: inline-block; }}
    .LONG {{ background: #e6f7ff; color: #1890ff; }}
    .SHORT {{ background: #fff7e6; color: #fa8c16; }}
    .止盈 {{ background: #f6ffed; color: #52c41a; }}
    .止损 {{ background: #fff1f0; color: #f5222d; }}
    .强平 {{ background: #fff7e6; color: #fa8c16; }}
    .info {{ background: #e6f7ff; border: 1px solid #91d5ff; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 期货交易回测报告</h1>
    
    <div class="info">
      <strong>回测时间：</strong>2025-03-19 至 2026-03-19<br>
      <strong>总资金：</strong>每品种 100,000 元（独立测试）<br>
      <strong>总盈亏：</strong><span class="pos">+{total_pnl:,.0f}元</span>
    </div>
    
    <div class="cards">
      <div class="card"><div class="label">总交易</div><div class="value">{total_trades}</div></div>
      <div class="card"><div class="label">总盈亏</div><div class="value pos">+{total_pnl:,.0f}元</div></div>
      <div class="card"><div class="label">品种数</div><div class="value">{len(stats)}</div></div>
      <div class="card"><div class="label">平均胜率</div><div class="value">{avg_win_rate}%</div></div>
    </div>
'''
    
    for product, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        exit_info = ' | '.join([f'{k}:{v}' for k,v in s['exit_stats'].items()])
        
        html += f'''
    <div class="section">
      <h2>🎯 {product} <span style="font-size:12px;color:#666">({exit_info})</span></h2>
      <div class="stats">
        <div class="stat"><div class="l">交易次数</div><div class="v">{s['count']}</div></div>
        <div class="stat"><div class="l">总盈亏</div><div class="v {'pos' if s['total']>=0 else 'neg'}">{s['total']:+,.0f}元</div></div>
        <div class="stat"><div class="l">盈利</div><div class="v pos">{s['wins']}</div></div>
        <div class="stat"><div class="l">亏损</div><div class="v neg">{s['losses']}</div></div>
        <div class="stat"><div class="l">胜率</div><div class="v">{s['win_rate']}%</div></div>
      </div>
      
      <h3>📋 交易明细</h3>
      <div class="scroll">
        <table>
          <tr><th>日期</th><th>开仓</th><th>平仓</th><th>方向</th><th>手数</th><th>盈亏</th><th>累计</th><th>出场</th></tr>
'''
        total = 0
        for t in s['trades']:
            total += t['pnl']
            pnl_cls = 'pos' if t['pnl']>0 else ('neg' if t['pnl']<0 else '')
            sign = '+' if t['pnl']>0 else ''
            
            html += f'''          <tr>
            <td>{t['date']}</td><td>{t['open_time']}</td><td>{t['close_time']}</td>
            <td><span class="tag {t['direction']}">{t['direction']}</span></td>
            <td>{t['lots']}</td>
            <td class="{pnl_cls}">{sign}{t['pnl']:.0f}</td>
            <td class="{'pos' if total>=0 else 'neg'}">{total:+,.0f}</td>
            <td><span class="tag {t['exit_type']}">{t['exit_type']}</span> {t['exit_method']}</td>
          </tr>
'''
        
        html += '''        </table>
      </div>
    </div>
'''
    
    html += '''
  </div>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</body>
</html>
'''
    return html

def main():
    print('=== 期货交易报告生成器 ===')
    
    # 解析
    print('解析数据...')
    trades = parse_summary_raw('C:/Users/17699/.openclaw/workspace/summary_clean.txt')
    print(f'找到 {len(trades)} 笔交易')
    
    if not trades:
        print('❌ 未找到交易数据')
        return
    
    # 分析
    print('分析...')
    stats = analyze_trades(trades)
    print(f'共 {len(stats)} 个品种')
    
    # 生成
    print('生成报告...')
    html = generate_html(stats)
    
    # 保存
    path = 'C:/Users/17699/.openclaw/workspace/trading_report_final.html'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'\n[OK] 报告已保存：{path}')
    print('\n品种统计:')
    for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"  {p}: {s['count']}笔 | {s['total']:+,.0f}元 | 胜率{s['win_rate']}%")

if __name__ == '__main__':
    main()
