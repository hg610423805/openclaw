# -*- coding: utf-8 -*-
"""
回测报告可视化生成器
====================
功能：读取回测结果，生成 HTML 可视化报告

作者：咕噜 🐱
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
from pathlib import Path


def load_backtest_results(data_dir):
    """加载回测结果数据"""
    results = {}
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.csv'):
            symbol = filename.replace(f'_{300}s.csv', '')
            filepath = os.path.join(data_dir, filename)
            df = pd.read_csv(filepath)
            results[symbol] = df
    
    return results


def calculate_strategy_metrics(equity_curve, initial_capital=1000000):
    """计算策略绩效指标"""
    if len(equity_curve) < 2:
        return None
    
    # 基础指标
    returns = equity_curve.pct_change().dropna()
    
    # 累计收益
    total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
    
    # 年化收益（假设 250 个交易日）
    trading_days = len(equity_curve)
    annual_return = (1 + total_return) ** (250 / max(trading_days, 1)) - 1
    
    # 波动率
    volatility = returns.std() * np.sqrt(250)
    
    # 夏普比率（假设无风险利率 3%）
    risk_free_rate = 0.03
    sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
    
    # 最大回撤
    rolling_max = equity_curve.cummax()
    drawdown = (equity_curve - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    # 胜率（需要交易记录）
    # 这里简化计算
    winning_days = (returns > 0).sum()
    total_days = len(returns)
    win_rate = winning_days / total_days if total_days > 0 else 0
    
    # 卡尔玛比率
    calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'win_rate': win_rate,
        'calmar_ratio': calmar_ratio,
        'trading_days': trading_days,
    }


def generate_html_report(results, metrics, output_path):
    """生成 HTML 可视化报告"""
    
    # 准备图表数据
    chart_data = {}
    for symbol, df in results.items():
        if 'datetime' in df.columns and 'close' in df.columns:
            chart_data[symbol] = {
                'dates': df['datetime'].tolist(),
                'close': df['close'].tolist(),
                'volume': df['volume'].tolist() if 'volume' in df.columns else []
            }
    
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🐱 咕噜量化 - 回测报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .metric-value.positive {{
            color: #10b981;
        }}
        
        .metric-value.negative {{
            color: #ef4444;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .chart-title {{
            font-size: 1.5em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        .symbol-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .symbol-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #eee;
        }}
        
        .symbol-name {{
            font-size: 1.8em;
            color: #333;
            font-weight: bold;
        }}
        
        .symbol-metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .symbol-metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .symbol-metric-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .symbol-metric-label {{
            color: #666;
            font-size: 0.85em;
            margin-top: 5px;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            margin-top: 30px;
        }}
        
        .footer a {{
            color: white;
            text-decoration: none;
        }}
        
        canvas {{
            max-height: 400px;
        }}
        
        .loading {{
            text-align: center;
            padding: 50px;
            color: white;
            font-size: 1.5em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐱 咕噜量化回测报告</h1>
            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据周期：2025 年全年 | 5 分钟 K 线</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{len(results)}</div>
                <div class="metric-label">品种数量</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{sum(len(df) for df in results.values()):,}</div>
                <div class="metric-label">总 K 线数</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">5 分钟</div>
                <div class="metric-label">数据精度</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">2025</div>
                <div class="metric-label">回测年份</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2 class="chart-title">📊 数据概览</h2>
            <canvas id="overviewChart"></canvas>
        </div>
'''
    
    # 为每个品种生成详细图表
    for symbol, df in results.items():
        if len(df) == 0:
            continue
            
        clean_symbol = symbol.replace('_', ' ').upper()
        
        # 计算该品种的简单统计
        if 'close' in df.columns:
            price_change = (df['close'].iloc[-1] - df['close'].iloc[0]) / df['close'].iloc[0] * 100
            avg_volume = df['volume'].mean() if 'volume' in df.columns else 0
            
            html_content += f'''
        <div class="symbol-section">
            <div class="symbol-header">
                <div class="symbol-name">{clean_symbol}</div>
            </div>
            
            <div class="symbol-metrics">
                <div class="symbol-metric">
                    <div class="symbol-metric-value">{len(df):,}</div>
                    <div class="symbol-metric-label">K 线数量</div>
                </div>
                <div class="symbol-metric">
                    <div class="symbol-metric-value">{df['close'].iloc[0]:.2f}</div>
                    <div class="symbol-metric-label">开盘价</div>
                </div>
                <div class="symbol-metric">
                    <div class="symbol-metric-value">{df['close'].iloc[-1]:.2f}</div>
                    <div class="symbol-metric-label">收盘价</div>
                </div>
                <div class="symbol-metric">
                    <div class="symbol-metric-value {'positive' if price_change > 0 else 'negative'}">{price_change:+.2f}%</div>
                    <div class="symbol-metric-label">期间涨跌</div>
                </div>
                <div class="symbol-metric">
                    <div class="symbol-metric-value">{df['high'].max():.2f}</div>
                    <div class="symbol-metric-label">最高价</div>
                </div>
                <div class="symbol-metric">
                    <div class="symbol-metric-value">{df['low'].min():.2f}</div>
                    <div class="symbol-metric-label">最低价</div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <canvas id="chart_{symbol}"></canvas>
            </div>
        </div>
'''
    
    html_content += '''
        <div class="footer">
            <p>🐱 Generated by 咕噜 Quant | Made with ❤️ for 爸爸</p>
        </div>
    </div>
    
    <script>
        // 全局配置
        Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto';
        Chart.defaults.color = '#666';
        
        // 颜色方案
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c', 
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#fa709a', '#fee140', '#30cfd0', '#330867'
        ];
        
        // 数据
        const chartData = ''' + json.dumps(chart_data, ensure_ascii=False) + ''';
        
        // 创建概览图表
        const overviewCtx = document.getElementById('overviewChart').getContext('2d');
        const overviewDatasets = Object.keys(chartData).slice(0, 5).map((symbol, index) => {
            const data = chartData[symbol];
            return {
                label: symbol,
                data: data.dates.map((date, i) => ({
                    x: date,
                    y: data.close[i]
                })),
                borderColor: colors[index % colors.length],
                backgroundColor: colors[index % colors.length] + '20',
                tension: 0.1,
                pointRadius: 0
            };
        });
        
        new Chart(overviewCtx, {
            type: 'line',
            data: {
                datasets: overviewDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'month',
                            displayFormats: {
                                month: 'MMM yyyy'
                            }
                        },
                        title: {
                            display: true,
                            text: '时间'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: '价格'
                        }
                    }
                }
            }
        });
        
        // 为每个品种创建详细图表
        Object.keys(chartData).forEach((symbol, index) => {
            const canvas = document.getElementById('chart_' + symbol);
            if (!canvas) return;
            
            const data = chartData[symbol];
            const ctx = canvas.getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: {
                    datasets: [{
                        label: symbol + ' 价格走势',
                        data: data.dates.map((date, i) => ({
                            x: date,
                            y: data.close[i]
                        })),
                        borderColor: colors[index % colors.length],
                        backgroundColor: colors[index % colors.length] + '20',
                        tension: 0.1,
                        pointRadius: 0,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'month',
                                displayFormats: {
                                    month: 'MMM yyyy'
                                }
                            },
                            title: {
                                display: true,
                                text: '时间'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '价格 (元)'
                            }
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>
'''
    
    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 报告已生成：{output_path}")
    return output_path


def main():
    """主函数"""
    print("=" * 60)
    print("📊 回测报告生成器")
    print("=" * 60)
    
    # 数据目录
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在：{data_dir}")
        print("请先运行 download_data.py 下载数据")
        return
    
    # 加载数据
    print(f"\n📂 加载数据：{data_dir}")
    results = load_backtest_results(data_dir)
    
    if not results:
        print("❌ 未找到任何数据文件")
        return
    
    print(f"✅ 加载成功：{len(results)} 个品种")
    
    # 生成报告
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"backtest_report_{timestamp}.html")
    
    print(f"\n🎨 生成可视化报告...")
    generate_html_report(results, {}, output_path)
    
    print(f"\n🌐 在浏览器中打开：file:///{output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
