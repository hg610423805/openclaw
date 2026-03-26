# -*- coding: utf-8 -*-
"""
直接发送财经日报内容到飞书（云文档格式）
"""
import requests
import json
from datetime import datetime

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

def update_doc_content(token, document_id, content):
    """更新文档内容"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 解析 markdown 为飞书格式
    blocks = []
    lines = content.split('\n')
    current_list = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 标题
        if line.startswith('# '):
            blocks.append({
                "block_type": "heading1",
                "heading1": {
                    "elements": [{"text_run": {"text": line[2:]}}]
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "block_type": "heading2",
                "heading2": {
                    "elements": [{"text_run": {"text": line[3:]}}]
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "block_type": "heading3",
                "heading3": {
                    "elements": [{"text_run": {"text": line[4:]}}]
                }
            })
        # 引用
        elif line.startswith('> '):
            blocks.append({
                "block_type": "callout",
                "callout": {
                    "elements": [{"text_run": {"text": line[2:]}}]
                }
            })
        # 表格行（简单处理）
        elif line.startswith('|') and line.endswith('|'):
            cells = [c.strip() for c in line.split('|')[1:-1]]
            if cells and cells[0] not in ['---', '===']:
                blocks.append({
                    "block_type": "table",
                    "table": {
                        "rows": [{
                            "cells": [{"text": c}] for c in cells
                        }]
                    }
                })
        # 普通文本
        else:
            blocks.append({
                "block_type": "text",
                "text": {
                    "elements": [{"text_run": {"text": line}}]
                }
            })
    
    payload = {
        "children": blocks
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    result = response.json()
    return result

def send_message(token, user_id, doc_link):
    """发送飞书消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
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
                    "content": f"**📅 日期：** 2026 年 3 月 22 日\n**⏰ 更新：** 09:38 实时数据\n\n**📊 今日重点：**\n• 期货锰硅：偏空震荡，逢高做空\n• 算力板块：⭐⭐⭐⭐⭐ 重点推荐\n• 储能电池：⭐⭐⭐⭐⭐ 重点推荐"
                }
            },
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {
                            "tag": "lark_md",
                            "content": "📄 查看云文档报告"
                        },
                        "url": doc_link,
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
                        "content": "💡 云文档已生成，点击按钮即可查看完整报告"
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
    
    params = {"receive_id_type": "open_id"}
    
    response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
    result = response.json()
    return result

def main():
    print("=" * 60)
    print("发送财经日报云文档到飞书...")
    print("=" * 60)
    
    # Step 1: Get token
    print("\n[1/3] 获取访问令牌...")
    token = get_tenant_access_token()
    print(f"[OK] Token: {token[:20]}...")
    
    # Step 2: Read markdown content
    print("\n[2/3] 读取报告内容...")
    with open("daily-report-2026-03-22-content.md", "r", encoding="utf-8") as f:
        content = f.read()
    print(f"[OK] 内容长度：{len(content)} 字符")
    
    # Step 3: Create doc
    print("\n[3/3] 创建云文档...")
    title = f"📰 财经日报 - 2026-03-22"
    doc_result = create_doc(token, title, content)
    
    if doc_result:
        doc_id = doc_result.get("document_id")
        doc_link = f"https://www.feishu.cn/drive/docx/{doc_id}"
        print(f"[OK] 云文档创建成功！")
        print(f"链接：{doc_link}")
        
        # Send message
        print("\n[通知] 发送消息...")
        msg_result = send_message(token, USER_OPEN_ID, doc_link)
        
        if msg_result.get("code") == 0:
            print(f"[OK] 消息发送成功！")
            print(f"Message ID: {msg_result.get('data', {}).get('message_id')}")
        else:
            print(f"[ERROR] 消息发送失败：{msg_result}")
    else:
        print(f"[ERROR] 文档创建失败：{doc_result}")
    
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
