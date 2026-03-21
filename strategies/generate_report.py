# -*- coding: utf-8 -*-
"""
生成回测 HTML 报告
"""

import json
from datetime import datetime

def generate_html_report(results, output_file):
    """生成 HTML 回测报告"""
    
    # 合并两个品种的数据
    sf = results.get('CZCE.SF000', {})
    sm = results.get('CZCE.SM000', {})
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EXPMA 策略回测报告 - 硅铁 & 锰硅</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        h1 {{ font-size: 24px; color: #1a1a1a; margin-bottom: 10px; }}
        h2 {{ font-size: 18px; color: #333; margin: 20px 0 10px; border-left: 4px solid #667eea; padding-left: 12px; }}
        h3 {{ font-size: 16px; color: #666; margin: 15px 0 8px; }}
        
        .kpi-row {{
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            gap: 15px;
            margin: 20px 0;
        }}
        .kpi {{
            text-align: center;
            padding: 15px;
            flex: 1;
            min-width: 120px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
        }}
        .kpi.green {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
        .kpi.orange {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }}
        .kpi-value {{ font-size: 28px; font-weight: bold; }}
        .kpi-label {{ font-size: 13px; opacity: 0.9; margin-top: 5px; }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin: 20px 0;
        }}
        
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; font-size: 13px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
        tr:hover {{ background: #f5f7ff; }}
        
        .tag {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .tag-good {{ background: #d4edda; color: #155724; }}
        .tag-warning {{ background: #fff3cd; color: #856404; }}
        .tag-bad {{ background: #f8d7da; color: #721c24; }}
        
        .profit-positive {{ color: #e74c3c; font-weight: bold; }}
        .profit-negative {{ color: #27ae60; font-weight: bold; }}
        
        .summary-box {{
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }}
        
        .recommendation {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin: 20px 0;
        }}
        .recommendation h3 {{ color: white; }}
        
        .nav-tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .nav-tab {{
            padding: 10px 20px;
            border: none;
            background: #f0f0f0;
            border-radius: 8px 8px 0 0;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .nav-tab.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        @media (max-width: 768px) {{
            .kpi-row {{ flex-direction: column; }}
            .kpi {{ min-width: 100%; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📊 EXPMA 双向策略回测报告</h1>
            <p style="color: #666; font-size: 14px; margin-top: 5px;">
                回测周期：2025-03-22 至 2026-03-22（1年）| 品种：硅铁主力连续 & 锰硅主力连续
            </p>
        </div>
        
        <!-- 导航标签 -->
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="switchTab('sf')">🥇 硅铁 (SF)</button>
            <button class="nav-tab" onclick="switchTab('sm')">🥈 锰硅 (SM)</button>
            <button class="nav-tab" onclick="switchTab('summary')">📋 总结分析</button>
            <button class="nav-tab" onclick="switchTab('trades')">📜 交易明细</button>
        </div>
        
        <!-- 硅铁报告 -->
        <div id="sf" class="tab-content active">
            {generate_product_report(sf, '硅铁主力连续')}
        </div>
        
        <!-- 锰硅报告 -->
        <div id="sm" class="tab-content">
            {generate_product_report(sm, '锰硅主力连续')}
        </div>
        
        <!-- 总结分析 -->
        <div id="summary" class="tab-content">
            {generate_summary(sf, sm)}
        </div>
        
        <!-- 交易明细 -->
        <div id="trades" class="tab-content">
            {generate_trades_table(sf, sm)}
        </div>
        
        <div class="card" style="text-align: center; color: #999; font-size: 13px; padding: 20px;">
            生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")} | 策略：EXPMA 双向趋势跟踪 | 数据源：天勤量化
        </div>
    </div>
    
    <script>
        function switchTab(tabId) {{
            // 隐藏所有内容
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(el => el.classList.remove('active'));
            
            // 显示选中内容
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}
        
        // 图表代码
        {generate_chart_scripts(sf, sm)}
    </script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 报告已生成：{output_file}")


def generate_product_report(data, name):
    """生成单个品种的报告"""
    if not data:
        return "<p>无数据</p>"
    
    # 评估标签
    if data.get('annual_return', 0) > 30:
        tag = '<span class="tag tag-good">优秀</span>'
    elif data.get('annual_return', 0) > 10:
        tag = '<span class="tag tag-warning">良好</span>'
    else:
        tag = '<span class="tag tag-bad">待优化</span>'
    
    return f'''
        <div class="card">
            <h2>🎯 {name} - 核心指标 {tag}</h2>
            <div class="kpi-row">
                <div class="kpi">
                    <div class="kpi-value">¥{data.get('total_profit', 0):,.0f}</div>
                    <div class="kpi-label">总盈利</div>
                </div>
                <div class="kpi green">
                    <div class="kpi-value">{data.get('annual_return', 0):.1f}%</div>
                    <div class="kpi-label">年化收益</div>
                </div>
                <div class="kpi">
                    <div class="kpi-value">{data.get('total_trades', 0)}</div>
                    <div class="kpi-label">总交易数</div>
                </div>
                <div class="kpi">
                    <div class="kpi-value">{data.get('win_rate', 0):.1f}%</div>
                    <div class="kpi-label">胜率</div>
                </div>
                <div class="kpi orange">
                    <div class="kpi-value">{data.get('max_drawdown', 0):.1f}%</div>
                    <div class="kpi-label">最大回撤</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 资金曲线</h2>
            <div class="chart-container">
                <canvas id="capitalChart_{name[:2]}"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>📊 月度盈亏</h2>
            <div class="chart-container">
                <canvas id="monthlyChart_{name[:2]}"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>📋 交易统计</h2>
            <table>
                <tr><td>初始资金</td><td>¥{data.get('initial_capital', 0):,.0f}</td></tr>
                <tr><td>最终资金</td><td>¥{data.get('final_capital', 0):,.0f}</td></tr>
                <tr><td>盈利交易</td><td class="profit-positive">{data.get('win_count', 0)} 笔</td></tr>
                <tr><td>亏损交易</td><td class="profit-negative">{data.get('loss_count', 0)} 笔</td></tr>
                <tr><td>平均每笔盈利</td><td>¥{data.get('total_profit', 0) / max(data.get('total_trades', 1), 1):,.0f}</td></tr>
            </table>
        </div>
    '''


def generate_summary(sf, sm):
    """生成总结分析"""
    sf_return = sf.get('annual_return', 0) if sf else 0
    sm_return = sm.get('annual_return', 0) if sm else 0
    sf_drawdown = sf.get('max_drawdown', 0) if sf else 0
    sm_drawdown = sm.get('max_drawdown', 0) if sm else 0
    
    best_product = "硅铁" if sf_return > sm_return else "锰硅"
    total_profit = (sf.get('total_profit', 0) if sf else 0) + (sm.get('total_profit', 0) if sm else 0)
    
    return f'''
        <div class="card">
            <h2>📊 综合评估</h2>
            <div class="summary-box">
                <p><strong>回测周期：</strong>2025-03-22 至 2026-03-22（1 年）</p>
                <p><strong>测试品种：</strong>硅铁主力连续 + 锰硅主力连续</p>
                <p><strong>总盈利：</strong>¥{total_profit:,.2f}</p>
                <p><strong>表现最好品种：</strong>{best_product}</p>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 策略优势</h2>
            <div class="summary-box" style="border-left-color: #11998e;">
                <p>✅ <strong>趋势跟踪：</strong>EXPMA 多周期共振，有效捕捉大趋势</p>
                <p>✅ <strong>双向交易：</strong>做多做空均可获利，适应不同市场环境</p>
                <p>✅ <strong>严格止损：</strong>基于 K 线高低点止损，风险可控</p>
                <p>✅ <strong>日内收盘：</strong>14:57 强制平仓，避免隔夜风险</p>
            </div>
        </div>
        
        <div class="card">
            <h2>⚠️ 风险提示</h2>
            <div class="summary-box" style="border-left-color: #f5576c;">
                <p>⚠️ <strong>震荡行情：</strong>日线震荡时空仓，可能错过小幅波动</p>
                <p>⚠️ <strong>胜率偏低：</strong>趋势策略胜率通常 30-40%，靠盈亏比获利</p>
                <p>⚠️ <strong>最大回撤：</strong>硅铁 {sf_drawdown:.1f}% / 锰硅 {sm_drawdown:.1f}%，需做好资金管理</p>
                <p>⚠️ <strong>过拟合风险：</strong>历史回测不代表未来表现</p>
            </div>
        </div>
        
        <div class="recommendation">
            <h3>🔧 优化建议</h3>
            <p style="margin-top: 10px;">
                <strong>1️⃣ 参数优化：</strong>测试不同 EXPMA 周期组合（如 7/14/28）<br><br>
                <strong>2️⃣ 仓位管理：</strong>建议单品种仓位不超过 30%，两品种组合不超过 50%<br><br>
                <strong>3️⃣ 止损优化：</strong>可考虑 ATR 动态止损，适应不同波动率<br><br>
                <strong>4️⃣ 品种扩展：</strong>可测试其他黑色系品种（螺纹、热卷）<br><br>
                <strong>5️⃣ 实盘验证：</strong>建议先用小资金实盘测试 1-3 个月
            </p>
        </div>
    '''


def generate_trades_table(sf, sm):
    """生成交易明细表"""
    sf_trades = sf.get('trades', []) if sf else []
    sm_trades = sm.get('trades', []) if sm else []
    
    rows = ""
    for t in sf_trades[:50]:  # 只显示前 50 条
        profit = t.get('profit', 0)
        profit_class = 'profit-positive' if profit > 0 else 'profit-negative'
        rows += f'''<tr>
            <td>硅铁</td>
            <td>{t.get('open_time', t.get('close_time', ''))}</td>
            <td>{t.get('direction', '')}</td>
            <td>{t.get('type', '')}</td>
            <td>{t.get('price', 0):.2f}</td>
            <td class="{profit_class}">{'+' if profit > 0 else ''}{profit:.2f}</td>
            <td>{t.get('reason', '')}</td>
        </tr>'''
    
    for t in sm_trades[:50]:
        profit = t.get('profit', 0)
        profit_class = 'profit-positive' if profit > 0 else 'profit-negative'
        rows += f'''<tr>
            <td>锰硅</td>
            <td>{t.get('open_time', t.get('close_time', ''))}</td>
            <td>{t.get('direction', '')}</td>
            <td>{t.get('type', '')}</td>
            <td>{t.get('price', 0):.2f}</td>
            <td class="{profit_class}">{'+' if profit > 0 else ''}{profit:.2f}</td>
            <td>{t.get('reason', '')}</td>
        </tr>'''
    
    return f'''
        <div class="card">
            <h2>📜 交易明细（前 100 条）</h2>
            <p style="color: #666; font-size: 13px; margin-bottom: 15px;">
                完整交易记录共 {len(sf_trades) + len(sm_trades)} 条，此处显示前 100 条
            </p>
            <table>
                <thead>
                    <tr>
                        <th>品种</th>
                        <th>时间</th>
                        <th>方向</th>
                        <th>类型</th>
                        <th>价格</th>
                        <th>盈亏</th>
                        <th>原因</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    '''


def generate_chart_scripts(sf, sm):
    """生成图表 JavaScript 代码"""
    # 硅铁月度数据
    sf_monthly = sf.get('monthly_pnl', {}) if sf else {}
    sf_labels = list(sf_monthly.keys())[:12]
    sf_data = [sf_monthly.get(m, 0) for m in sf_labels]
    
    # 锰硅月度数据
    sm_monthly = sm.get('monthly_pnl', {}) if sm else {}
    sm_labels = list(sm_monthly.keys())[:12]
    sm_data = [sm_monthly.get(m, 0) for m in sm_labels]
    
    return f'''
        // 硅铁资金曲线
        new Chart(document.getElementById('capitalChart_SF'), {{
            type: 'line',
            data: {{
                labels: {sf_labels},
                datasets: [{{
                    label: '硅铁资金曲线',
                    data: {sf_data},
                    borderColor: 'rgba(102, 126, 234, 1)',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
        
        // 硅铁月度盈亏
        new Chart(document.getElementById('monthlyChart_SF'), {{
            type: 'bar',
            data: {{
                labels: {sf_labels},
                datasets: [{{
                    label: '月度盈亏',
                    data: {sf_data},
                    backgroundColor: {['rgba(46, 204, 113, 0.7)' if v > 0 else 'rgba(231, 76, 60, 0.7)' for v in sf_data]}
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
        
        // 锰硅资金曲线
        new Chart(document.getElementById('capitalChart_SM'), {{
            type: 'line',
            data: {{
                labels: {sm_labels},
                datasets: [{{
                    label: '锰硅资金曲线',
                    data: {sm_data},
                    borderColor: 'rgba(118, 75, 162, 1)',
                    backgroundColor: 'rgba(118, 75, 162, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
        
        // 锰硅月度盈亏
        new Chart(document.getElementById('monthlyChart_SM'), {{
            type: 'bar',
            data: {{
                labels: {sm_labels},
                datasets: [{{
                    label: '月度盈亏',
                    data: {sm_data},
                    backgroundColor: {['rgba(46, 204, 113, 0.7)' if v > 0 else 'rgba(231, 76, 60, 0.7)' for v in sm_data]}
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.05)' }} }},
                    x: {{ grid: {{ display: false }} }}
                }}
            }}
        }});
    '''


if __name__ == "__main__":
    # 加载回测结果
    with open('backtest_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # 生成 HTML 报告
    generate_html_report(results, 'backtest-report.html')
    print("✅ 报告生成完成！")
