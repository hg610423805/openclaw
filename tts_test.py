# -*- coding: utf-8 -*-
"""生成语音测试"""
from gtts import gTTS
import os

text = "猴哥～咕噜在这里哦！晚安啦，做个好梦～"
tts = gTTS(text=text, lang='zh-CN')
output_path = "C:\\Users\\17699\\.openclaw\\workspace\\gulu_goodnight.mp3"
tts.save(output_path)
print(f"✅ 语音文件已生成：{output_path}")
print(f"文件大小：{os.path.getsize(output_path)} bytes")
