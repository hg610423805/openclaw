# -*- coding: utf-8 -*-
"""
百度网盘直接上传脚本 - 使用 requests 库
"""
import requests
import json
import hashlib
import time

# 配置
APP_KEY = "q8WE4EpCsau1oS0MplgMKNBn"
APP_SECRET = "oklMClujzlgDIfqCI1SvE2Gf"
AUTH_CODE = "4c2c39e75c6b03eb914e76d534a78233"

# 文件路径
LOCAL_FILE = r"C:\Users\17699\.openclaw\workspace\OpenClaw_Kindergarten_AI_Business_Plan.pptx"
REMOTE_PATH = "/apps/商业计划书/OpenClaw 幼儿园 AI 数字员工商业计划书.pptx"

def get_access_token():
    """用授权码获取 access_token"""
    print("[1/5] 获取 access_token...")
    
    url = "https://openapi.baidu.com/oauth/2.0/token"
    params = {
        "grant_type": "authorization_code",
        "code": AUTH_CODE,
        "client_id": APP_KEY,
        "client_secret": APP_SECRET,
        "redirect_uri": "oob"
    }
    
    response = requests.get(url, params=params, timeout=30)
    result = response.json()
    
    if "access_token" in result:
        print(f"    OK - Token 获取成功")
        return result["access_token"]
    else:
        print(f"    ERROR - {result}")
        raise Exception(f"获取 token 失败：{result}")

def get_remote_file_id(token, remote_path):
    """检查远程文件是否已存在"""
    print("[2/5] 检查远程文件...")
    
    url = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
    params = {
        "method": "meta",
        "access_token": token,
        "path": json.dumps([remote_path])
    }
    
    response = requests.get(url, params=params, timeout=30)
    result = response.json()
    
    if "list" in result and len(result["list"]) > 0:
        file_id = result["list"][0]["fs_id"]
        print(f"    文件已存在，fs_id: {file_id}")
        return file_id
    else:
        print(f"    文件不存在，需要上传")
        return None

def upload_file(token, local_path, remote_path):
    """上传文件到百度网盘"""
    print(f"[3/5] 上传文件到百度网盘...")
    print(f"    本地：{local_path}")
    print(f"    远程：{remote_path}")
    
    # 读取文件
    with open(local_path, 'rb') as f:
        file_content = f.read()
    
    file_size = len(file_content)
    print(f"    文件大小：{file_size / 1024:.1f} KB")
    
    # 小文件直接上传（小于 4MB）
    url = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
    params = {
        "method": "upload",
        "access_token": token,
        "path": remote_path,
        "ondemand": "overwrite"
    }
    
    files = {
        "file": ('OpenClaw_Kindergarten_AI_Business_Plan.pptx', file_content, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')
    }
    
    print(f"    开始上传...")
    response = requests.post(url, params=params, files=files, timeout=120)
    result = response.json()
    
    print(f"    响应：{result}")
    
    if "fs_id" in result or "size" in result:
        print(f"    OK - 上传成功")
        return True
    else:
        print(f"    ERROR - 上传失败")
        return False

def verify_upload(token, remote_path):
    """验证上传结果"""
    print("[4/5] 验证上传结果...")
    
    url = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
    params = {
        "method": "meta",
        "access_token": token,
        "path": json.dumps([remote_path])
    }
    
    response = requests.get(url, params=params, timeout=30)
    result = response.json()
    
    if "list" in result and len(result["list"]) > 0:
        file_info = result["list"][0]
        print(f"    OK - 文件验证成功")
        print(f"    文件名：{file_info.get('server_filename', 'N/A')}")
        print(f"    大小：{file_info.get('size', 0) / 1024:.1f} KB")
        print(f"    路径：{file_info.get('path', 'N/A')}")
        return True
    else:
        print(f"    ERROR - 文件验证失败")
        return False

def main():
    print("=" * 60)
    print("百度网盘上传工具")
    print("=" * 60)
    
    try:
        # Step 1: 获取 token
        token = get_access_token()
        
        # Step 2: 检查远程文件
        remote_file_id = get_remote_file_id(token, REMOTE_PATH)
        
        # Step 3: 上传文件
        success = upload_file(token, LOCAL_FILE, REMOTE_PATH)
        
        if not success:
            raise Exception("上传失败")
        
        # Step 4: 验证上传
        verify_upload(token, REMOTE_PATH)
        
        # Step 5: 输出结果
        print("\n" + "=" * 60)
        print("✅ 上传完成！")
        print("=" * 60)
        print(f"文件路径：{REMOTE_PATH}")
        print("请在百度网盘 App 或网页版查看文件")
        print("https://pan.baidu.com/")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ 错误：{e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
