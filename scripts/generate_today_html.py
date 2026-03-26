# -*- coding: utf-8 -*-
"""
生成今日财经日报 HTML
"""
import os
from datetime import datetime

WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
GITHUB_USERNAME = "hg610423805"
GITHUB_REPO = "openclaw"

# 今日新闻数据（基于真实抓取）
futures_news = [
    {"time": "08:06", "title": "中信证券：国内煤价有望进入上涨通道，涨价具备持续性", "impact": "✅ 利好", "source": "人民财讯"},
    {"time": "3/22 晚间", "title": "焦煤期货夜盘大涨近 9%，临汾主焦煤竞拍价涨 206 元/吨", "impact": "✅ 强利好", "source": "我的钢铁网"},
    {"time": "3/22", "title": "锰硅工厂成本走高，挺价情绪浓厚，库存环比增长 9000 吨", "impact": "➖ 中性偏多", "source": "我的钢铁网"},
    {"time": "07:10", "title": "霍尔木兹海峡局势紧张，伊朗阐述通行原则", "impact": "⚠️ 间接影响", "source": "东方财富"},
]

stock_news = {
    "算力": [
        {"time": "今日 14:30", "title": "华为春季全场景新品发布会", "impact": "✅ 催化", "stocks": [{"code": "603019", "name": "中科曙光", "reason": "国产算力龙头"}, {"code": "000977", "name": "浪潮信息", "reason": "服务器龙头"}]},
        {"time": "3/24", "title": "Arm 芯片活动", "impact": "✅ 催化"},
        {"time": "3/25-27", "title": "上海国际半导体展览会", "impact": "✅ 中期催化"},
    ],
    "储能电池": [
        {"time": "3/25-27", "title": "第十一届钙钛矿与叠层电池产业化论坛（无锡）", "impact": "✅ 强催化", "stocks": [{"code": "300750", "name": "宁德时代", "reason": "全球动力电池龙头"}, {"code": "002594", "name": "比亚迪", "reason": "储能业务快速增长"}]},
        {"time": "3/25-27", "title": "清洁能源博览会 CEEC 2026（北京）", "impact": "✅ 催化"},
        {"time": "3/27-29", "title": "中国电动汽车百人会论坛", "impact": "✅ 催化"},
    ],
    "电力": [
        {"time": "3/25-27", "title": "第十六届中国国际清洁能源博览会", "impact": "✅ 催化", "stocks": [{"code": "600900", "name": "长江电力", "reason": "水电龙头"}]},
    ],
    "机器人": [
        {"time": "4/17-19", "title": "2026 中国人形机器人生态大会（上海）", "impact": "✅ 中期催化", "stocks": [{"code": "300124", "name": "汇川技术", "reason": "工控龙头"}, {"code": "002747", "name": "埃斯顿", "reason": "工业机器人"}]},
    ],
    "商业航天": [],
}

analysis = {
    "trend": "逢低做多",
    "reason": "焦煤大涨 9% + 中信证券研报背书 + 成本端强支撑",
    "target": "成本推动上涨 5-8%",
    "stop": "前低支撑",
    "confidence": "中等",
}

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财经日报 - {datetime.now().strftime("%Y-%m-%d")}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft YaHei", sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            padding: 15px 15px 80px; 
        }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        .header {{ 
            background: white; 
            border-radius: 16px; 
            padding: 20px; 
            margin-bottom: 15px; 
            text-align: center; 
        }}
        .header h1 {{ color: #667eea; font-size: 1.8rem; margin-bottom: 10px; }}
        .header .datetime {{ color: #888; font-size: 0.95rem; }}
        .header .badge {{ 
            display: inline-block; 
            background: linear-gradient(135deg, #ef4444, #dc2626); 
            color: white; 
            padding: 4px 12px; 
            border-radius: 20px; 
            font-size: 0.75rem; 
            margin-top: 8px; 
        }}
        .section {{ 
            background: white; 
            border-radius: 16px; 
            padding: 20px; 
            margin-bottom: 15px; 
        }}
        .section h2 {{ 
            color: #333; 
            font-size: 1.3rem; 
            margin-bottom: 15px; 
            padding-bottom: 12px; 
            border-bottom: 2px solid #667eea; 
        }}
        .news-item {{ 
            background: #f8f9fa; 
            border-radius: 10px; 
            padding: 14px; 
            margin-bottom: 10px; 
        }}
        .news-title {{ 
            font-weight: 600; 
            color: #333; 
            margin-bottom: 8px; 
            font-size: 0.9rem; 
        }}
        .news-meta {{ 
            display: flex; 
            gap: 8px; 
            align-items: center; 
            flex-wrap: wrap; 
        }}
        .news-meta .time, .news-meta .source {{ 
            color: #888; 
            font-size: 0.75rem; 
        }}
        .news-meta .impact {{ 
            padding: 2px 8px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
        }}
        .impact-good {{ background: #d1fae5; color: #065f46; }}
        .impact-neutral {{ background: #fff3cd; color: #856404; }}
        .impact-warning {{ background: #fee2e2; color: #991b1b; }}
        .analysis-card {{ 
            background: linear-gradient(135deg, #667eea, #764ba2); 
            color: white; 
            border-radius: 14px; 
            padding: 20px; 
            margin-top: 15px; 
        }}
        .analysis-header {{ 
            display: flex; 
            justify-content: space-between; 
            margin-bottom: 15px; 
        }}
        .trend {{ font-size: 1rem; font-weight: 700; }}
        .analysis-reasoning {{ 
            background: rgba(255,255,255,0.1); 
            padding: 12px; 
            border-radius: 8px; 
            font-size: 0.85rem; 
            line-height: 1.6; 
            margin-bottom: 15px; 
        }}
        .analysis-action {{ 
            display: grid; 
            grid-template-columns: repeat(3, 1fr); 
            gap: 10px; 
        }}
        .action-item {{ 
            background: rgba(255,255,255,0.15); 
            padding: 10px; 
            border-radius: 8px; 
            text-align: center; 
        }}
        .action-item .label {{ font-size: 0.75rem; opacity: 0.8; display: block; margin-bottom: 4px; }}
        .action-item .value {{ font-size: 0.9rem; font-weight: 700; }}
        .sector-card {{ 
            background: #f8f9fa; 
            border-radius: 12px; 
            padding: 18px; 
            margin-bottom: 15px; 
        }}
        .sector-header {{ 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-bottom: 12px; 
        }}
        .sector-header h3 {{ color: #667eea; font-size: 1.1rem; }}
        .sector-header .rating {{ font-size: 0.9rem; }}
        .sector-stocks {{ 
            background: white; 
            border-radius: 10px; 
            padding: 12px; 
            margin-top: 10px; 
        }}
        .stocks-title {{ font-size: 0.85rem; color: #667eea; font-weight: 600; margin-bottom: 10px; }}
        .stock-item {{ 
            display: flex; 
            align-items: flex-start; 
            gap: 10px; 
            padding: 10px 0; 
            border-bottom: 1px solid #eee; 
        }}
        .stock-item:last-child {{ border-bottom: none; }}
        .stock-code {{ 
            background: #667eea; 
            color: white; 
            padding: 3px 8px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
            font-weight: 600; 
            flex-shrink: 0; 
        }}
        .stock-name {{ font-weight: 600; color: #333; font-size: 0.9rem; }}
        .stock-reason {{ color: #666; font-size: 0.8rem; line-height: 1.4; }}
        .footer {{ 
            text-align: center; 
            color: rgba(255,255,255,0.8); 
            padding: 20px; 
            font-size: 0.85rem; 
        }}
        .highlight {{ 
            background: linear-gradient(135deg, #fbbf24, #f59e0b); 
            color: white; 
            padding: 15px; 
            border-radius: 12px; 
            margin-bottom: 15px; 
            text-align: center; 
        }}
        .highlight h3 {{ font-size: 1.1rem; margin-bottom: 5px; }}
        .highlight p {{ font-size: 0.9rem; opacity: 0.95; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 财经日报</h1>
            <div class="datetime">{datetime.now().strftime("%Y-%m-%d")} 周一</div>
            <div class="badge">🔥 补发推送</div>
        </div>

        <div class="highlight">
            <h3>🎯 今日重点</h3>
            <p>期货：焦煤大涨 9% → 锰硅成本端强支撑 | A 股：储能电池本周密集催化</p>
        </div>

        <div class="section">
            <h2>🛢️ 期货锰硅/硅锰</h2>
'''

for n in futures_news:
    impact_class = "impact-good" if "利好" in n["impact"] else ("impact-warning" if "利空" in n["impact"] else "impact-neutral")
    html_content += f'''
            <div class="news-item">
                <div class="news-title">{n["title"]}</div>
                <div class="news-meta">
                    <span class="time">🕐 {n["time"]}</span>
                    <span class="source">📰 {n["source"]}</span>
                    <span class="impact {impact_class}">{n["impact"]}</span>
                </div>
            </div>
'''

html_content += f'''
            <div class="analysis-card">
                <div class="analysis-header">
                    <span class="trend">🎯 建议：{analysis["trend"]}</span>
                    <span>置信度：{analysis["confidence"]}</span>
                </div>
                <div class="analysis-reasoning">
                    <strong>📝 核心逻辑：</strong>{analysis["reason"]}
                </div>
                <div class="analysis-action">
                    <div class="action-item">
                        <span class="label">目标</span>
                        <span class="value">{analysis["target"]}</span>
                    </div>
                    <div class="action-item">
                        <span class="label">止损</span>
                        <span class="value">{analysis["stop"]}</span>
                    </div>
                    <div class="action-item">
                        <span class="label">评级</span>
                        <span class="value">⭐⭐⭐⭐</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>📈 A 股板块</h2>
'''

sector_ratings = {
    "储能电池": "⭐⭐⭐⭐⭐",
    "算力": "⭐⭐⭐⭐",
    "电力": "⭐⭐⭐",
    "机器人": "⭐⭐⭐",
    "商业航天": "⭐⭐",
}

for sector, news in stock_news.items():
    if not news:
        continue
    rating = sector_ratings.get(sector, "⭐⭐")
    html_content += f'''
            <div class="sector-card">
                <div class="sector-header">
                    <h3>{"🔋" if sector == "储能电池" else "💻" if sector == "算力" else "⚡" if sector == "电力" else "🤖" if sector == "机器人" else "🚀"} {sector}</h3>
                    <span class="rating">{rating}</span>
                </div>
'''
    for n in news[:3]:
        html_content += f'''
                <div class="news-item">
                    <div class="news-title">{n["title"]}</div>
                    <div class="news-meta">
                        <span class="time">🕐 {n["time"]}</span>
                        <span class="impact impact-good">{n["impact"]}</span>
                    </div>
                </div>
'''
    
    # 添加股票推荐
    if "stocks" in news[0]:
        html_content += '''
                <div class="sector-stocks">
                    <div class="stocks-title">🎯 龙头股</div>
'''
        for stock in news[0]["stocks"]:
            html_content += f'''
                    <div class="stock-item">
                        <span class="stock-code">{stock["code"]}</span>
                        <span class="stock-name">{stock["name"]}</span>
                        <span class="stock-reason">{stock["reason"]}</span>
                    </div>
'''
        html_content += '''
                </div>
'''
    
    html_content += '''
            </div>
'''

html_content += f'''
        </div>

        <div class="footer">
            <p>📊 数据来源：东方财富期货 · 财联社 · 我的钢铁网 · 新浪财经</p>
            <p>⚠️ 投资有风险，入市需谨慎</p>
            <p style="margin-top: 10px; opacity: 0.7;">🐱 咕噜 AI 生成 | 下次推送：明日 08:00</p>
        </div>
    </div>
</body>
</html>
'''

# 保存文件
date_str = datetime.now().strftime("%Y-%m-%d")
filename = f"daily-report-{date_str}.html"

with open(os.path.join(WORKSPACE, filename), 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'SUCCESS: HTML generated - {filename}')
print(f'Path: {os.path.join(WORKSPACE, filename)}')
print(f'GitHub Pages URL: https://{GITHUB_USERNAME}.github.io/{GITHUB_REPO}/{filename}')
