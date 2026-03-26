# -*- coding: utf-8 -*-
"""
通过授权码获取用户 open_id
需要用户先在飞书中授权机器人
"""
import requests
import json

# 飞书凭证
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"

def get_user_token(auth_code):
    """通过授权码获取 user_access_token"""
    url = "https://open.feishu.cn/open-apis/authen/v1/access_token"
    headers = {"Content-Type": "application/json"}
    payload = {
        "grant_type": "authorization_code",
        "code": auth_code
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_user_info(user_token):
    """获取用户信息（包含 open_id）"""
    url = "https://open.feishu.cn/open-apis/authen/v1/user_info"
    headers = {
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    print("="*60)
    print("获取飞书 Open ID")
    print("="*60)
    print("\n请按以下步骤操作：")
    print("1. 在飞书中打开机器人聊天窗口")
    print("2. 发送任意消息给机器人")
    print("3. 机器人会回复一个授权链接")
    print("4. 点击链接授权后，会看到一个 code 参数")
    print("5. 把 code 值复制给我")
    print("\n或者：")
    print("直接在飞书搜索 '咕噜' 机器人，发送消息即可")
    print("="*60)
