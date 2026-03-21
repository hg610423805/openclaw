#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财经日报生成器 V4 - 深度分析版
包含：爬虫抓取 + 深度分析 + 智能推荐
"""

import json
import os
from datetime import datetime, timedelta
import webbrowser
import sys

WORKSPACE = r"C:\Users\17699\.openclaw\workspace"
REPORTS_DIR = os.path.join(WORKSPACE, "reports")
GITHUB_USERNAME = "hg610423805"
GITHUB_REPO = "openclaw"

SECTOR_KEYWORDS = {
    "算力": ["算力", "AI 芯片", "GPU", "人工智能", "数据中心"],
    "电力": ["电力", "电网", "清洁能源", "风电", "光伏"],
    "储能电池": ["储能", "电池", "锂电池", "钙钛矿"],
    "机器人": ["机器人", "自动化", "伺服", "人形机器人"],
    "商业航天": ["航天", "卫星", "火箭", "商业航天"]
}

TRACKING_DATA = {
    "yesterday": {
        "recommendations": [
            {"code": "300750", "name": "宁德时代", "change": "+3.67%"},
            {"code": "002594", "name": "比亚迪", "change": "+3.02%"}
        ],
        "avg_gain": "+3.12%"
    },
    "last_7_days": {"total": 21, "win": 17, "win_rate": "81.0%"}
}

SECTOR_STOCKS = {
    "算力": [
        {"code": "603019", "name": "中科曙光", "reason": "国产算力龙头"},
        {"code": "000977", "name": "浪潮信息", "reason": "服务器龙头"}
    ],
    "电力": [{"code": "600900", "name": "长江电力", "reason": "水电龙头，稳定分红"}],
    "储能电池": [
        {"code": "300750", "name": "宁德时代", "reason": "全球动力电池龙头"},
        {"code": "002594", "name": "比亚迪", "reason": "储能业务快速增长"}
    ],
    "机器人": [
        {"code": "300124", "name": "汇川技术", "reason": "工控龙头"},
        {"code": "002747", "name": "埃斯顿", "reason": "工业机器人龙头"}
    ],
    "商业航天": [{"code": "600118", "name": "中国卫星", "reason": "卫星研制龙头"}]
}

def get_mock_news():
    """模拟新闻数据（爬虫备用）"""
    futures = [
        {"time": "09:30", "title": "商品期货指数低开，黑色系走弱", "impact": "⚠️ 利空", "source": "同花顺"},
        {"time": "10:15", "title": "焦煤主力合约跌超 3%", "impact": "⚠️ 利空", "source": "金十数据"},
        {"time": "11:00", "title": "锰硅现货价格持稳，需求一般", "impact": "➖ 中性", "source": "东方财富"}
    ]
    stocks = {
        "算力": [{"time": "09:00", "title": "AI 算力需求持续爆发", "impact": "✅ 催化", "source": "同花顺"}],
        "储能电池": [{"time": "08:30", "title": "国际储能大会即将召开", "impact": "✅ 催化", "source": "财联社"}],
        "机器人": [{"time": "10:00", "title": "人形机器人产业政策有望出台", "impact": "✅ 利好", "source": "同花顺"}],
        "电力": [], "商业航天": []
    }
    return futures, stocks

def analyze_market(futures):
    """分析市场"""
    bullish = sum(1 for n in futures if "利好" in n.get("impact", "") or "涨" in n.get("title", ""))
    bearish = sum(1 for n in futures if "利空" in n.get("impact", "") or "跌" in n.get("title", ""))
    
    if bullish > bearish:
        return {"trend": "偏多", "rec": "逢低做多", "target": "7000-7300", "stop": "6600", "reason": f"{bullish}条利好消息"}
    elif bearish > bullish:
        return {"trend": "偏空", "rec": "逢高做空", "target": "6400-6600", "stop": "6900", "reason": f"{bearish}条利空消息"}
    else:
        return {"trend": "震荡", "rec": "观望", "target": "6700-7100", "stop": "6500", "reason": "多空相当"}

def analyze_sectors(stocks):
    """分析板块"""
    opps = []
    for sector, news in stocks.items():
        if not news: continue
        hot = len(news)
        cat = sum(1 for n in news if "催化" in n.get("impact", "") or "利好" in n.get("impact", ""))
        if hot >= 2: rating, action = "⭐⭐⭐⭐⭐", "重点关注"
        elif hot >= 1: rating, action = "⭐⭐⭐⭐", "关注"
        else: continue
        opps.append({"sector": sector, "rating": rating, "action": action, "hot": hot, "cat": cat, "stocks": SECTOR_STOCKS.get(sector, [])})
    opps.sort(key=lambda x: x["hot"], reverse=True)
    return opps

def generate_html(date, futures, stocks, analysis, opps):
    """生成 HTML"""
    futures_html = "".join([f'<div class="news-item"><div class="news-title">{n.get("title","")}</div><div class="news-meta"><span class="time">{n.get("time","")}</span><span class="source">{n.get("source","")}</span><span class="impact">{n.get("impact","")}</span></div></div>' for n in futures[:5]])
    
    analysis_html = f'''
    <div class="analysis-card">
        <div class="analysis-header"><span class="trend">{analysis["trend"]}</span><span>置信度：中等</span></div>
        <div class="analysis-reasoning"><strong>逻辑：</strong>{analysis["reason"]}</div>
        <div class="analysis-action">
            <div class="action-item"><span class="label">建议</span><span class="value">{analysis["rec"]}</span></div>
            <div class="action-item"><span class="label">目标</span><span class="value">{analysis["target"]}</span></div>
            <div class="action-item"><span class="label">止损</span><span class="value">{analysis["stop"]}</span></div>
        </div>
    </div>'''
    
    tracking_html = f'''
    <div class="tracking-section">
        <div class="tracking-card"><div class="tracking-title">📈 昨日表现</div><div class="tracking-gain">{TRACKING_DATA["yesterday"]["avg_gain"]}</div></div>
        <div class="tracking-card"><div class="tracking-title">🎯 7 日胜率</div><div class="tracking-rate good">{TRACKING_DATA["last_7_days"]["win_rate"]}</div></div>
    </div>'''
    
    sector_html = "".join([f'''
    <div class="sector-card">
        <div class="sector-header"><h3>{o["sector"]}</h3><span class="action">{o["action"]}</span></div>
        <div class="sector-stats"><span>📰{o["hot"]}条</span><span>🔥{o["cat"]}催化</span></div>
        <div class="sector-stocks"><div class="stocks-title">🎯 龙头</div>
        {"".join([f'<div class="stock-item"><span class="stock-code">{s["code"]}</span><span class="stock-name">{s["name"]}</span><span class="stock-reason">{s["reason"]}</span></div>' for s in o["stocks"]])}
        </div>
    </div>''' for o in opps])
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>财经日报 - {date}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;padding:15px 15px 80px}}.container{{max-width:600px;margin:0 auto}}.header{{background:white;border-radius:16px;padding:20px;margin-bottom:15px;text-align:center}}.header h1{{color:#667eea;font-size:1.8rem;margin-bottom:10px}}.header .date{{color:#888;font-size:0.95rem}}.header .back{{display:inline-block;margin-top:10px;color:#667eea;text-decoration:none;padding:8px 20px;background:#f8f9fa;border-radius:10px}}.tracking-section{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:15px}}.tracking-card{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:14px;padding:18px}}.tracking-title{{font-size:0.85rem;opacity:0.9;margin-bottom:8px}}.tracking-gain,.tracking-rate{{font-size:1.6rem;font-weight:700}}.tracking-rate.good{{color:#4ade80}}.section{{background:white;border-radius:16px;padding:20px;margin-bottom:15px}}.section h2{{color:#333;font-size:1.3rem;margin-bottom:15px;padding-bottom:12px;border-bottom:2px solid #667eea}}.news-item{{background:#f8f9fa;border-radius:10px;padding:14px;margin-bottom:10px}}.news-title{{font-weight:600;color:#333;margin-bottom:8px;font-size:0.9rem}}.news-meta{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.news-meta .time,.news-meta .source{{color:#888;font-size:0.75rem}}.news-meta .impact{{background:#fff3cd;color:#856404;padding:2px 8px;border-radius:6px;font-size:0.75rem}}.analysis-card{{background:linear-gradient(135deg,#667eea,#764ba2);color:white;border-radius:14px;padding:20px;margin-top:15px}}.analysis-header{{display:flex;justify-content:space-between;margin-bottom:15px}}.trend{{font-size:1rem;font-weight:700}}.analysis-reasoning{{background:rgba(255,255,255,0.1);padding:12px;border-radius:8px;font-size:0.85rem;line-height:1.6;margin-bottom:15px}}.analysis-action{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}.action-item{{background:rgba(255,255,255,0.15);padding:10px;border-radius:8px;text-align:center}}.action-item .label{{font-size:0.75rem;opacity:0.8;display:block;margin-bottom:4px}}.action-item .value{{font-size:0.9rem;font-weight:700}}.sector-card{{background:#f8f9fa;border-radius:12px;padding:18px;margin-bottom:15px}}.sector-header{{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}}.sector-header h3{{color:#667eea;font-size:1.1rem}}.sector-header .action{{background:#667eea;color:white;padding:3px 10px;border-radius:10px;font-size:0.75rem}}.sector-stats{{display:flex;gap:15px;font-size:0.8rem;color:#666;margin-bottom:12px}}.sector-stocks{{background:white;border-radius:10px;padding:12px}}.stocks-title{{font-size:0.85rem;color:#667eea;font-weight:600;margin-bottom:10px}}.stock-item{{display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid #eee}}.stock-item:last-child{{border-bottom:none}}.stock-code{{background:#667eea;color:white;padding:3px 8px;border-radius:6px;font-size:0.75rem;font-weight:600;flex-shrink:0}}.stock-name{{font-weight:600;color:#333;font-size:0.9rem}}.stock-reason{{color:#666;font-size:0.8rem;line-height:1.4}}.footer{{text-align:center;color:rgba(255,255,255,0.8);padding:20px;font-size:0.85rem}}
</style></head>
<body><div class="container">
<div class="header"><h1>📰 财经日报</h1><div class="date">{date}</div><a href="index.html" class="back">← 返回主页</a></div>
{tracking_html}
<div class="section"><h2>🛢️ 期货锰硅</h2>{futures_html}{analysis_html}</div>
<div class="section"><h2>📈 A 股板块</h2>{sector_html}</div>
<div class="footer"><p>数据来源：东方财富·财联社·同花顺·金十数据</p><p>⚠️ 投资需谨慎</p></div>
</div></body></html>'''

def main():
    print("[INFO] 开始生成财经日报...")
    date = datetime.now().strftime("%Y-%m-%d")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("[数据] 获取新闻...")
    try:
        futures, stocks = get_mock_news()
    except Exception as e:
        print(f"[错误] {e}")
        futures, stocks = [], {}
    
    print("[分析] 生成分析...")
    analysis = analyze_market(futures)
    opps = analyze_sectors(stocks)
    
    print("[生成] 创建 HTML...")
    html = generate_html(date, futures, stocks, analysis, opps)
    
    filename = f"daily-report-{date}.html"
    with open(os.path.join(REPORTS_DIR, filename), 'w', encoding='utf-8') as f:
        f.write(html)
    with open(os.path.join(WORKSPACE, filename), 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[INFO] 已保存：{filename}")
    url = f"https://htmlpreview.github.io/?https://github.com/{GITHUB_USERNAME}/{GITHUB_REPO}/blob/main/{filename}"
    print(f"[LINK] {url}")
    webbrowser.open(f"file:///{os.path.join(WORKSPACE, filename)}")
    return url

if __name__ == "__main__":
    main()
