# -*- coding: utf-8 -*-
"""
发送今日新闻推送到飞书
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
print(f'Token OK: {token[:20]}...')

# Send message
url = 'https://open.feishu.cn/open-apis/im/v1/messages'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

content = {
    'config': {
        'wide_screen_mode': True
    },
    'header': {
        'title': {'tag': 'plain_text', 'content': '🐱 咕噜的每日推送 (补发)'},
        'template': 'red'
    },
    'elements': [
        {
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': '**📅 日期：** 2026 年 3 月 23 日 周一\n**⏰ 推送时间：** 08:27 (补发)\n\n**🔥 核心要点：**\n• 焦煤夜盘大涨 9%，锰硅成本端强支撑\n• 中信证券：煤价进入上涨通道\n• 储能电池本周密集催化 (3/25-27)\n• 华为发布会今日 14:30'
            }
        },
        {
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': '**🛢️ 期货锰硅建议：逢低做多**\n**📈 A 股重点：储能电池⭐⭐⭐⭐⭐**'
            }
        },
        {
            'tag': 'hr'
        },
        {
            'tag': 'note',
            'elements': [
                {'tag': 'plain_text', 'content': '💡 完整报告已保存，下次开始自动 8 点推送'}
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
else:
    print(f'FAILED: {result}')
