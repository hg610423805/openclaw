# -*- coding: utf-8 -*-
"""
飞书消息和文档上传 - 均线 KDJ 策略回测报告
"""
import requests
import json
from datetime import datetime

# 飞书凭证
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"

def get_tenant_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    result = response.json()
    return result.get("tenant_access_token")

def send_message(token, receive_id, msg_type="text", content=None):
    """发送消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id_type": "open_id",
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": content if content else json.dumps({"text": "测试消息"})
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def create_doc(token, title, content, folder_token=None):
    """创建飞书文档"""
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "title": title,
        "content": content
    }
    if folder_token:
        payload["folder_token"] = folder_token
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    print("="*60)
    print("飞书回测报告推送")
    print("="*60)
    
    # 获取 token
    token = get_tenant_token()
    if not token:
        print("[ERROR] 获取 token 失败")
        exit(1)
    
    print(f"[OK] Token 获取成功")
    
    # 回测报告内容
    report_md = """# 均线+KDJ 策略回测报告

## 回测信息
- **策略名称**: 均线+KDJ 趋势跟踪策略
- **回测区间**: 2025-09-24 至 2026-03-23 (180 天)
- **初始资金**: 100,000 元
- **仓位比例**: 50%
- **每日最多交易**: 3 笔

## 策略规则

### 监控级别
- **监控 K 线**: 30 分钟级别
- **交易 K 线**: 5 分钟级别

### 核心指标
- EXPMA13 / EXPMA26
- KDJ 的 J 值

### 入场条件

#### 做多 (30 分钟 J<20 且 EXPMA13>EXPMA26)
1. **方式 1**: 5 分钟 J<20 + EXPMA13>EXPMA26 + K 线低点抬高
2. **方式 2**: 5 分钟金叉入场

#### 做空 (30 分钟 J>80 且 EXPMA13<EXPMA26)
1. **方式 1**: 5 分钟 J>80 + EXPMA13<EXPMA26 + K 线高点降低
2. **方式 2**: 5 分钟死叉入场

### 出场规则
- **止损**: 前 K 线高低点 ±1tick 或 分型高低点
- **止盈**: 5 分钟 EXPMA 反向交叉
- **移动止损**: 底分型/顶分型上移/下移

## 回测结果

| 品种 | 交易笔数 | 总盈亏 | 胜率 | 最终资金 |
|------|----------|--------|------|----------|
| 锰硅 (SM) | 0 笔 | 0.00 元 | - | 100,000 元 |
| 玻璃 (FG) | 1 笔 | -245.68 元 | 0.00% | 99,754 元 |
| 玉米 (C) | 1 笔 | -105.21 元 | 0.00% | 99,895 元 |

## 问题分析

1. **交易信号少**: 180 天仅 2 笔交易，说明入场条件过于严格
2. **胜率偏低**: 2 笔交易全部止损/止盈亏损
3. **锰硅无信号**: 可能 30 分钟级别 J 值很少触及<20 或>80

## 优化建议

1. **放宽 J 值阈值**: J<20 改为 J<30，J>80 改为 J>70
2. **增加入场方式**: 考虑增加其他确认信号
3. **优化止损**: 当前止损可能过紧
4. **延长回测**: 建议回测 1-3 年数据

---
*报告生成时间: {time}*
*策略版本：v1.0 - 完整规则版*
""".format(time=datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # 1. 创建文档
    print("\n[1] 创建飞书文档...")
    doc_result = create_doc(token, "均线+KDJ 策略回测报告 - 20260323", report_md)
    print(f"文档创建结果：{json.dumps(doc_result, ensure_ascii=False)}")
    
    if doc_result.get("code") == 0 or "document" in doc_result:
        doc_token = doc_result.get("document", {}).get("document_id", "未知")
        doc_url = f"https://www.feishu.cn/docx/{doc_token}"
        print(f"[OK] 文档创建成功！")
        print(f"文档链接：{doc_url}")
        
        # 2. 发送消息通知
        print("\n[2] 发送飞书消息通知...")
        msg_content = json.dumps({
            "text": f"""【均线+KDJ 策略回测报告】

回测区间：2025-09-24 至 2026-03-23
初始资金：100,000 元

回测结果:
- 锰硅：0 笔交易，盈亏 0 元
- 玻璃：1 笔交易，亏损 -245.68 元
- 玉米：1 笔交易，亏损 -105.21 元

详细报告：{doc_url}

问题分析：
1. 交易信号过少 (180 天仅 2 笔)
2. 入场条件可能过于严格
3. 建议优化 J 值阈值和止损策略

请查看完整报告了解详细分析。"""
        })
        
        # 注意：需要用户的 open_id 才能发送消息
        print(f"[提示] 消息内容已准备，需要用户 open_id 才能发送")
        print(f"消息内容预览：{msg_content[:200]}...")
    else:
        print(f"[ERROR] 文档创建失败：{doc_result}")
    
    print("\n" + "="*60)
    print("飞书报告推送完成")
    print("="*60)
