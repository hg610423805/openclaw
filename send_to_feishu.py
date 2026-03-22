# -*- coding: utf-8 -*-
"""
发送财经日报链接到飞书
"""
import requests
import json

# 飞书配置
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"
USER_OPEN_ID = "ou_2a456545aa7be2a12881fe2a3f21198e"

def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload, timeout=30)
    result = response.json()
    if result.get("code") == 0:
        return result.get("tenant_access_token")
    else:
        raise Exception(f"获取 token 失败：{result}")

def create_doc(token, title, content):
    """创建飞书云文档"""
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title
    }
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    result = response.json()
    if result.get("code") == 0:
        return result.get("data")
    else:
        raise Exception(f"创建文档失败：{result}")

def send_message(token, user_id, title, links):
    """发送飞书消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 构建卡片消息
    content = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "title": {
                "tag": "plain_text",
                "content": "🐱 咕噜财经日报已生成"
            },
            "template": "blue"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": f"**📅 日期：** 2026 年 3 月 21 日\n**⏰ 生成时间：** 08:20\n\n**📊 今日内容：**\n• 霍尔木兹局势、算力板块、储能电池\n• 期货/A 股推荐标的"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "lark_md",
                            "content": "📰 查看财经日报"
                        },
                        "url": links["daily"],
                        "type": "default",
                        "style": "blue"
                    },
                    {
                        "tag": "button",
                        "text": {
                            "tag": "lark_md",
                            "content": "📊 回测报告"
                        },
                        "url": links["backtest"],
                        "type": "default",
                        "style": "blue"
                    }
                ]
            },
            {
                "tag": "hr"
            },
            {
                "tag": "note",
                "elements": [
                    {
                        "tag": "plain_text",
                        "content": "💡 提示：GitHub Pages 更新需要 1-5 分钟生效"
                    }
                ]
            }
        ]
    }
    
    payload = {
        "receive_id": user_id,
        "msg_type": "interactive",
        "content": json.dumps(content)
    }
    
    # 查询参数
    params = {"receive_id_type": "open_id"}
    
    response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
    result = response.json()
    return result

def main():
    print("=" * 60)
    print("发送财经日报到飞书...")
    print("=" * 60)
    
    # Step 1: Get token
    print("\n[1/3] 获取访问令牌...")
    token = get_tenant_access_token()
    print(f"[OK] Token: {token[:20]}...")
    
    # Step 2: Send message
    print("\n[2/3] 发送消息...")
    links = {
        "daily": "https://hg610423805.github.io/openclaw/daily-report-2026-03-22.html",
        "backtest": "https://hg610423805.github.io/openclaw/reports/report-期货回测分析 -2026-03-20-2303.html"
    }
    result = send_message(token, USER_OPEN_ID, "财经日报", links)
    
    if result.get("code") == 0:
        print("[OK] 消息发送成功！")
        print(f"Message ID: {result.get('data', {}).get('message_id')}")
    else:
        print(f"[ERROR] 发送失败：{result}")
    
    # Step 3: Create doc
    print("\n[3/3] 创建汇总文档...")
    doc_content = """# 📰 咕噜财经日报 - 报告汇总

## 📊 今日报告（2026-03-21）

- **总索引页**：https://hg610423805.github.io/openclaw/
- **财经日报**：https://hg610423805.github.io/openclaw/reports/daily-report-2026-03-21.html
- **回测报告**：https://hg610423805.github.io/openclaw/reports/report-期货回测分析 -2026-03-20-2303.html

---
*生成：咕噜 AI 🐱*
"""
    doc_result = create_doc(token, "📰 咕噜财经日报汇总", doc_content)
    
    if doc_result:
        print(f"[OK] 文档创建成功！")
        print(f"文档链接：https://www.feishu.cn/drive/docx/{doc_result.get('document_id')}")
    else:
        print(f"[INFO] 文档创建跳过")
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
