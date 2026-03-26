# -*- coding: utf-8 -*-
"""
飞书测试消息发送
"""
import requests
import json

# 飞书凭证
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"

# 用户 open_id（从配置中读取）
USER_OPEN_ID = "ou_2a456545aa7be2a12881fe2a3f21198e"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    response = requests.post(url, json=payload)
    return response.json().get("tenant_access_token")

def send_message(token, receive_id):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 测试消息内容
    content = {
        "text": """【飞书接入测试 - 咕噜】

爸爸好！我是咕噜，你的 AI 助手。

飞书已成功接入，现在我可以：
1. 发送交易信号提醒
2. 推送回测报告
3. 定期发送市场动态

这是测试消息，收到请回复！

---
时间：2026-03-23 23:15
策略：均线+KDJ"""
    }
    
    payload = json.dumps({
        "receive_id_type": "open_id",
        "receive_id": receive_id,
        "msg_type": "text",
        "content": content
    })
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    print("="*60)
    print("飞书测试消息发送")
    print("="*60)
    print(f"目标用户：{USER_OPEN_ID}")
    
    token = get_tenant_token()
    if not token:
        print("[ERROR] 获取 token 失败")
        exit(1)
    
    print(f"[OK] Token 获取成功")
    
    result = send_message(token, USER_OPEN_ID)
    
    print(f"\n发送结果：{json.dumps(result, ensure_ascii=False)}")
    
    if result.get("code") == 0 or "success" in str(result).lower():
        print("\n[OK] 消息发送成功！")
        print("请检查飞书是否收到消息")
    else:
        print(f"\n[ERROR] 消息发送失败")
        print(f"错误信息：{result.get('msg', '未知错误')}")
        print("\n可能的原因：")
        print("1. open_id 不正确")
        print("2. 机器人未获得发送消息权限")
        print("3. 用户未关注机器人")
