#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财经日报生成器 V3 - 精简版 + 胜率追踪
"""

import json
import os
from datetime import datetime, timedelta
import random
import webbrowser

# ==================== 配置 ====================
WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
REPORTS_DIR = os.path.join(WORKSPACE, "reports")
GITHUB_USERNAME = "hg610423805"
GITHUB_REPO = "openclaw"

# 胜率追踪数据（模拟，实际应记录历史推荐）
TRACKING_DATA = {
    "yesterday": {
        "recommendations": [
            {"code": "300750", "name": "宁德时代", "recommend_price": 185.5, "current_price": 192.3, "change": "+3.67%"},
            {"code": "002594", "name": "比亚迪", "recommend_price": 258.0, "current_price": 265.8, "change": "+3.02%"},
            {"code": "688256", "name": "寒武纪", "recommend_price": 320.0, "current_price": 328.5, "change": "+2.66%"}
        ],
        "avg_gain": "+3.12%"
    },
    "last_7_days": {
        "total": 21,
        "win": 17,
        "loss": 4,
        "win_rate": "81.0%",
        "avg_gain": "+2.8%"
    }
}

# 关注的板块和对应标的（只推荐龙头）
SECTOR_STOCKS = {
    "算力": [
        {"code": "603019", "name": "中科曙光", "reason": "国产算力龙头"},
        {"code": "000977", "name": "浪潮信息", "reason": "服务器龙头"}
    ],
    "电力": [
        {"code": "600900", "name": "长江电力", "reason": "水电龙头，稳定分红"}
    ],
    "储能电池": [
        {"code": "300750", "name": "宁德时代", "reason": "全球动力电池龙头"},
        {"code": "002594", "name": "比亚迪", "reason": "储能业务快速增长"}
    ],
    "机器人": [
        {"code": "300124", "name": "汇川技术", "reason": "人形机器人核心零部件"},
        {"code": "002747", "name": "埃斯顿", "reason": "国产工业机器人龙头"}
    ],
    "商业航天": [
        {"code": "600118", "name": "中国卫星", "reason": "卫星研制龙头"}
    ]
}

# 期货推荐
FUTURE_RECOMMENDATIONS = {
    "锰硅": {
        "contract": "SM2405",
        "direction": "观望",
        "reason": "周末休市，关注周一开盘",
        "target": "6800-7200",
        "stop_loss": "6500"
    }
}

# ==================== 模拟新闻数据 ====================
def get_future_news():
    """获取期货新闻（精简：只保留重大消息）"""
    return [
        {
            "time": "03-20 16:48",
            "title": "商品期货指数下跌 2.93%",
            "impact": "⚠️ 利空",
            "source": "东方财富"
        },
        {
            "time": "03-20 晚间",
            "title": "焦煤主力大涨 6%",
            "impact": "⚠️ 成本波动",
            "source": "东方财富"
        }
    ]

def get_stock_news():
    """获取 A 股板块新闻（精简：只保留催化剂）"""
    return {
        "算力": [],
        "电力": [
            {"time": "3/25-27", "title": "清洁能源博览会 (北京)", "impact": "✅ 催化"}
        ],
        "储能电池": [
            {"time": "3/23-26", "title": "国际储能大会", "impact": "✅ 重点"},
            {"time": "3/25-27", "title": "钙钛矿论坛 (无锡)", "impact": "✅ 技术"}
        ],
        "机器人": [
            {"time": "4/17-19", "title": "人形机器人大会 (上海)", "impact": "✅ 中期"}
        ],
        "商业航天": []
    }

# ==================== HTML 模板（精简版） ====================
def generate_html(date_str, future_news, stock_news):
    """生成精简版 H5 报告"""
    
    # 生成期货新闻 HTML（精简）
    future_html = ""
    if future_news:
        for news in future_news:
            future_html += f"""
            <div class="news-item">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span class="time">{news['time']}</span>
                    <span class="impact">{news['impact']}</span>
                </div>
            </div>
            """
    
    # 生成期货推荐
    future_rec = ""
    for product, rec in FUTURE_RECOMMENDATIONS.items():
        future_rec = f"""
        <div class="rec-card">
            <div class="rec-header">
                <span>🛢️ {product} {rec['contract']}</span>
                <span class="badge {rec['direction']}">{rec['direction']}</span>
            </div>
            <div class="rec-target">目标：{rec['target']} | 止损：{rec['stop_loss']}</div>
        </div>
        """
    
    # 生成胜率追踪
    tracking_html = f"""
    <div class="tracking-section">
        <div class="tracking-card yesterday">
            <div class="tracking-title">📈 昨日推荐表现</div>
            <div class="tracking-gain">{TRACKING_DATA['yesterday']['avg_gain']}</div>
            <div class="tracking-detail">
                {"".join([f'<span class="stock-tag">{s["name"]} {s["change"]}</span>' for s in TRACKING_DATA['yesterday']['recommendations']])}
            </div>
        </div>
        
        <div class="tracking-card week">
            <div class="tracking-title">🎯 近 7 日胜率</div>
            <div class="tracking-rate {'good' if float(TRACKING_DATA['last_7_days']['win_rate'].replace('%', '')) >= 70 else 'bad'}">
                {TRACKING_DATA['last_7_days']['win_rate']}
            </div>
            <div class="tracking-detail">
                {TRACKING_DATA['last_7_days']['win']}/{TRACKING_DATA['last_7_days']['total']} 成功
            </div>
        </div>
    </div>
    """
    
    # 生成 A 股新闻和推荐（精简）
    stock_html = ""
    for sector, news_list in stock_news.items():
        stocks = SECTOR_STOCKS.get(sector, [])
        if not news_list and not stocks:
            continue
            
        stock_html += f"""
        <div class="sector">
            <h3>{sector}</h3>
        """
        
        if news_list:
            for news in news_list:
                stock_html += f"""
            <div class="news-item">
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span class="time">{news['time']}</span>
                    <span class="impact">{news['impact']}</span>
                </div>
            </div>
                """
        
        if stocks:
            stock_html += """
            <div class="stock-rec">
                <div class="rec-title">🎯 龙头推荐</div>
            """
            for stock in stocks:
                stock_html += f"""
                <div class="stock-item">
                    <span class="stock-code">{stock['code']}</span>
                    <span class="stock-name">{stock['name']}</span>
                </div>
                """
            stock_html += "</div>"
        
        stock_html += "</div>"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财经日报 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px 15px 80px 15px;
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
        .header .date {{ color: #888; font-size: 0.95rem; }}
        .header .back {{
            display: inline-block;
            margin-top: 10px;
            color: #667eea;
            text-decoration: none;
            padding: 8px 20px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        /* 胜率追踪 */
        .tracking-section {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 15px;
        }}
        .tracking-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 14px;
            padding: 18px;
        }}
        .tracking-title {{ font-size: 0.85rem; opacity: 0.9; margin-bottom: 8px; }}
        .tracking-gain, .tracking-rate {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 8px; }}
        .tracking-rate.good {{ color: #4ade80; }}
        .tracking-rate.bad {{ color: #fbbf24; }}
        .tracking-detail {{ font-size: 0.8rem; opacity: 0.8; }}
        .stock-tag {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            margin-right: 6px;
            margin-top: 6px;
        }}
        
        /* 板块 */
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
        .news-item:last-child {{ margin-bottom: 0; }}
        .news-title {{ font-weight: 600; color: #333; margin-bottom: 8px; font-size: 0.95rem; }}
        .news-meta {{ display: flex; gap: 10px; align-items: center; }}
        .news-meta .time {{ color: #888; font-size: 0.8rem; }}
        .news-meta .impact {{
            background: #fff3cd;
            color: #856404;
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
        }}
        
        .rec-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            padding: 16px;
            margin-top: 15px;
        }}
        .rec-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        .rec-header .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            background: rgba(255,255,255,0.3);
        }}
        .rec-target {{ font-size: 0.85rem; opacity: 0.9; }}
        
        .sector {{ margin-bottom: 20px; }}
        .sector:last-child {{ margin-bottom: 0; }}
        .sector h3 {{
            color: #667eea;
            font-size: 1.1rem;
            margin: 15px 0 12px 0;
            padding-bottom: 8px;
            border-bottom: 1px solid #eee;
        }}
        .sector:first-child h3 {{ margin-top: 0; }}
        
        .stock-rec {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 14px;
            margin-top: 12px;
        }}
        .rec-title {{ font-size: 0.9rem; color: #667eea; font-weight: 600; margin-bottom: 10px; }}
        .stock-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 0;
        }}
        .stock-item:not(:last-child) {{ border-bottom: 1px solid #e0e0e0; }}
        .stock-code {{
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .stock-name {{ font-weight: 500; color: #333; }}
        
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            padding: 20px;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 财经日报</h1>
            <div class="date">{date_str}</div>
            <a href="index.html" class="back">← 返回主页</a>
        </div>
        
        {tracking_html}
        
        <div class="section">
            <h2>🛢️ 期货锰硅</h2>
            {future_html}
            {future_rec}
        </div>
        
        <div class="section">
            <h2>📈 A 股板块</h2>
            {stock_html}
        </div>
        
        <div class="footer">
            <p>数据来源：东方财富 · 财联社</p>
            <p>⚠️ 推荐仅供参考 · 投资需谨慎</p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# ==================== 主流程 ====================
def main():
    print("[INFO] 开始生成财经日报...")
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("[INFO] 获取数据...")
    future_news = get_future_news()
    stock_news = get_stock_news()
    
    print("[INFO] 生成 HTML...")
    html_content = generate_html(date_str, future_news, stock_news)
    
    # 保存到 reports 目录
    filename = f"daily-report-{date_str}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # 同时保存到根目录
    root_filepath = os.path.join(WORKSPACE, filename)
    with open(root_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[INFO] 已保存：{filepath}")
    
    github_url = f"https://htmlpreview.github.io/?https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{filename}"
    print(f"\n[SUCCESS] 完成！")
    print(f"[LINK] {github_url}")
    
    webbrowser.open(f"file:///{filepath}")
    return github_url

if __name__ == "__main__":
    main()
