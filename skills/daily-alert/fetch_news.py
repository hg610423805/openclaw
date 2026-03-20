# -*- coding: utf-8 -*-
"""
每日新闻提醒脚本
- 期货锰硅消息（权威源：东方财富、新浪财经、期货日报）
- A 股板块消息（算力、电力、储能、机器人、商业航天）
"""

import requests
import json
from datetime import datetime, timedelta
import re

# 权威新闻源配置
NEWS_SOURCES = {
    'futures': [
        {
            'name': '东方财富期货',
            'url': 'https://api.eastmoney.com/api/news/list',
            'params': {'type': 'qh', 'page': 1, 'page_size': 20}
        },
        {
            'name': '新浪财经期货',
            'url': 'https://finance.sina.com.cn/future/',
            'rss': 'http://finance.sina.com.cn/rss/future.xml'
        }
    ],
    'stocks': [
        {
            'name': '东方财富',
            'url': 'https://api.eastmoney.com/api/news/list',
            'params': {'type': 'a'},
            'keywords': ['算力', '电力', '储能', '电池', '机器人', '商业航天', '人工智能', '芯片']
        },
        {
            'name': '财联社',
            'url': 'https://www.cls.cn/api/roll/list',
            'keywords': ['算力', '电力', '储能', '机器人', '航天']
        }
    ]
}

# 锰硅相关关键词
FUTURES_KEYWORDS = ['锰硅', '硅锰', '合金', '钢铁', '锰矿', '铁合金']

# A 股板块关键词
STOCK_SECTORS = {
    '算力': ['算力', 'AI 芯片', 'GPU', '数据中心', '云计算', '人工智能'],
    '电力': ['电力', '电网', '特高压', '输配电', '发电'],
    '储能电池': ['储能', '电池', '锂电', '钠电', '氢能', '新能源'],
    '机器人': ['机器人', '自动化', '伺服', '减速器', '智能制造'],
    '商业航天': ['航天', '卫星', '火箭', '太空', '宇航']
}

def fetch_eastmoney_news(news_type='qh', limit=20):
    """获取东方财富新闻 - 使用 RSS 源"""
    try:
        # 使用东方财富 RSS
        url = 'http://app.finance.eastmoney.com/rss.aspx'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            # 简单解析 RSS
            import re
            items = re.findall(r'<item>(.*?)</item>', resp.text, re.DOTALL)
            news = []
            for item in items[:limit]:
                title_match = re.search(r'<title>(.*?)</title>', item)
                link_match = re.search(r'<link>(.*?)</link>', item)
                time_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
                if title_match:
                    news.append({
                        'Title': title_match.group(1),
                        'Link': link_match.group(1) if link_match else '',
                        'PublishTime': ''
                    })
            return news
    except Exception as e:
        print(f'东方财富获取失败：{e}')
    return []

def fetch_cls_news(limit=20):
    """获取财联社 - 使用网页抓取"""
    try:
        url = 'https://www.cls.cn/telegraph'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            import re
            # 简单抓取标题
            titles = re.findall(r'<div class="title">.*?</div>', resp.text)
            news = []
            for t in titles[:limit]:
                clean_title = re.sub(r'<.*?>', '', t)
                news.append({'Title': clean_title, 'content': ''})
            return news
    except Exception as e:
        print(f'财联社获取失败：{e}')
    return []

def analyze_impact(title, content):
    """分析消息影响"""
    impact_score = 0
    impact_type = '短期'
    suggestion = '观望'
    
    # 影响程度关键词
    positive_words = ['大涨', '利好', '突破', '创新高', '供不应求', '涨价', '增产']
    negative_words = ['大跌', '利空', '下跌', '亏损', '减产', '库存', '过剩']
    long_term_words = ['政策', '规划', '战略', '长期', '五年', '十年', '改革']
    
    text = title + ' ' + (content if content else '')
    
    # 计算影响分数
    for word in positive_words:
        if word in text:
            impact_score += 1
    for word in negative_words:
        if word in text:
            impact_score -= 1
    
    # 判断长短期
    for word in long_term_words:
        if word in text:
            impact_type = '长期'
            break
    
    # 给出建议
    if impact_score >= 2:
        suggestion = '做多'
    elif impact_score <= -2:
        suggestion = '做空'
    else:
        suggestion = '观望'
    
    # 影响百分比估算
    impact_pct = min(abs(impact_score) * 0.5, 5.0)
    
    return {
        'score': impact_score,
        'type': impact_type,
        'suggestion': suggestion,
        'pct': impact_pct
    }

def filter_futures_news(news_list, hours=24):
    """筛选锰硅相关新闻"""
    filtered = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for news in news_list:
        title = news.get('Title', '') or news.get('title', '')
        content = news.get('Content', '') or news.get('content', '') or ''
        
        # 检查关键词
        has_keyword = any(kw in title or kw in content for kw in FUTURES_KEYWORDS)
        if not has_keyword:
            continue
        
        # 获取时间
        pub_time_str = news.get('PublishTime', '') or news.get('pub_time', '')
        try:
            if pub_time_str:
                pub_time = datetime.fromtimestamp(int(pub_time_str))
            else:
                pub_time = datetime.now()
        except:
            pub_time = datetime.now()
        
        # 检查时间
        if pub_time < cutoff_time:
            continue
        
        # 分析影响
        analysis = analyze_impact(title, content)
        
        filtered.append({
            'title': title,
            'content': content[:200] if content else '',
            'source': '东方财富',
            'time': pub_time.strftime('%Y-%m-%d %H:%M'),
            'analysis': analysis
        })
    
    return filtered

def filter_stock_news(news_list, hours=24):
    """筛选 A 股板块新闻"""
    filtered = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    for news in news_list:
        title = news.get('Title', '') or news.get('title', '')
        content = news.get('Content', '') or news.get('content', '') or ''
        
        # 检查板块关键词
        matched_sectors = []
        text = title + ' ' + content
        for sector, keywords in STOCK_SECTORS.items():
            if any(kw in text for kw in keywords):
                matched_sectors.append(sector)
        
        if not matched_sectors:
            continue
        
        # 获取时间
        pub_time_str = news.get('PublishTime', '') or news.get('pub_time', '')
        try:
            if pub_time_str:
                pub_time = datetime.fromtimestamp(int(pub_time_str))
            else:
                pub_time = datetime.now()
        except:
            pub_time = datetime.now()
        
        if pub_time < cutoff_time:
            continue
        
        # 分析影响
        analysis = analyze_impact(title, content)
        
        filtered.append({
            'title': title,
            'content': content[:200] if content else '',
            'sectors': matched_sectors,
            'source': '财联社',
            'time': pub_time.strftime('%Y-%m-%d %H:%M'),
            'analysis': analysis
        })
    
    return filtered

def generate_report(futures_news, stock_news):
    """生成报告"""
    report = []
    
    # 期货部分
    report.append('📊 期货锰硅日报')
    report.append('=' * 50)
    report.append(f'生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}')
    report.append(f'消息范围：过去 24 小时')
    report.append('')
    
    if futures_news:
        report.append(f'📰 相关新闻：{len(futures_news)} 条')
        report.append('')
        for i, news in enumerate(futures_news[:5], 1):
            report.append(f'{i}. {news["title"]}')
            report.append(f'   时间：{news["time"]} | 来源：{news["source"]}')
            a = news['analysis']
            report.append(f'   影响：{a["type"]} | 幅度：±{a["pct"]:.1f}% | 建议：{a["suggestion"]}')
            report.append('')
    else:
        report.append('⚠️ 过去 24 小时无重大锰硅相关新闻')
        report.append('')
    
    # A 股部分
    report.append('')
    report.append('📈 A 股板块日报')
    report.append('=' * 50)
    report.append('关注板块：算力 | 电力 | 储能电池 | 机器人 | 商业航天')
    report.append('')
    
    if stock_news:
        report.append(f'📰 相关新闻：{len(stock_news)} 条')
        report.append('')
        for i, news in enumerate(stock_news[:10], 1):
            sectors = '、'.join(news['sectors'])
            report.append(f'{i}. [{sectors}] {news["title"]}')
            report.append(f'   时间：{news["time"]} | 来源：{news["source"]}')
            a = news['analysis']
            report.append(f'   影响：{a["type"]} | 幅度：±{a["pct"]:.1f}% | 建议：{a["suggestion"]}')
            report.append('')
    else:
        report.append('⚠️ 过去 24 小时无重大板块相关新闻')
        report.append('')
    
    # 风险提示
    report.append('')
    report.append('⚠️ 风险提示')
    report.append('- 以上分析仅供参考，不构成投资建议')
    report.append('- 期货市场风险较大，请谨慎操作')
    report.append('- 消息面需结合技术面综合判断')
    
    return '\n'.join(report)

def main():
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print('[INFO] 开始获取新闻...')
    
    # 获取期货新闻
    print('[INFO] 获取期货新闻...')
    em_news = fetch_eastmoney_news('qh', 50)
    futures_news = filter_futures_news(em_news, hours=24)
    print(f'   找到 {len(futures_news)} 条锰硅相关新闻')
    
    # 获取 A 股新闻
    print('[INFO] 获取 A 股新闻...')
    cls_news = fetch_cls_news(50)
    stock_news = filter_stock_news(cls_news, hours=24)
    print(f'   找到 {len(stock_news)} 条板块相关新闻')
    
    # 生成报告
    report = generate_report(futures_news, stock_news)
    
    # 保存报告
    with open('C:/Users/17699/.openclaw/workspace/skills/daily-alert/daily_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print('[OK] 报告已生成：daily_report.txt')
    print('')
    print(report)
    
    return report

if __name__ == '__main__':
    main()
