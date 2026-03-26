# -*- coding: utf-8 -*-
"""
飞书消息发送测试
"""
import requests
import json

# 飞书凭证
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"

# 获取 tenant_access_token
def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    result = response.json()
    return result.get("tenant_access_token")

# 发送消息
def send_message(token, chat_id, content):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id_type": "chat_id",
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()
    return result

if __name__ == "__main__":
    token = get_tenant_token()
    if token:
        print(f"[OK] 飞书连接成功")
        print(f"Token: {token[:30]}...")
        print(f"\n现在可以发送消息到飞书聊天了！")
    else:
        print(f"[ERROR] 飞书连接失败")
