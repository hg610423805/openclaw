#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财经日报生成器 V2 - 优化版
包含：日期选择 + 标的推荐
"""

import json
import os
from datetime import datetime, timedelta
import webbrowser

# ==================== 配置 ====================
WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
REPORTS_DIR = os.path.join(WORKSPACE, "reports")
GITHUB_USERNAME = "hg610423805"
GITHUB_REPO = "openclaw"

# 关注的板块和对应标的
SECTOR_STOCKS = {
    "算力": [
        {"code": "603019", "name": "中科曙光", "reason": "国产算力龙头，AI 服务器核心供应商"},
        {"code": "000977", "name": "浪潮信息", "reason": "服务器龙头，受益于算力需求爆发"},
        {"code": "688256", "name": "寒武纪", "reason": "AI 芯片龙头，国产替代核心标的"}
    ],
    "电力": [
        {"code": "600900", "name": "长江电力", "reason": "水电龙头，稳定分红"},
        {"code": "600025", "name": "华能水电", "reason": "澜沧江流域水电开发"},
        {"code": "003816", "name": "中国广核", "reason": "核电龙头，清洁能源"}
    ],
    "储能电池": [
        {"code": "300750", "name": "宁德时代", "reason": "全球动力电池龙头，储能业务快速增长"},
        {"code": "002594", "name": "比亚迪", "reason": "新能源车 + 储能双轮驱动"},
        {"code": "300014", "name": "亿纬锂能", "reason": "消费 + 动力 + 储能电池全覆盖"}
    ],
    "机器人": [
        {"code": "002415", "name": "海康威视", "reason": "机器视觉龙头，机器人业务布局"},
        {"code": "300124", "name": "汇川技术", "reason": "工控龙头，人形机器人核心零部件"},
        {"code": "002747", "name": "埃斯顿", "reason": "国产工业机器人龙头"}
    ],
    "商业航天": [
        {"code": "000768", "name": "中航西飞", "reason": "军用飞机龙头，航天业务布局"},
        {"code": "600118", "name": "中国卫星", "reason": "卫星研制龙头"},
        {"code": "002151", "name": "北斗星通", "reason": "北斗导航芯片龙头"}
    ]
}

# 期货标的推荐
FUTURE_RECOMMENDATIONS = {
    "锰硅": {
        "contract": "SM2405",
        "direction": "观望",
        "reason": "周末休市，关注周一开盘焦煤价格传导",
        "target": "6800-7200",
        "stop_loss": "6500"
    }
}

# ==================== 模拟新闻数据 ====================
def get_future_news():
    """获取期货新闻"""
    return [
        {
            "time": "03-20 16:48",
            "title": "商品期货综合指数下跌 2.93%，日内资金净流出",
            "impact": "⚠️ 利空",
            "suggestion": "观望",
            "source": "东方财富"
        },
        {
            "time": "03-20 晚间",
            "title": "焦煤主力合约日内大涨 6.00%",
            "impact": "⚠️ 成本波动",
            "suggestion": "关注黑色系联动",
            "source": "东方财富"
        }
    ]

def get_stock_news():
    """获取 A 股板块新闻"""
    return {
        "算力": [],
        "电力": [
            {
                "time": "03-25-27",
                "title": "第十六届中国国际清洁能源博览会 (北京)",
                "impact": "✅ 催化",
                "suggestion": "关注电力设备",
                "source": "财联社"
            }
        ],
        "储能电池": [
            {
                "time": "03-23-26",
                "title": "2026 年第十六届中国国际储能大会",
                "impact": "✅ 催化",
                "suggestion": "重点关注",
                "source": "财联社"
            },
            {
                "time": "03-25-27",
                "title": "钙钛矿与叠层电池产业化论坛 (无锡)",
                "impact": "✅ 技术催化",
                "suggestion": "关注新技术",
                "source": "财联社"
            }
        ],
        "机器人": [
            {
                "time": "04-17-19",
                "title": "2026 中国人形机器人生态大会 (上海)",
                "impact": "✅ 中期催化",
                "suggestion": "提前布局",
                "source": "财联社"
            }
        ],
        "商业航天": []
    }

def get_historical_dates():
    """获取历史报告日期列表"""
    dates = []
    today = datetime.now()
    for i in range(30):  # 最近 30 天
        date = today - timedelta(days=i)
        dates.append(date.strftime("%Y-%m-%d"))
    return dates

# ==================== HTML 模板 ====================
def generate_html(date_str, future_news, stock_news, current_date=None):
    """生成 H5 报告 HTML"""
    
    if current_date is None:
        current_date = date_str
    
    historical_dates = get_historical_dates()
    
    # 生成日期选项
    date_options = ""
    for d in historical_dates:
        selected = "selected" if d == date_str else ""
        date_options += f'<option value="{d}" {selected}>{d}</option>'
    
    # 生成期货新闻 HTML
    future_html = ""
    if future_news:
        for news in future_news:
            future_html += f"""
            <div class="news-item">
                <div class="news-time">{news['time']}</div>
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span class="impact">{news['impact']}</span>
                    <span class="suggestion">建议：{news['suggestion']}</span>
                    <span class="source">{news['source']}</span>
                </div>
            </div>
            """
    else:
        future_html = '<div class="no-news">今日无重大消息</div>'
    
    # 生成期货推荐 HTML
    future_rec_html = ""
    for product, rec in FUTURE_RECOMMENDATIONS.items():
        future_rec_html += f"""
        <div class="recommendation-card">
            <div class="rec-header">
                <span class="rec-title">🛢️ {product}</span>
                <span class="rec-badge {rec['direction'].lower()}">{rec['direction']}</span>
            </div>
            <div class="rec-contract">合约：{rec['contract']}</div>
            <div class="rec-reason">{rec['reason']}</div>
            <div class="rec-target">目标：{rec['target']} | 止损：{rec['stop_loss']}</div>
        </div>
        """
    
    # 生成 A 股新闻和推荐 HTML
    stock_html = ""
    for sector, news_list in stock_news.items():
        sector_class = "active" if news_list else ""
        stocks = SECTOR_STOCKS.get(sector, [])
        
        stock_html += f"""
        <div class="sector {sector_class}">
            <h3>{sector}</h3>
        """
        
        if news_list:
            for news in news_list:
                stock_html += f"""
            <div class="news-item">
                <div class="news-time">{news['time']}</div>
                <div class="news-title">{news['title']}</div>
                <div class="news-meta">
                    <span class="impact">{news['impact']}</span>
                    <span class="suggestion">建议：{news['suggestion']}</span>
                    <span class="source">{news['source']}</span>
                </div>
            </div>
                """
        else:
            stock_html += '<div class="no-news">无重大消息</div>'
        
        # 添加标的推荐
        if stocks:
            stock_html += """
            <div class="recommendations">
                <h4>🎯 相关标的推荐</h4>
            """
            for stock in stocks:
                stock_html += f"""
                <div class="stock-card">
                    <div class="stock-header">
                        <span class="stock-code">{stock['code']}</span>
                        <span class="stock-name">{stock['name']}</span>
                    </div>
                    <div class="stock-reason">💡 {stock['reason']}</div>
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 600px; margin: 0 auto; }}
        
        /* Header */
        .header {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .header h1 {{ color: #667eea; font-size: 2rem; margin-bottom: 15px; }}
        
        /* Date Selector */
        .date-selector {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .date-selector label {{
            display: block;
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 10px;
        }}
        .date-selector select {{
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1rem;
            background: #f8f9fa;
            transition: border-color 0.3s;
        }}
        .date-selector select:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        /* Section */
        .section {{
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #333;
            font-size: 1.5rem;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #667eea;
        }}
        
        /* News Item */
        .news-item {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #667eea;
        }}
        .news-time {{ color: #999; font-size: 0.85rem; margin-bottom: 8px; }}
        .news-title {{ color: #333; font-size: 1rem; margin-bottom: 10px; font-weight: 600; }}
        .news-meta {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .impact {{
            background: #fff3cd;
            color: #856404;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
        .suggestion {{
            background: #d4edda;
            color: #155724;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
        .source {{
            background: #e2e3e5;
            color: #383d41;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
        .no-news {{
            color: #999;
            text-align: center;
            padding: 20px;
            font-style: italic;
        }}
        
        /* Sector */
        .sector h3 {{
            color: #667eea;
            font-size: 1.2rem;
            margin: 20px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        .sector:first-child h3 {{ margin-top: 0; }}
        
        /* Recommendations */
        .recommendations {{
            margin-top: 20px;
            padding: 20px;
            background: linear-gradient(135deg, #f8f9fa, #e9ecef);
            border-radius: 12px;
        }}
        .recommendations h4 {{
            color: #667eea;
            font-size: 1.1rem;
            margin-bottom: 15px;
        }}
        .stock-card {{
            background: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        .stock-card:last-child {{ margin-bottom: 0; }}
        .stock-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .stock-code {{
            background: #667eea;
            color: white;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .stock-name {{
            font-weight: 600;
            color: #333;
        }}
        .stock-reason {{
            color: #666;
            font-size: 0.9rem;
            line-height: 1.5;
        }}
        
        /* Future Recommendations */
        .recommendation-card {{
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }}
        .rec-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .rec-title {{ font-size: 1.2rem; font-weight: 600; }}
        .rec-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .rec-badge.观望 {{ background: rgba(255,255,255,0.3); }}
        .rec-badge.做多 {{ background: #28a745; }}
        .rec-badge.做空 {{ background: #dc3545; }}
        .rec-contract {{ opacity: 0.9; margin-bottom: 8px; }}
        .rec-reason {{ opacity: 0.9; margin-bottom: 10px; line-height: 1.5; }}
        .rec-target {{
            background: rgba(255,255,255,0.2);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
        }}
        
        /* Footer */
        .footer {{
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        .footer a {{ color: white; text-decoration: underline; }}
        
        /* Back Button */
        .back-btn {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 10px 20px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 15px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📰 财经日报</h1>
            <a href="index.html" class="back-btn">← 返回主页</a>
        </div>
        
        <!-- Date Selector -->
        <div class="date-selector">
            <label>📅 选择日期查看历史报告：</label>
            <select onchange="window.location.href='daily-report-' + this.value + '.html'">
                {date_options}
            </select>
        </div>
        
        <!-- Future Section -->
        <div class="section">
            <h2>🛢️ 期货锰硅</h2>
            {future_html}
            
            <h3 style="margin-top: 25px; color: #667eea;">🎯 操作建议</h3>
            {future_rec_html}
        </div>
        
        <!-- Stock Section -->
        <div class="section">
            <h2>📈 A 股板块</h2>
            {stock_html}
        </div>
        
        <div class="footer">
            <p>数据来源：东方财富、财联社</p>
            <p>🤖 由 咕噜 自动生成</p>
            <p style="margin-top: 15px; font-size: 0.8rem; opacity: 0.7;">
                ⚠️ 投资有风险 · 推荐仅供参考
            </p>
        </div>
    </div>
</body>
</html>"""
    
    return html

# ==================== 主流程 ====================
def main():
    print("[INFO] 开始生成财经日报...")
    
    # 获取日期
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # 确保 reports 目录存在
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # 获取新闻数据
    print("[INFO] 获取期货新闻...")
    future_news = get_future_news()
    
    print("[INFO] 获取 A 股新闻...")
    stock_news = get_stock_news()
    
    # 生成 HTML
    print("[INFO] 生成 HTML 报告...")
    html_content = generate_html(date_str, future_news, stock_news)
    
    # 保存文件到 reports 目录
    filename = f"daily-report-{date_str}.html"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[INFO] 已保存：{filepath}")
    
    # 同时保存一份到根目录（用于 htmlpreview）
    root_filepath = os.path.join(WORKSPACE, filename)
    with open(root_filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[INFO] 已保存：{root_filepath}")
    
    # 生成 GitHub 链接
    github_url = f"https://htmlpreview.github.io/?https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{filename}"
    
    print(f"\n[SUCCESS] 完成！")
    print(f"[LINK] {github_url}")
    
    # 本地打开预览
    webbrowser.open(f"file:///{filepath}")
    
    return github_url

if __name__ == "__main__":
    main()
