#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高质量财经新闻爬虫
数据源：同花顺、金十数据、东方财富
"""

import requests
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time

# ==================== 爬虫配置 ====================
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.10jqka.com.cn/'
}

# 关注的板块关键词
SECTOR_KEYWORDS = {
    "算力": ["算力", "AI 芯片", "GPU", "人工智能", "数据中心", "服务器"],
    "电力": ["电力", "电网", "清洁能源", "风电", "光伏", "核电"],
    "储能电池": ["储能", "电池", "锂电池", "钠电池", "钙钛矿", "新能源"],
    "机器人": ["机器人", "自动化", "伺服", "减速器", "人形机器人"],
    "商业航天": ["航天", "卫星", "火箭", "商业航天", "低空经济"]
}

# 期货关键词
FUTURE_KEYWORDS = ["锰硅", "硅锰", "焦煤", "焦炭", "钢铁", "黑色系"]

# ==================== 爬虫函数 ====================
def crawl_10jqka_futures():
    """爬取同花顺期货新闻"""
    news_list = []
    try:
        # 同花顺期货频道
        url = "https://futures.10jqka.com.cn/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取新闻列表
            news_items = soup.find_all('a', href=re.compile(r'/futures/\d+\.shtml'))[:10]
            
            for item in news_items:
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                # 检查是否包含期货关键词
                if any(kw in title for kw in FUTURE_KEYWORDS):
                    # 获取详细内容
                    content = fetch_detail_content(f"https:{link}" if link.startswith('//') else link)
                    
                    news_list.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "title": title,
                        "content": content[:200] if content else title,
                        "impact": analyze_impact(title, content),
                        "source": "同花顺"
                    })
        
        time.sleep(1)  # 避免请求过快
    except Exception as e:
        print(f"[同花顺期货] 爬取失败：{e}")
    
    return news_list

def crawl_10jqka_stock():
    """爬取同花顺 A 股新闻"""
    news_list = []
    try:
        # 同花顺财经
        url = "https://www.10jqka.com.cn/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取新闻
            news_items = soup.find_all('a', href=re.compile(r'/\d+\.shtml'))[:20]
            
            for item in news_items:
                title = item.get_text(strip=True)
                
                # 检查是否包含板块关键词
                for sector, keywords in SECTOR_KEYWORDS.items():
                    if any(kw in title for kw in keywords):
                        news_list.append({
                            "time": datetime.now().strftime("%H:%M"),
                            "title": title,
                            "sector": sector,
                            "impact": "✅ 催化" if any(kw in title for kw in ["大会", "论坛", "发布", "政策"]) else "➖ 资讯",
                            "source": "同花顺"
                        })
                        break
        
        time.sleep(1)
    except Exception as e:
        print(f"[同花顺 A 股] 爬取失败：{e}")
    
    return news_list

def crawl_jin10_data():
    """爬取金十数据快讯"""
    news_list = []
    try:
        # 金十数据财经快讯
        url = "https://www.jin10.com/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取快讯
            news_items = soup.find_all('div', class_='jin-international-item')[:15]
            
            for item in news_items:
                title = item.get_text(strip=True)
                
                # 检查相关性
                all_keywords = FUTURE_KEYWORDS + [kw for kws in SECTOR_KEYWORDS.values() for kw in kws]
                if any(kw in title for kw in all_keywords):
                    news_list.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "title": title,
                        "impact": analyze_impact(title, ""),
                        "source": "金十数据"
                    })
        
        time.sleep(1)
    except Exception as e:
        print(f"[金十数据] 爬取失败：{e}")
    
    return news_list

def crawl_eastmoney_futures():
    """爬取东方财富期货新闻"""
    news_list = []
    try:
        url = "https://futures.eastmoney.com/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取新闻
            news_items = soup.find_all('a', href=re.compile(r'/a/\d+\.html'))[:10]
            
            for item in news_items:
                title = item.get_text(strip=True)
                
                if any(kw in title for kw in FUTURE_KEYWORDS):
                    news_list.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "title": title,
                        "impact": analyze_impact(title, ""),
                        "source": "东方财富"
                    })
    except Exception as e:
        print(f"[东方财富期货] 爬取失败：{e}")
    
    return news_list

def fetch_detail_content(url):
    """获取新闻详细内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取正文
        content_div = soup.find('div', class_='content') or soup.find('div', id='content')
        if content_div:
            return content_div.get_text(strip=True)[:300]
    except:
        pass
    return ""

def analyze_impact(title, content):
    """分析新闻影响（简单规则）"""
    positive_words = ["上涨", "大涨", "利好", "突破", "创新高", "增长", "爆发", "催化"]
    negative_words = ["下跌", "大跌", "利空", "暴跌", "下滑", "萎缩", "风险", "警告"]
    
    text = title + " " + content
    
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    
    if pos_count > neg_count:
        return "✅ 利好"
    elif neg_count > pos_count:
        return "⚠️ 利空"
    else:
        return "➖ 中性"

# ==================== 主函数 ====================
def get_all_news():
    """获取所有新闻"""
    print("[爬虫] 开始抓取新闻...")
    
    futures_news = []
    stock_news = {sector: [] for sector in SECTOR_KEYWORDS.keys()}
    
    # 爬取期货新闻
    print("  ├─ 同花顺期货...")
    futures_news.extend(crawl_10jqka_futures())
    
    print("  ├─ 东方财富期货...")
    futures_news.extend(crawl_eastmoney_futures())
    
    print("  ├─ 金十数据...")
    jin10_news = crawl_jin10_data()
    futures_news.extend([n for n in jin10_news if any(kw in n.get('title', '') for kw in FUTURE_KEYWORDS)])
    
    # 爬取 A 股新闻
    print("  ├─ 同花顺 A 股...")
    stock_data = crawl_10jqka_stock()
    for news in stock_data:
        sector = news.get('sector')
        if sector:
            stock_news[sector].append(news)
    
    # 去重
    futures_news = list({n['title']: n for n in futures_news}.values())[:5]
    
    print(f"  └─ 完成！期货{len(futures_news)}条，A 股{sum(len(v) for v in stock_news.values())}条")
    
    return futures_news, stock_news

if __name__ == "__main__":
    futures, stocks = get_all_news()
    print(f"\n期货新闻：{len(futures)}条")
    for n in futures:
        print(f"  - [{n['source']}] {n['title']}")
    
    print(f"\nA 股新闻：")
    for sector, news in stocks.items():
        if news:
            print(f"  {sector}: {len(news)}条")
