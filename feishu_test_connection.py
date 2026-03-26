# -*- coding: utf-8 -*-
"""
飞书连接测试脚本
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
    print(f"获取 tenant_access_token: {json.dumps(result, ensure_ascii=False)}")
    return result.get("tenant_access_token")

# 测试获取机器人信息
def get_bot_info(token):
    url = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    result = response.json()
    print(f"机器人信息：{json.dumps(result, ensure_ascii=False)}")
    return result

if __name__ == "__main__":
    print("="*60)
    print("飞书连接测试")
    print("="*60)
    print(f"App ID: {APP_ID}")
    print(f"App Secret: {APP_SECRET[:10]}...")
    print("="*60)
    
    token = get_tenant_token()
    if token:
        print(f"\n✅ 飞书连接成功！")
        print(f"Tenant Token: {token[:20]}...")
    else:
        print(f"\n❌ 飞书连接失败，请检查凭证是否正确")
