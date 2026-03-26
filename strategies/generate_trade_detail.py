# -*- coding: utf-8 -*-
"""
生成交易明细 HTML 报告
"""
import json
from datetime import datetime

# 读取回测结果
with open('backtest_results_real.json', 'r', encoding='utf-8') as f:
    results = json.load(f)

def generate_trade_detail_html(symbol_data, symbol_name):
    """生成交易明细 HTML"""
    trades = symbol_data['trades']
    
    # 配对开仓和平仓
    paired_trades = []
    open_trade = None
    
    for trade in trades:
        if trade['type'] == '开仓':
            open_trade = trade
        elif trade['type'] == '平仓' and open_trade:
            paired_trades.append({
                'open': open_trade,
                'close': trade
            })
            open_trade = None
    
    # 生成 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易明细报告 - {symbol_name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 15px; padding: 30px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .header h1 {{ color: #667eea; margin-bottom: 10px; }}
        .header p {{ color: #666; }}
        .card {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .card h2 {{ color: #333; margin-bottom: 20px; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .stat-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-box.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .stat-box.red {{ background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%); }}
        .stat-value {{ font-size: 32px; font-weight: bold; margin-bottom: 5px; }}
        .stat-label {{ font-size: 14px; opacity: 0.9; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; color: #333; font-weight: 600; position: sticky; top: 0; }}
        tr:hover {{ background: #f8f9fa; }}
        .profit {{ color: #11998e; font-weight: bold; }}
        .loss {{ color: #eb3349; font-weight: bold; }}
        .badge {{ display: inline-block; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }}
        .badge-long {{ background: #d1ecf1; color: #0c5460; }}
        .badge-short {{ background: #f8d7da; color: #721c24; }}
        .badge-win {{ background: #d4edda; color: #155724; }}
        .badge-loss {{ background: #f8d7da; color: #721c24; }}
        .footer {{ text-align: center; color: white; margin-top: 30px; }}
        .filter-bar {{ margin-bottom: 15px; display: flex; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ padding: 6px 16px; border: none; border-radius: 20px; cursor: pointer; font-size: 12px; transition: all 0.2s; }}
        .filter-btn.active {{ background: #667eea; color: white; }}
        .filter-btn.inactive {{ background: #e9ecef; color: #666; }}
        .scroll-container {{ max-height: 600px; overflow-y: auto; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 交易明细报告 - {symbol_name}</h1>
            <p>回测周期：{symbol_data['start_date']} 至 {symbol_data['end_date']} | 总交易数：{len(paired_trades)} 笔</p>
        </div>

        <div class="card">
            <h2>📊 总体统计</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="stat-value">¥{symbol_data['total_profit']:,.0f}</div>
                    <div class="stat-label">总盈利</div>
                </div>
                <div class="stat-box green">
                    <div class="stat-value">{symbol_data['annual_return']:.2f}%</div>
                    <div class="stat-label">年化收益</div>
                </div>
                <div class="stat-box">
                    <div class="stat-value">{symbol_data['win_rate']:.1f}%</div>
                    <div class="stat-label">胜率</div>
                </div>
                <div class="stat-box red">
                    <div class="stat-value">{symbol_data['max_drawdown']:.2f}%</div>
                    <div class="stat-label">最大回撤</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📝 交易明细 ({len(paired_trades)} 笔)</h2>
            <div class="filter-bar">
                <button class="filter-btn active" onclick="filterTable('all')">全部</button>
                <button class="filter-btn inactive" onclick="filterTable('win')">盈利</button>
                <button class="filter-btn inactive" onclick="filterTable('loss')">亏损</button>
                <button class="filter-btn inactive" onclick="filterTable('long')">做多</button>
                <button class="filter-btn inactive" onclick="filterTable('short')">做空</button>
            </div>
            <div class="scroll-container">
                <table id="tradeTable">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>方向</th>
                            <th>开仓时间</th>
                            <th>平仓时间</th>
                            <th>开仓价</th>
                            <th>平仓价</th>
                            <th>盈亏 (元)</th>
                            <th>胜率</th>
                            <th>开仓原因</th>
                            <th>平仓原因</th>
                        </tr>
                    </thead>
                    <tbody>
'''
    
    for i, pair in enumerate(paired_trades, 1):
        open_t = pair['open']
        close_t = pair['close']
        profit = close_t.get('profit', 0)
        is_win = profit > 0
        direction = open_t['direction']
        
        html += f'''                        <tr class="{'win' if is_win else 'loss'}" data-direction="{direction}" data-result="{'win' if is_win else 'loss'}">
                            <td>{i}</td>
                            <td><span class="badge badge-{'long' if direction == '多' else 'short'}">{'做多' if direction == '多' else '做空'}</span></td>
                            <td>{open_t['open_time']}</td>
                            <td>{close_t['close_time']}</td>
                            <td>{open_t['price']:.1f}</td>
                            <td>{close_t['price']:.1f}</td>
                            <td class="{'profit' if is_win else 'loss'}">{'+' if is_win else ''}{profit:,.0f}</td>
                            <td><span class="badge badge-{'win' if is_win else 'loss'}">{'盈利' if is_win else '亏损'}</span></td>
                            <td>{open_t.get('reason', '-')}</td>
                            <td>{close_t.get('reason', '-')}</td>
                        </tr>
'''
    
    html += '''                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            <p>生成时间：''' + datetime.now().strftime("%Y-%m-%d %H:%M") + ''' | 咕噜量化助手 🐱</p>
        </div>
    </div>

    <script>
        function filterTable(filter) {
            const rows = document.querySelectorAll('#tradeTable tbody tr');
            const buttons = document.querySelectorAll('.filter-btn');
            
            buttons.forEach(btn => {
                btn.classList.remove('active');
                btn.classList.add('inactive');
            });
            event.target.classList.remove('inactive');
            event.target.classList.add('active');
            
            rows.forEach(row => {
                const direction = row.dataset.direction;
                const result = row.dataset.result;
                
                let show = false;
                if (filter === 'all') show = true;
                else if (filter === 'win' && result === 'win') show = true;
                else if (filter === 'loss' && result === 'loss') show = true;
                else if (filter === 'long' && direction === '多') show = true;
                else if (filter === 'short' && direction === '空') show = true;
                
                row.style.display = show ? '' : 'none';
            });
        }
    </script>
</body>
</html>'''
    
    return html

# 生成锰硅报告
sm_html = generate_trade_detail_html(results['KQ.m@CZCE.SM'], '锰硅主力连续')
with open('trade-detail-SM.html', 'w', encoding='utf-8') as f:
    f.write(sm_html)

# 生成硅铁报告（如果有数据）
if 'KQ.m@CZCE.SF' in results:
    sf_html = generate_trade_detail_html(results['KQ.m@CZCE.SF'], '硅铁主力连续')
    with open('trade-detail-SF.html', 'w', encoding='utf-8') as f:
        f.write(sf_html)

print("[OK] 交易明细报告生成完成！")
print("   - 锰硅：trade-detail-SM.html")
print("   - 硅铁：trade-detail-SF.html")
