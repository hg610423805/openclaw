# -*- coding: utf-8 -*-
"""
发送 HTML 报告链接到飞书
"""
import requests
import json

APP_ID = 'cli_a9307dacd6389bdf'
APP_SECRET = 'ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy'
USER_OPEN_ID = 'ou_2a456545aa7be2a12881fe2a3f21198e'

# Get token
url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
payload = {'app_id': APP_ID, 'app_secret': APP_SECRET}
response = requests.post(url, json=payload, timeout=30)
result = response.json()
if result.get('code') != 0:
    print(f'Token failed: {result}')
    exit(1)
token = result.get('tenant_access_token')
print(f'Token OK')

# Send message
url = 'https://open.feishu.cn/open-apis/im/v1/messages'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

html_url = 'https://hg610423805.github.io/openclaw/daily-report-2026-03-23.html'

content = {
    'config': {
        'wide_screen_mode': True
    },
    'header': {
        'title': {'tag': 'plain_text', 'content': '🐱 咕噜的 HTML 报告链接'},
        'template': 'green'
    },
    'elements': [
        {
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': '**📰 财经日报 HTML 已生成**\n**📅 日期：** 2026 年 3 月 23 日 周一\n\n**🔥 核心内容：**\n• 焦煤大涨 9% → 锰硅成本端强支撑\n• 储能电池本周密集催化\n• 华为发布会今日 14:30'
            }
        },
        {
            'tag': 'action',
            'actions': [
                {
                    'tag': 'button',
                    'text': {
                        'tag': 'lark_md',
                        'content': '📊 查看 HTML 报告'
                    },
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
                {'tag': 'plain_text', 'content': '💡 GitHub Pages 更新需要 1-5 分钟生效，如打不开请稍后刷新'}
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
