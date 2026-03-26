# -*- coding: utf-8 -*-
"""
发送回测报告链接到飞书
"""
import requests
import json

APP_ID = 'cli_a9307dacd6389bdf'
APP_SECRET = 'ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy'
USER_OPEN_ID = 'ou_2a456545aa7be2a12881fe2a3f21198e'

url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
payload = {'app_id': APP_ID, 'app_secret': APP_SECRET}
response = requests.post(url, json=payload, timeout=30)
result = response.json()
if result.get('code') != 0:
    print(f'Token failed: {result}')
    exit(1)
token = result.get('tenant_access_token')
print('Token OK')

html_url = 'https://hg610423805.github.io/openclaw/backtest-report-20260323.html'

url = 'https://open.feishu.cn/open-apis/im/v1/messages'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

content = {
    'config': {'wide_screen_mode': True},
    'header': {
        'title': {'tag': 'plain_text', 'content': '📊 回测报告已生成'},
        'template': 'blue'
    },
    'elements': [
        {
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': '**🎯 期货回测分析报告**\n**📅 周期**: 2025-03-19 至 2026-03-19\n\n**💰 核心数据**:\n• 总盈亏：+91,620 元 (+91.62%)\n• 总交易：363 笔\n• 胜率：34.7%\n\n**🏆 品种排名**:\n1. 锰硅：+39,400 元\n2. 硅铁：+29,050 元\n3. 鸡蛋：+16,230 元'
            }
        },
        {
            'tag': 'action',
            'actions': [
                {
                    'tag': 'button',
                    'text': {'tag': 'lark_md', 'content': '📊 查看完整报告'},
                    'url': html_url,
                    'type': 'primary',
                    'style': 'blue'
                }
            ]
        },
        {
            'tag': 'hr'
        },
        {
            'tag': 'note',
            'elements': [
                {'tag': 'plain_text', 'content': '💡 GitHub Pages 更新需要 1-5 分钟，如打不开请稍后刷新'}
            ]
        }
    ]
}

payload = {
    'receive_id': USER_OPEN_ID,
    'msg_type': 'interactive',
    'content': json.dumps(content)
}

params = {'receive_id_type': 'open_id'}
response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
result = response.json()

if result.get('code') == 0:
    print('SUCCESS: Message sent!')
    print(f"Message ID: {result.get('data', {}).get('message_id')}")
    print(f"HTML URL: {html_url}")
else:
    print(f'FAILED: {result}')
