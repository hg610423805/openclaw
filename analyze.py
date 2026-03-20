# -*- coding: utf-8 -*-
import re
import json
from collections import defaultdict

# 读取文件
with open('C:/Users/17699/.openclaw/media/inbound/summary---e02d8fec-df95-4525-b8ca-79db5c1955bb', 'r', encoding='utf-8') as f:
    content = f.read()

if content.startswith('\ufeff'):
    content = content[1:]

lines = content.split('\n')

# 解析交易
trades = []
for line in lines:
    match = re.match(r'^(\d{4}-\d{2}-\d{2})\s+(\S+)\s+(LONG|SHORT)', line)
    if match:
        date = match.group(1)
        product = match.group(2)
        direction = match.group(3)
        lots_match = re.search(r'(\d+)\s*手', line)
        pnl_match = re.search(r'([+-]?[\d.]+)\s*元', line)
        if lots_match and pnl_match:
            trades.append({'date': date, 'product': product, 'direction': direction, 'lots': int(lots_match.group(1)), 'pnl': float(pnl_match.group(1))})

import sys
sys.stdout.reconfigure(encoding='utf-8')
print(f'[OK] 解析交易：{len(trades)} 笔')

# 统计
monthly = defaultdict(lambda: {'total': 0, 'trades': 0, 'wins': 0, 'losses': 0})
by_product = defaultdict(lambda: {'total': 0, 'trades': 0, 'wins': 0, 'losses': 0})

for t in trades:
    month = t['date'][:7]
    monthly[month]['total'] += t['pnl']
    monthly[month]['trades'] += 1
    if t['pnl'] > 0: monthly[month]['wins'] += 1
    elif t['pnl'] < 0: monthly[month]['losses'] += 1
    
    by_product[t['product']]['total'] += t['pnl']
    by_product[t['product']]['trades'] += 1
    if t['pnl'] > 0: by_product[t['product']]['wins'] += 1
    elif t['pnl'] < 0: by_product[t['product']]['losses'] += 1

sorted_trades = sorted(trades, key=lambda x: x['date'])
cumulative = []
total = 0
for t in sorted_trades:
    total += t['pnl']
    cumulative.append({'date': t['date'], 'cumulative': total})

total_pnl = cumulative[-1]['cumulative'] if cumulative else 0
win_rate = round((len([t for t in trades if t['pnl'] > 0]) / len(trades)) * 100, 1) if trades else 0

print(f'[OK] 总盈亏：{total_pnl} 元 | 胜率：{win_rate}% | 月份：{len(monthly)} | 品种：{len(by_product)}')

# 准备数据
months = sorted(monthly.keys())
products = list(by_product.keys())

# 生成 HTML
with open('C:/Users/17699/.openclaw/workspace/template.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 替换占位符
html = html.replace('{{TOTAL_PNL}}', str(round(total_pnl)))
html = html.replace('{{TOTAL_PNL_CLASS}}', 'positive' if total_pnl >= 0 else 'negative')
html = html.replace('{{TOTAL_TRADES}}', str(len(trades)))
html = html.replace('{{WIN_RATE}}', str(win_rate))
html = html.replace('{{MONTH_COUNT}}', str(len(months)))

# 月度数据
monthly_rows = ''
for m in months:
    d = monthly[m]
    cls = 'positive' if d['total'] >= 0 else 'negative'
    sign = '+' if d['total'] >= 0 else ''
    monthly_rows += f'<tr><td>{m}</td><td>{d["trades"]}</td><td class="positive">{d["wins"]}</td><td class="negative">{d["losses"]}</td><td class="{cls}">{sign}{round(d["total"])}</td></tr>\n'
html = html.replace('{{MONTHLY_ROWS}}', monthly_rows)

# 品种数据
product_rows = ''
for p in products:
    d = by_product[p]
    wr = round((d['wins']/d['trades'])*100, 1) if d['trades'] > 0 else 0
    cls = 'positive' if d['total'] >= 0 else 'negative'
    sign = '+' if d['total'] >= 0 else ''
    tag_name = p.replace('主连', '')
    product_rows += f'<tr><td><span class="product-tag {tag_name}">{p}</span></td><td>{d["trades"]}</td><td class="{cls}">{sign}{round(d["total"])}</td><td>{wr}%</td></tr>\n'
html = html.replace('{{PRODUCT_ROWS}}', product_rows)

# 图表数据
html = html.replace('{{MONTH_LABELS}}', json.dumps(months))
html = html.replace('{{MONTH_DATA}}', json.dumps([monthly[m]['total'] for m in months]))
html = html.replace('{{MONTH_COLORS}}', json.dumps(['rgba(82, 196, 26, 0.7)' if monthly[m]['total'] >= 0 else 'rgba(245, 34, 45, 0.7)' for m in months]))
html = html.replace('{{CUM_LABELS}}', json.dumps([c['date'] for c in cumulative[:50]]))
html = html.replace('{{CUM_DATA}}', json.dumps([c['cumulative'] for c in cumulative[:50]]))
html = html.replace('{{PROD_LABELS}}', json.dumps(products))
html = html.replace('{{PROD_DATA}}', json.dumps([by_product[p]['total'] for p in products]))
html = html.replace('{{PROD_COUNTS}}', json.dumps([by_product[p]['trades'] for p in products]))

with open('C:/Users/17699/.openclaw/workspace/trading_report.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('[OK] H5 报告已生成：trading_report.html')

# 保存 JSON
data = {'trades': trades, 'monthly': dict(monthly), 'byProduct': dict(by_product), 'cumulative': cumulative, 'summary': {'totalPnl': total_pnl, 'winRate': win_rate}}
with open('C:/Users/17699/.openclaw/workspace/analysis_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print('[OK] 数据已保存：analysis_data.json')
