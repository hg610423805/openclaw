# -*- coding: utf-8 -*-
"""
下载高质量图片并制作超精美商业计划书 PPT
"""
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# 图片保存目录
IMG_DIR = r"C:\Users\17699\.openclaw\workspace\images"
os.makedirs(IMG_DIR, exist_ok=True)

# 免费高质量图片 URLs (Pexels/Unsplash)
IMAGE_URLS = {
    "title_bg": "https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "business": "https://images.pexels.com/photos/3760067/pexels-photo-3760067.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "tech": "https://images.pexels.com/photos/1181242/pexels-photo-1181242.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "office": "https://images.pexels.com/photos/3196359/pexels-photo-3196359.jpeg?auto=compress&cs=tinysrgb&w=1920",
    "gradient_blue": "https://images.pexels.com/photos/19589445/pexels-photo-19589445/free-photo-view-of-buildings-in-city.jpeg?auto=compress&cs=tinysrgb&w=1920",
}

def download_image(url, filename):
    """下载图片"""
    print(f"Downloading {filename}...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            filepath = os.path.join(IMG_DIR, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            print(f"  -> Saved: {filepath}")
            return filepath
    except Exception as e:
        print(f"  -> Error: {e}")
    return None

# 下载图片
print("=" * 60)
print("Downloading high-quality images...")
print("=" * 60)
for name, url in IMAGE_URLS.items():
    download_image(url, f"{name}.jpg")

# 创建渐变背景图
print("\nCreating gradient backgrounds...")

def create_gradient_image(width, height, color1, color2, filename):
    """创建渐变背景图"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    # 简单的上下渐变
    for y in range(height):
        ratio = y / height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    filepath = os.path.join(IMG_DIR, filename)
    img.save(filepath)
    print(f"  -> Created: {filepath}")
    return filepath

# 创建豪华渐变背景
create_gradient_image(1920, 1080, (26, 43, 74), (0, 90, 190), "gradient_dark_blue.jpg")
create_gradient_image(1920, 1080, (248, 250, 252), (255, 255, 255), "gradient_light.jpg")
create_gradient_image(1920, 1080, (212, 175, 55), (255, 215, 0), "gradient_gold.jpg")

print("\nAll images ready!")
print(f"Image directory: {IMG_DIR}")