# -*- coding: utf-8 -*-
"""
百度网盘上传脚本
"""
import os
import sys
import json

# 设置环境变量
os.environ['BYPY_DIR'] = r'C:\Users\17699\.bypy'

# 授权码
AUTH_CODE = "4c2c39e75c6b03eb914e76d534a78233"

# 文件路径
FILE_PATH = r"C:\Users\17699\.openclaw\workspace\OpenClaw_Kindergarten_AI_Business_Plan.pptx"
REMOTE_PATH = "/apps/商业计划书/OpenClaw 幼儿园 AI 数字员工商业计划书.pptx"

print("=" * 60)
print("开始配置百度网盘...")
print("=" * 60)

# Step 1: 创建 bypy 配置目录
bypy_dir = os.environ['BYPY_DIR']
os.makedirs(bypy_dir, exist_ok=True)
print(f"[1/4] 配置目录：{bypy_dir}")

# Step 2: 写入授权码
auth_file = os.path.join(bypy_dir, 'bypy.json')
auth_data = {
    'access_token': '',
    'refresh_token': AUTH_CODE,
    'expires_at': 9999999999  # 永久有效（临时处理）
}

with open(auth_file, 'w', encoding='utf-8') as f:
    json.dump(auth_data, f, indent=2)

print(f"[2/4] 授权文件已写入：{auth_file}")

# Step 3: 使用 bypy 上传
print(f"\n[3/4] 开始上传文件...")
print(f"本地文件：{FILE_PATH}")
print(f"远程路径：{REMOTE_PATH}")

import subprocess
result = subprocess.run(
    ['bypy', 'upload', FILE_PATH, REMOTE_PATH],
    capture_output=True,
    text=True,
    timeout=120
)

print(result.stdout)
if result.stderr:
    print("错误信息:", result.stderr)

if result.returncode == 0:
    print("\n" + "=" * 60)
    print("✅ 上传成功！")
    print("=" * 60)
    print(f"文件位置：百度网盘/{REMOTE_PATH}")
    print("=" * 60)
else:
    print("\n" + "=" * 60)
    print("❌ 上传失败")
    print("=" * 60)
    sys.exit(1)
