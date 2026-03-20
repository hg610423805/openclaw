# -*- coding: utf-8 -*-
"""
上传文件到飞书云文档 - 我的文档库
"""
import requests
import json
import time

# 飞书配置（从 openclaw.json 获取）
APP_ID = "cli_a9307dacd6389bdf"
APP_SECRET = "ovuWWE8GNHzSiDCJAIK9HcwoKgDPBdBy"

# 文件路径
FILE_PATH = r"C:\Users\17699\.openclaw\workspace\OpenClaw_Kindergarten_AI_Business_Plan.pptx"
FILE_NAME = "OpenClaw 幼儿园 AI 数字员工商业计划书.pptx"

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

def upload_file(token, file_path, file_name):
    """上传文件到飞书云空间 - 使用 upload_all 接口"""
    url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 使用 multipart/form-data 上传 - 尝试正确的参数格式
    with open(file_path, "rb") as f:
        file_content = f.read()
    
    # 构建 multipart 请求
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    body = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file_type\"\r\n\r\n"
        f"stream\r\n"
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file\"; filename=\"{file_name}\"\r\n"
        f"Content-Type: application/vnd.openxmlformats-officedocument.presentationml.presentation\r\n\r\n"
    ).encode('utf-8') + file_content + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": f"multipart/form-data; boundary={boundary}"
    }
    
    response = requests.post(url, headers=headers, data=body, timeout=120)
    
    print(f"  -> Upload response status: {response.status_code}")
    print(f"  -> Upload response text: {response.text[:500]}")
    
    try:
        result = response.json()
    except:
        result = {"raw": response.text}
    
    if result.get("code") == 0:
        return result.get("data")
    else:
        raise Exception(f"Upload failed: {result}")

def create_file_to_my_drive(token, file_token, file_name, file_type="pptx"):
    """将上传的文件创建到「我的文档库」"""
    # 首先获取根文件夹 token
    url = "https://open.feishu.cn/open-apis/drive/explorer/v2/root_folder/meta"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    result = response.json()
    
    if result.get("code") != 0:
        # 如果获取根文件夹失败，使用 "0" 作为根文件夹
        root_token = "0"
    else:
        root_token = result.get("data", {}).get("token", "0")
    
    # 创建文件引用到我的云文档
    url = "https://open.feishu.cn/open-apis/drive/v1/files"
    payload = {
        "obj_type": file_type,
        "title": file_name,
        "parent_folder": {
            "folder_token": root_token
        },
        "source": {
            "id": file_token,
            "type": "upload"
        }
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    result = response.json()
    
    if result.get("code") == 0:
        return result.get("data")
    else:
        raise Exception(f"创建文件失败：{result}")

def main():
    print("=" * 60)
    print("Start uploading file to Feishu Drive...")
    print("=" * 60)
    
    # Step 1: Get token
    print("\n[1/4] Getting access token...")
    token = get_tenant_access_token()
    print("[OK] Token obtained")
    
    # Step 2: Upload file
    print(f"\n[2/4] Uploading file: {FILE_NAME}")
    upload_result = upload_file(token, FILE_PATH, FILE_NAME)
    file_token = upload_result.get("file_token")
    print(f"[OK] File uploaded, file_token: {file_token}")
    
    # Step 3: Create to My Drive
    print(f"\n[3/4] Creating file to 'My Drive'...")
    create_result = create_file_to_my_drive(token, file_token, FILE_NAME, "pptx")
    file_url = create_result.get("url", "")
    print("[OK] File created")
    
    # Step 4: Output result
    print("\n" + "=" * 60)
    print("SUCCESS - Upload completed!")
    print("=" * 60)
    print(f"File name: {FILE_NAME}")
    print(f"File URL: {file_url}")
    print("=" * 60)
    
    return file_url

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
