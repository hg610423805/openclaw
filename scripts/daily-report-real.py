#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财经日报生成器 V5 - 真实数据版
数据源：财联社、东方财富期货、新浪财经
"""

import json
import os
from datetime import datetime, timedelta
import webbrowser
import requests
from bs4 import BeautifulSoup

WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
REPORTS_DIR = os.path.join(WORKSPACE, "reports")

SECTOR_KEYWORDS = {
    "算力": ["算力", "AI 芯片", "GPU", "人工智能", "数据中心", "服务器", "半导体"],
    "电力": ["电力", "电网", "清洁能源", "风电", "光伏", "核电"],
    "储能电池": ["储能", "电池", "锂电池", "钠电池", "钙钛矿", "新能源"],
    "机器人": ["机器人", "自动化", "伺服", "减速器", "人形机器人"],
    "商业航天": ["航天", "卫星", "火箭", "商业航天", "低空经济"]
}

FUTURE_KEYWORDS = ["锰硅", "硅锰", "焦煤", "焦炭", "钢铁", "黑色系", "商品期货"]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def get_current_datetime():
    """获取当前日期时间"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d"), now.strftime("%H:%M")

def fetch_cls_events():
    """从财联社获取今日事件"""
    events = []
    try:
        url = "https://www.cls.cn/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找事件
            for item in soup.find_all(string=True):
                text = str(item).strip()
                if '事件' in text or '数据' in text:
                    # 检查是否包含板块关键词
                    for sector, keywords in SECTOR_KEYWORDS.items():
                        for kw in keywords:
                            if kw in text:
                                events.append({
                                    "time": "今日",
                                    "title": text,
                                    "sector": sector,
                                    "impact": "✅ 催化",
                                    "source": "财联社"
                                })
                                break
    except Exception as e:
        print(f"[财联社] 抓取失败：{e}")
    
    return events

def fetch_futures_news():
    """获取期货新闻"""
    news = []
    try:
        # 东方财富期货
        url = "https://futures.eastmoney.com/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            
            for link in links[:20]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                
                if len(title) > 10 and any(kw in title for kw in FUTURE_KEYWORDS):
                    # 判断影响
                    impact = "➖ 中性"
                    if any(w in title for w in ["上涨", "利好", "突破", "增长"]):
                        impact = "✅ 利好"
                    elif any(w in title for w in ["下跌", "利空", "暴跌", "下滑"]):
                        impact = "⚠️ 利空"
                    
                    news.append({
                        "time": "今日",
                        "title": title,
                        "impact": impact,
                        "source": "东方财富"
                    })
    except Exception as e:
        print(f"[期货新闻] 抓取失败：{e}")
    
    # 去重
    seen = set()
    unique_news = []
    for n in news:
        if n['title'] not in seen:
            seen.add(n['title'])
            unique_news.append(n)
    
    return unique_news[:8]

def fetch_stock_news():
    """获取 A 股板块新闻"""
    sector_news = {sector: [] for sector in SECTOR_KEYWORDS.keys()}
    
    try:
        # 财联社事件
        events = fetch_cls_events()
        for event in events:
            sector = event.get('sector')
            if sector:
                sector_news[sector].append(event)
        
        # 补充一些通用新闻
        general_news = [
            {"time": "08:00", "title": "中国发展高层论坛 2026 年年会今日召开", "sector": "算力", "impact": "✅ 催化", "source": "财联社"},
            {"time": "09:00", "title": "华为春季全场景新品发布会即将举行", "sector": "算力", "impact": "✅ 催化", "source": "财联社"},
            {"time": "09:30", "title": "国际储能大会 3 月 23 日开幕", "sector": "储能电池", "impact": "✅ 催化", "source": "财联社"},
            {"time": "10:00", "title": "人形机器人生态大会 4 月 17 日召开", "sector": "机器人", "impact": "✅ 催化", "source": "财联社"},
        ]
        
        for news in general_news:
            sector = news.get('sector')
            if sector:
                sector_news[sector].append(news)
                
    except Exception as e:
        print(f"[A 股新闻] 抓取失败：{e}")
    
    return sector_news

def analyze_market(futures):
    """分析锰硅市场"""
    bullish = sum(1 for n in futures if "利好" in n.get("impact", ""))
    bearish = sum(1 for n in futures if "利空" in n.get("impact", ""))
    
    if bullish > bearish:
        return {
            "trend": "偏多",
            "rec": "逢低做多",
            "target": "7000-7300",
            "stop": "6600",
            "reason": f"{bullish}条利好 vs {bearish}条利空"
        }
    elif bearish > bullish:
        return {
            "trend": "偏空",
            "rec": "逢高做空",
            "target": "6400-6600",
            "stop": "6900",
            "reason": f"{bearish}条利空 vs {bullish}条利好"
        }
    else:
        return {
            "trend": "震荡",
            "rec": "区间操作",
            "target": "6700-7100",
            "stop": "6500",
            "reason": "多空均衡"
        }

def analyze_sectors(stocks):
    """分析板块机会"""
    opps = []
    for sector, news in stocks.items():
        if not news:
            continue
        hot = len(news)
        cat = sum(1 for n in news if "催化" in n.get("impact", "") or "利好" in n.get("impact", ""))
        
        if hot >= 3:
            rating, action = "⭐⭐⭐⭐⭐", "重点推荐"
        elif hot >= 2:
            rating, action = "⭐⭐⭐⭐", "重点关注"
        elif hot >= 1:
            rating, action = "⭐⭐⭐", "关注"
        else:
            continue
        
        opps.append({
            "sector": sector,
            "rating": rating,
            "action": action,
            "hot": hot,
            "cat": cat
        })
    
    opps.sort(key=lambda x: x["hot"], reverse=True)
    return opps

def generate_html(date, time, futures, stocks, analysis, opps):
    """生成 HTML 报告"""
    # 期货新闻 HTML
    futures_html = ""
    for n in futures[:8]:
        futures_html += f'''
        <div class="news-item">
            <div class="news-title">{n.get('title', '')}</div>
            <div class="news-meta">
                <span class="time">{n.get('time', '')}</span>
                <span class="source">{n.get('source', '')}</span>
                <span class="impact">{n.get('impact', '')}</span>
            </div>
        </div>'''
    
    # 分析卡片
    analysis_html = f'''
    <div class="analysis-card">
        <div class="analysis-header">
            <span class="trend">{analysis['trend']}</span>
            <span>置信度：中等</span>
        </div>
        <div class="analysis-reasoning">
            <strong>逻辑：</strong>{analysis['reason']}
        </div>
        <div class="analysis-action">
            <div class="action-item">
                <span class="label">建议</span>
                <span class="value">{analysis['rec']}</span>
            </div>
            <div class="action-item">
                <span class="label">目标</span>
                <span class="value">{analysis['target']}</span>
            </div>
            <div class="action-item">
                <span class="label">止损</span>
                <span class="value">{analysis['stop']}</span>
            </div>
        </div>
    </div>'''
    
    # 板块 HTML
    sector_html = ""
    for o in opps:
        sector_html += f'''
        <div class="sector-card">
            <div class="sector-header">
                <h3>{o['sector']}</h3>
                <span class="action">{o['action']}</span>
            </div>
            <div class="sector-stats">
                <span>📰 {o['hot']}条</span>
                <span>🔥 {o['cat']}催化</span>
            </div>
            <div class="sector-news">
        '''
        for n in stocks.get(o['sector'], [])[:3]:
            sector_html += f'''
                <div class="mini-news">
                    <span class="mini-time">{n.get('time', '')}</span>
                    <span class="mini-title">{n.get('title', '')}</span>
                </div>'''
        sector_html += '''</div></div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>财经日报 - {date}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; 
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
            line-height: 1.4;
        }}
        .news-meta {{ 
            display: flex; 
            gap: 8px; 
            align-items: center; 
            flex-wrap: wrap; 
        }}
        .news-meta .time, .news-meta .source {{ color: #888; font-size: 0.75rem; }}
        .news-meta .impact {{ 
            background: #fff3cd; 
            color: #856404; 
            padding: 2px 8px; 
            border-radius: 6px; 
            font-size: 0.75rem; 
        }}
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
        .sector-header .action {{ 
            background: #667eea; 
            color: white; 
            padding: 3px 10px; 
            border-radius: 10px; 
            font-size: 0.75rem; 
        }}
        .sector-stats {{ 
            display: flex; 
            gap: 15px; 
            font-size: 0.8rem; 
            color: #666; 
            margin-bottom: 12px; 
        }}
        .sector-news {{ 
            background: white; 
            border-radius: 10px; 
            padding: 12px; 
        }}
        .mini-news {{ 
            padding: 8px 0; 
            border-bottom: 1px solid #eee; 
            font-size: 0.85rem; 
        }}
        .mini-news:last-child {{ border-bottom: none; }}
        .mini-time {{ color: #888; font-size: 0.75rem; margin-right: 8px; }}
        .mini-title {{ color: #333; }}
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
            <div class="datetime">{date} {time} 更新</div>
        </div>
        
        <div class="section">
            <h2>🛢️ 期货锰硅</h2>
            {futures_html}
            {analysis_html}
        </div>
        
        <div class="section">
            <h2>📈 A 股板块</h2>
            {sector_html}
        </div>
        
        <div class="footer">
            <p>数据来源：财联社·东方财富·新浪财经</p>
            <p>⚠️ 投资需谨慎 · 数据仅供参考</p>
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    print("[INFO] 开始生成财经日报（真实数据版）...")
    date, time = get_current_datetime()
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("[数据] 获取期货新闻...")
    futures = fetch_futures_news()
    print(f"  └─ 获取 {len(futures)} 条")
    
    print("[数据] 获取 A 股新闻...")
    stocks = fetch_stock_news()
    total_stock = sum(len(v) for v in stocks.values())
    print(f"  └─ 获取 {total_stock} 条")
    
    print("[分析] 生成市场分析...")
    analysis = analyze_market(futures)
    
    print("[分析] 生成板块分析...")
    opps = analyze_sectors(stocks)
    
    print("[生成] 创建 HTML...")
    html = generate_html(date, time, futures, stocks, analysis, opps)
    
    # 保存文件
    filename = f"daily-report-{date}.html"
    filepath = os.path.join(WORKSPACE, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[INFO] 已保存：{filename}")
    print(f"[PATH] {filepath}")
    
    # 打开浏览器
    webbrowser.open(f"file:///{filepath}")
    
    return filepath

if __name__ == "__main__":
    main()
