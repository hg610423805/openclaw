# -*- coding: utf-8 -*-
"""
快速交易报告生成器
直接使用已解析的 analysis_data.json
"""

import sys
import json
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print('=== 快速交易报告生成器 ===')
    
    # 读取数据
    with open('C:/Users/17699/.openclaw/workspace/analysis_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    trades = data['trades']
    print(f'读取 {len(trades)} 笔交易')
    
    # 按品种分组
    by_product = defaultdict(list)
    for t in trades:
        by_product[t['product']].append(t)
    
    # 排序
    for p in by_product:
        by_product[p].sort(key=lambda x: x['date'])
    
    # 统计
    stats = {}
    for p, lst in by_product.items():
        total = sum(t['pnl'] for t in lst)
        wins = len([t for t in lst if t['pnl'] > 0])
        stats[p] = {
            'trades': lst,
            'total': total,
            'wins': wins,
            'losses': len(lst) - wins,
            'count': len(lst),
            'win_rate': round((wins/len(lst))*100, 1)
        }
    
    total_pnl = sum(s['total'] for s in stats.values())
    
    # 生成 HTML
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>交易报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{{font-family:sans-serif;background:#f5f5f5;padding:20px}}
.container{{max-width:1400px;margin:0 auto}}
h1{{text-align:center}}h2{{border-left:4px solid #1890ff;padding-left:10px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px;margin:20px 0}}
.card{{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
.card .l{{color:#666;font-size:13px}}.card .v{{font-size:24px;font-weight:bold;margin-top:8px}}
.pos{{color:#52c41a}}.neg{{color:#f5222d}}
.section{{background:#fff;padding:20px;border-radius:8px;margin:20px 0;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:20px 0}}
.stat{{background:#fafafa;padding:10px;border-radius:6px;text-align:center}}
.stat .l{{font-size:12px;color:#666}}.stat .v{{font-size:16px;font-weight:bold;margin-top:5px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th,td{{padding:6px 8px;border-bottom:1px solid #eee}}
th{{background:#fafafa;position:sticky;top:0}}.scroll{{max-height:500px;overflow-y:auto}}
.tag{{padding:2px 6px;border-radius:10px;font-size:11px}}
.LONG{{background:#e6f7ff;color:#1890ff}}.SHORT{{background:#fff7e6;color:#fa8c16}}
</style></head><body><div class="container">
<h1>📊 期货交易报告</h1>
<div style="background:#e6f7ff;border:1px solid #91d5ff;padding:15px;border-radius:8px;margin:20px 0">
<strong>回测：</strong>2025-03-19 至 2026-03-19 | <strong>总盈亏：</strong><span class="pos">+{total_pnl:,.0f}元</span>
</div>
<div class="cards">
<div class="card"><div class="l">总交易</div><div class="value">{len(trades)}</div></div>
<div class="card"><div class="l">总盈亏</div><div class="value pos">+{total_pnl:,.0f}元</div></div>
<div class="card"><div class="l">品种</div><div class="value">{len(stats)}</div></div>
<div class="card"><div class="l">胜率</div><div class="value">{round(sum(s["win_rate"] for s in stats.values())/len(stats),1)}%</div></div>
</div>
'''
    
    for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        html += f'''
<div class="section">
<h2>🎯 {p}</h2>
<div class="stats">
<div class="stat"><div class="l">次数</div><div class="v">{s['count']}</div></div>
<div class="stat"><div class="l">盈亏</div><div class="v {'pos' if s['total']>=0 else 'neg'}">{s['total']:+,.0f}元</div></div>
<div class="stat"><div class="l">盈利</div><div class="v pos">{s['wins']}</div></div>
<div class="stat"><div class="l">亏损</div><div class="v neg">{s['losses']}</div></div>
<div class="stat"><div class="l">胜率</div><div class="v">{s['win_rate']}%</div></div>
</div>
<h3>交易明细</h3>
<div class="scroll"><table>
<tr><th>日期</th><th>方向</th><th>手数</th><th>盈亏</th><th>累计</th></tr>
'''
        total = 0
        for t in s['trades']:
            total += t['pnl']
            html += f'<tr><td>{t["date"]}</td><td><span class="tag {t["direction"]}">{t["direction"]}</span></td><td>{t["lots"]}</td><td class="{"pos" if t["pnl"]>0 else "neg"}">{t["pnl"]:+.0f}</td><td class="{"pos" if total>=0 else "neg"}">{total:+,.0f}</td></tr>'
        html += '''</table></div></div>'''
    
    html += '''</div></body></html>'''
    
    # 保存
    path = 'C:/Users/17699/.openclaw/workspace/trading_report_quick.html'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f'\n[OK] 报告已保存：{path}')
    print('\n品种:')
    for p, s in sorted(stats.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"  {p}: {s['count']}笔 | {s['total']:+,.0f}元")

if __name__ == '__main__':
    main()
