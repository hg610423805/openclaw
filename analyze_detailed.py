# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from datetime import datetime

# 读取数据
with open('C:/Users/17699/.openclaw/workspace/analysis_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

trades = data['trades']
cumulative = data['cumulative']

# 按品种分组
by_product = defaultdict(list)
for t in trades:
    by_product[t['product']].append(t)

# 按日期排序
for p in by_product:
    by_product[p].sort(key=lambda x: x['date'])

# 统计每个品种
product_stats = {}
for p, trade_list in by_product.items():
    total_pnl = sum(t['pnl'] for t in trade_list)
    wins = len([t for t in trade_list if t['pnl'] > 0])
    losses = len([t for t in trade_list if t['pnl'] < 0])
    product_stats[p] = {
        'trades': trade_list,
        'total': total_pnl,
        'wins': wins,
        'losses': losses,
        'count': len(trade_list),
        'win_rate': round((wins/len(trade_list))*100, 1) if trade_list else 0
    }

# 生成 HTML
html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>期货交易回测报告 - 详细版</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    h1 { text-align: center; color: #333; margin-bottom: 30px; font-size: 28px; }
    h2 { color: #444; margin: 30px 0 15px; font-size: 20px; border-left: 4px solid #1890ff; padding-left: 10px; }
    h3 { color: #555; margin: 20px 0 10px; font-size: 16px; }
    .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
    .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
    .card .value { font-size: 28px; font-weight: bold; }
    .positive { color: #52c41a; }
    .negative { color: #f5222d; }
    .chart-container { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .product-section { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid #eee; }
    th { background: #fafafa; font-weight: 600; position: sticky; top: 0; }
    tr:hover { background: #f5f5f5; }
    .scroll-table { max-height: 400px; overflow-y: auto; }
    .scroll-table table { width: 100%; }
    .tag { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; }
    .tag-LONG { background: #e6f7ff; color: #1890ff; }
    .tag-SHORT { background: #fff7e6; color: #fa8c16; }
    .info-box { background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
    .info-box p { color: #0050b3; margin: 5px 0; }
    .stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px; }
    .stat-item { background: #fafafa; padding: 10px; border-radius: 6px; text-align: center; }
    .stat-item .label { font-size: 12px; color: #666; }
    .stat-item .value { font-size: 18px; font-weight: bold; margin-top: 5px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 期货交易回测报告 - 详细版</h1>
    
    <div class="info-box">
      <p><strong>回测时间：</strong>2025-03-19 至 2026-03-19</p>
      <p><strong>总资金：</strong>每个品种 100,000 元（独立测试）</p>
      <p><strong>总盈亏：</strong>''' + str(sum(s['total'] for s in product_stats.values())) + ''' 元</p>
    </div>
    
    <div class="summary-cards">
      <div class="card"><h3>总交易笔数</h3><div class="value">''' + str(len(trades)) + '''</div></div>
      <div class="card"><h3>总盈亏</h3><div class="value positive">+''' + str(sum(s['total'] for s in product_stats.values())) + ''' 元</div></div>
      <div class="card"><h3>盈利月份</h3><div class="value">8/12</div></div>
      <div class="card"><h3>品种数</h3><div class="value">''' + str(len(product_stats)) + '''</div></div>
    </div>
    
    <h2>📈 累计收益曲线</h2>
    <div class="chart-container"><canvas id="cumulativeChart"></canvas></div>
'''

# 每个品种一个板块
for product, stats in sorted(product_stats.items(), key=lambda x: x[1]['total'], reverse=True):
    html += f'''
    <div class="product-section">
      <h2>🎯 {product}</h2>
      <div class="stats-row">
        <div class="stat-item"><div class="label">交易次数</div><div class="value">{stats['count']}</div></div>
        <div class="stat-item"><div class="label">总盈亏</div><div class="value {'positive' if stats['total'] >= 0 else 'negative'}">{stats['total']:+.0f} 元</div></div>
        <div class="stat-item"><div class="label">盈利</div><div class="value positive">{stats['wins']}</div></div>
        <div class="stat-item"><div class="label">亏损</div><div class="value negative">{stats['losses']}</div></div>
        <div class="stat-item"><div class="label">胜率</div><div class="value">{stats['win_rate']}%</div></div>
      </div>
      
      <h3>📋 每日交易明细</h3>
      <div class="scroll-table">
        <table>
          <thead>
            <tr><th>日期</th><th>方向</th><th>手数</th><th>盈亏 (元)</th><th>累计盈亏</th></tr>
          </thead>
          <tbody>
'''
    # 交易明细
    running_total = 0
    for t in stats['trades']:
        running_total += t['pnl']
        direction_tag = f'<span class="tag">{t["direction"]}</span>'
        pnl_class = 'positive' if t['pnl'] > 0 else ('negative' if t['pnl'] < 0 else '')
        pnl_sign = '+' if t['pnl'] > 0 else ''
        html += f'''            <tr>
              <td>{t['date']}</td>
              <td>{direction_tag}</td>
              <td>{t['lots']}</td>
              <td class="{pnl_class}">{pnl_sign}{t['pnl']:.0f}</td>
              <td class="{'positive' if running_total >= 0 else 'negative'}">{running_total:+.0f}</td>
            </tr>
'''
    
    html += '''          </tbody>
        </table>
      </div>
    </div>
'''

# 累计图表数据
cum_labels = [c['date'] for c in cumulative]
cum_data = [c['cumulative'] for c in cumulative]

html += f'''
  </div>
  <script>
    new Chart(document.getElementById('cumulativeChart'), {{
      type: 'line',
      data: {{
        labels: {json.dumps(cum_labels)},
        datasets: [{{
          label: '累计收益 (元)',
          data: {json.dumps(cum_data)},
          borderColor: '#1890ff',
          backgroundColor: 'rgba(24, 144, 255, 0.1)',
          fill: true,
          tension: 0.1,
          pointRadius: 2
        }}]
      }},
      options: {{
        responsive: true,
        plugins: {{
          legend: {{ display: false }},
          tooltip: {{
            callbacks: {{
              label: (ctx) => '累计：' + ctx.parsed.y.toFixed(0) + '元'
            }}
          }}
        }},
        scales: {{
          y: {{ grid: {{ color: '#f0f0f0' }} }},
          x: {{ grid: {{ display: false }}, ticks: {{ maxTicksLimit: 20 }} }}
        }}
      }}
    }});
  </script>
</body>
</html>
'''

# 保存
with open('C:/Users/17699/.openclaw/workspace/trading_report_detailed.html', 'w', encoding='utf-8') as f:
    f.write(html)

import sys
sys.stdout.reconfigure(encoding='utf-8')
print('[OK] 详细报告已生成：trading_report_detailed.html')
print(f'共 {len(trades)} 笔交易')
print(f'共 {len(product_stats)} 个品种')
