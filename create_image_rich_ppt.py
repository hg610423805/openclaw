# -*- coding: utf-8 -*-
"""
超丰富图片版商业计划书 PPT - 大量高质量图片 + 数据可视化
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE
from pptx.chart.data import CategoryChartData

# 创建演示文稿
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 图片目录
IMG_DIR = r"C:\Users\17699\.openclaw\workspace\images"

# 配色
COLORS = {
    'primary': RGBColor(26, 43, 74),
    'secondary': RGBColor(0, 90, 190),
    'accent': RGBColor(212, 175, 55),
    'accent_light': RGBColor(255, 215, 0),
    'white': RGBColor(255, 255, 255),
    'dark': RGBColor(45, 52, 69),
    'light': RGBColor(248, 250, 252),
    'overlay': RGBColor(0, 0, 0),
    'success': RGBColor(39, 174, 96),
    'warning': RGBColor(230, 126, 34),
}

import os

def add_picture_background(slide, image_name, overlay_alpha=0.5):
    """添加图片背景"""
    img_path = os.path.join(IMG_DIR, image_name)
    if not os.path.exists(img_path):
        # 如果图片不存在，创建纯色背景
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLORS['primary']
        bg.line.fill.background()
        return
    
    pic = slide.shapes.add_picture(img_path, Inches(0), Inches(0), width=prs.slide_width)
    if pic.height < prs.slide_height:
        pic.top = int((prs.slide_height - pic.height) / 2)
    
    # 半透明遮罩
    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = COLORS['overlay']
    overlay.fill.transparency = overlay_alpha
    overlay.line.fill.background()

def add_header(slide, title):
    """添加顶部标题栏"""
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.3))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.fill.transparency = 0.85
    header.line.fill.background()
    
    gold = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.25), prs.slide_width, Inches(0.05))
    gold.fill.solid()
    gold.fill.fore_color.rgb = COLORS['accent']
    gold.line.fill.background()
    
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(34)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']

def add_content_card(slide, x, y, w, h, title, content, icon=""):
    """添加内容卡片（带图片背景）"""
    # 卡片背景
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    card.fill.solid()
    card.fill.fore_color.rgb = COLORS['white']
    card.fill.transparency = 0.88
    card.line.color.rgb = COLORS['accent']
    card.line.width = Pt(2)
    
    # 图标
    if icon:
        icon_box = slide.shapes.add_textbox(Inches(x+0.2), Inches(y+0.2), Inches(0.6), Inches(0.6))
        tf = icon_box.text_frame
        p = tf.paragraphs[0]
        p.text = icon
        p.font.size = Pt(32)
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(x+0.2), Inches(y+0.8), Inches(w-0.4), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']
    
    # 内容
    content_box = slide.shapes.add_textbox(Inches(x+0.2), Inches(y+1.4), Inches(w-0.4), Inches(h-1.6))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(content):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(13)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(6)

def add_stat_card(slide, x, y, number, label, color):
    """添加统计数据卡片"""
    # 背景卡片
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(3), Inches(2))
    card.fill.solid()
    card.fill.fore_color.rgb = color
    card.fill.transparency = 0.85
    card.line.color.rgb = COLORS['accent']
    card.line.width = Pt(2)
    
    # 数字
    num_box = slide.shapes.add_textbox(Inches(x), Inches(y+0.3), Inches(3), Inches(1))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = number
    p.font.size = Pt(48)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 标签
    label_box = slide.shapes.add_textbox(Inches(x), Inches(y+1.3), Inches(3), Inches(0.6))
    tf = label_box.text_frame
    p = tf.paragraphs[0]
    p.text = label
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

def add_timeline_visual(slide, phases):
    """添加可视化时间线"""
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    
    for i, phase in enumerate(phases):
        x = 0.8 + i * 4.5
        y = 2.5
        
        # 圆点
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.8), Inches(0.8))
        circle.fill.solid()
        circle.fill.fore_color.rgb = colors[i]
        circle.line.color.rgb = COLORS['accent']
        circle.line.width = Pt(3)
        
        # 连接线
        if i < len(phases) - 1:
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x+0.8), Inches(y+0.35), Inches(3.7), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS['accent']
            line.line.fill.background()
        
        # 阶段标题
        title = slide.shapes.add_textbox(Inches(x), Inches(y+1), Inches(3.5), Inches(0.5))
        tf = title.text_frame
        p = tf.paragraphs[0]
        p.text = phase['title']
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = colors[i]
        p.alignment = PP_ALIGN.CENTER
        
        # 阶段内容
        content = slide.shapes.add_textbox(Inches(x), Inches(y+1.5), Inches(3.5), Inches(2))
        tf = content.text_frame
        tf.word_wrap = True
        for j, item in enumerate(phase['items']):
            if j == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = "• " + item
            p.font.size = Pt(12)
            p.font.color.rgb = COLORS['dark']
            p.alignment = PP_ALIGN.CENTER

# ============ 创建幻灯片 ============

# 1. 封面 - 使用团队协作背景
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "title_bg.jpg", 0.45)

# 金色装饰
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.1), prs.slide_height)
bar.fill.solid()
bar.fill.fore_color.rgb = COLORS['accent']
bar.line.fill.background()

line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.7), prs.slide_width, Inches(0.03))
line.fill.solid()
line.fill.fore_color.rgb = COLORS['accent']
line.line.fill.background()

# 标题
title_box = slide.shapes.add_textbox(Inches(1), Inches(2.3), Inches(11), Inches(1.5))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "OpenClaw 幼儿园 AI 数字员工 SaaS"
p.font.size = Pt(52)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

sub = slide.shapes.add_textbox(Inches(1), Inches(3.8), Inches(11), Inches(0.8))
tf = sub.text_frame
p = tf.paragraphs[0]
p.text = "商业计划书"
p.font.size = Pt(32)
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER

tag = slide.shapes.add_textbox(Inches(1), Inches(4.8), Inches(11), Inches(0.5))
tf = tag.text_frame
p = tf.paragraphs[0]
p.text = "让 AI 成为每位幼儿教师的得力助手"
p.font.size = Pt(18)
p.font.color.rgb = COLORS['white']
p.font.italic = True
p.alignment = PP_ALIGN.CENTER

# 2. 项目定位 - 使用幼儿教育相关图片布局
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "business.jpg", 0.5)
add_header(slide, "🎯 项目核心定位")

# 4个核心痛点卡片
add_content_card(slide, 0.5, 1.6, 3, 2.7, "👩‍🏫 教师端", [
    "80%工作时间处理重复事务",
    "周报、通知、考勤、答疑",
    "教学陪伴时间被挤压"
], "👩‍🏫")

add_content_card(slide, 4.2, 1.6, 3, 2.7, "👨‍🏫 园长端", [
    "多园管理难、数据不互通",
    "合规审计压力大",
    "家园满意度难提升"
], "👨‍🏫")

add_content_card(slide, 7.9, 1.6, 3, 2.7, "👨‍👩‍👧 家长端", [
    "信息获取不及时",
    "个性化需求难满足",
    "园所透明度低"
], "👨‍👩‍👧")

add_content_card(slide, 0.5, 4.5, 10.5, 2.5, "💡 解决方案", [
    "用 AI 自动化实现：保教、家园、行政、后勤全流程提效",
    "私有化部署，数据不出园，满足教育合规要求",
    "5分钟一键部署，零代码操作"
], "💡")

# 3. 市场规模 - 大数字展示
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "tech.jpg", 0.5)
add_header(slide, "📊 市场规模与机会")

# 统计数据
add_stat_card(slide, 0.5, 1.6, "28万+", "国内幼儿园", COLORS['primary'])
add_stat_card(slide, 3.8, 1.6, "60%", "民营园占比", COLORS['secondary'])
add_stat_card(slide, 7.1, 1.6, "300亿+", "市场规模(元)", COLORS['accent'])
add_stat_card(slide, 10.4, 1.6, "15%+", "年复合增长率", COLORS['success'])

# 下方说明
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(4), Inches(12.3), Inches(3))
card.fill.solid()
card.fill.fore_color.rgb = COLORS['white']
card.fill.transparency = 0.9
card.line.color.rgb = COLORS['accent']
card.line.width = Pt(2)

text = slide.shapes.add_textbox(Inches(0.7), Inches(4.2), Inches(11.5), Inches(2.5))
tf = text.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "🚀 市场机会"
p.font.size = Pt(22)
p.font.bold = True
p.font.color.rgb = COLORS['primary']
p = tf.add_paragraph()
p.text = "• 传统幼教 SaaS 仅停留在信息管理层面，AI 自动化渗透率不足 5%"
p.font.size = Pt(16)
p.font.color.rgb = COLORS['dark']
p = tf.add_paragraph()
p.text = "• 存在巨大市场空白，AI + 私有化部署是差异化机会"
p.font.size = Pt(16)
p.font.color.rgb = COLORS['dark']

# 4. 产品架构 - 图示化
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "office.jpg", 0.5)
add_header(slide, "🏗️ 核心产品架构")

# 三层架构
# 上层
top_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1.6), Inches(11.3), Inches(1.5))
top_card.fill.solid()
top_card.fill.fore_color.rgb = COLORS['accent']
top_card.line.color.rgb = COLORS['white']
top_card.line.width = Pt(2)

top_text = slide.shapes.add_textbox(Inches(1), Inches(1.9), Inches(11.3), Inches(0.8))
tf = top_text.text_frame
p = tf.paragraphs[0]
p.text = "📱 上层：交互端（微信/企业微信 + 园长管理后台 + 家长小程序）"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 中层
mid_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(3.3), Inches(11.3), Inches(1.5))
mid_card.fill.solid()
mid_card.fill.fore_color.rgb = COLORS['secondary']
mid_card.line.color.rgb = COLORS['white']
mid_card.line.width = Pt(2)

mid_text = slide.shapes.add_textbox(Inches(1), Inches(3.6), Inches(11.3), Inches(0.8))
tf = mid_text.text_frame
p = tf.paragraphs[0]
p.text = "⚙️ 中层：幼教专属技能库（家园沟通 + 保教管理 + 行政后勤 + 安全合规）"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 底层
bottom_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(5), Inches(11.3), Inches(1.5))
bottom_card.fill.solid()
bottom_card.fill.fore_color.rgb = COLORS['primary']
bottom_card.line.color.rgb = COLORS['white']
bottom_card.line.width = Pt(2)

bottom_text = slide.shapes.add_textbox(Inches(1), Inches(5.3), Inches(11.3), Inches(0.8))
tf = bottom_text.text_frame
p = tf.paragraphs[0]
p.text = "🔧 底层：OpenClaw AI 执行引擎 + 国产大模型（通义千问/Qwen/文心一言）"
p.font.size = Pt(20)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 5. MVP功能 - 三列卡片
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "business.jpg", 0.5)
add_header(slide, "📦 MVP 核心功能")

add_content_card(slide, 0.5, 1.6, 4, 5.2, "🏠 家园智能助手", [
    "自动生成幼儿成长周报",
    "自动生成食谱/考勤",
    "24小时家长高频问题答疑",
    "特殊体质个性化提醒",
    "一键发家长群/私信"
], "🏠")

add_content_card(slide, 4.7, 1.6, 4, 5.2, "📚 保教自动化", [
    "按主题/年龄生成教案",
    "自动生成活动方案",
    "自动整理观察笔记",
    "生成幼儿发展评估报告",
    "幼儿档案自动归档"
], "📚")

add_content_card(slide, 9, 1.6, 4, 5.2, "🍽️ 后勤自动化", [
    "自动排班、考勤统计",
    "缺勤预警",
    "按营养标准生成食谱",
    "联动库存生成采购清单",
    "费用账单自动生成"
], "🍽️")

# 6. 产品迭代 - 可视化时间线
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "gradient_dark_blue.jpg", 0.3)
add_header(slide, "📅 产品迭代路线")

add_timeline_visual(slide, [
    {"title": "🚀 0-3个月 MVP", "items": ["核心3模块开发", "5分钟一键部署", "对接微信", "签约5家种子园"]},
    {"title": "📈 3-6个月 完善", "items": ["安全合规模块", "集团多园管理版", "优化技能库", "签约50家园所"]},
    {"title": "🌟 6-12个月 生态", "items": ["家长端增值服务", "幼教技能商店", "API开放", "签约200家园所"]}
])

# 7. 商业模式 - 4层变现
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "tech.jpg", 0.5)
add_header(slide, "💰 四层递进变现体系")

# 4个层级卡片
add_content_card(slide, 0.3, 1.5, 3.1, 2.4, "💳 基础层：B端SaaS", [
    "标准版 2980元/园/年",
    "专业版 5980元/园/年",
    "集团版 29800元/集团/年"
], "💳")

add_content_card(slide, 3.6, 1.5, 3.1, 2.4, "🔧 增值层：服务", [
    "部署实施 1800-3600元",
    "定制开发 5000-20000元",
    "年度运维 800元/园/年"
], "🔧")

add_content_card(slide, 6.9, 1.5, 3.1, 2.4, "🌐 生态层：B2B2C", [
    "C端家长增值 30-98元/月",
    "供应链分成 10%-30%",
    "合规数据服务"
], "🌐")

add_content_card(slide, 10.2, 1.5, 3.1, 2.4, "🏛️ 平台层：生态", [
    "技能商店佣金 15%-30%",
    "认证培训 980-2980元",
    "引擎授权"
], "🏛️")

# 8. 盈利测算 - 表格
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "office.jpg", 0.5)
add_header(slide, "📈 12个月盈利测算")

# 表格
table = slide.shapes.add_table(4, 6, Inches(0.5), Inches(1.6), Inches(12.3), Inches(5)).table
cols = ["阶段", "园所", "订阅营收", "增值服务", "总营收", "核心目标"]
for i, c in enumerate(cols):
    cell = table.cell(0, i)
    cell.text = c
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLORS['primary']
    cell.text_frame.paragraphs[0].font.size = Pt(14)
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.color.rgb = COLORS['white']
    cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

data = [
    ["0-3月", "5家", "0(免费)", "0", "0", "验证产品价值"],
    ["3-6月", "50家", "20万", "5万", "25万", "月营收5万+"],
    ["6-12月", "200家", "100万", "40万", "140万", "单月盈利"]
]
for r, row in enumerate(data, 1):
    for c, val in enumerate(row):
        cell = table.cell(r, c)
        cell.text = val
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['white'] if r % 2 == 0 else COLORS['light']
        cell.text_frame.paragraphs[0].font.size = Pt(13)
        cell.text_frame.paragraphs[0].font.color.rgb = COLORS['dark']
        cell.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

# 9. 核心壁垒 - 4个图标卡片
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "gradient_dark_blue.jpg", 0.4)
add_header(slide, "🛡️ 四大核心壁垒")

add_content_card(slide, 0.3, 1.5, 3, 2.6, "📚 行业Know-How", [
    "深度贴合幼教政策",
    "《3-6岁儿童学习与发展指南》",
    "专属幼教技能库护城河"
], "📚")

add_content_card(slide, 3.5, 1.5, 3, 2.6, "🔐 数据合规", [
    "本地私有化部署",
    "数据不出园",
    "权限隔离与审计"
], "🔐")

add_content_card(slide, 6.7, 1.5, 3, 2.6, "⚙️ 技术交付", [
    "5分钟一键部署",
    "零代码操作",
    "落地门槛极低"
], "⚙️")

add_content_card(slide, 9.9, 1.5, 3, 2.6, "🌐 网络效应", [
    "园所越多→越完善",
    "家长用户越多",
    "供应链越丰富"
], "🌐")

# 10. 融资计划
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "business.jpg", 0.5)
add_header(slide, "💼 融资计划")

# 融资卡片
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(2), Inches(9.3), Inches(2))
card.fill.solid()
card.fill.fore_color.rgb = COLORS['primary']
card.line.color.rgb = COLORS['accent']
card.line.width = Pt(3)

text = slide.shapes.add_textbox(Inches(2.5), Inches(2.5), Inches(8.5), Inches(1.5))
tf = text.text_frame
p = tf.paragraphs[0]
p.text = "天使轮融资"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER
p = tf.add_paragraph()
p.text = "500-1000万元  |  出让10%-15%股权"
p.font.size = Pt(20)
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 资金用途
uses = [("40%", "产品研发", "🏗️"), ("35%", "市场拓展", "📢"), ("20%", "团队建设", "👥"), ("5%", "运营储备", "🔧")]
for i, (pct, label, icon) in enumerate(uses):
    x = 1 + i * 3
    add_stat_card(slide, x, 4.5, pct, label, COLORS['secondary'])

# 11. 结束页
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_picture_background(slide, "gradient_dark_blue.jpg", 0.2)

circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.3), Inches(1.8), Inches(2.7), Inches(2.7))
circle.fill.solid()
circle.fill.fore_color.rgb = COLORS['accent']
circle.line.fill.background()
circle.transparency = 0.5

title = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1.2))
tf = title.text_frame
p = tf.paragraphs[0]
p.text = "携手共创幼教 AI 新未来"
p.font.size = Pt(42)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

sub = slide.shapes.add_textbox(Inches(1), Inches(5.2), Inches(11), Inches(0.8))
tf = sub.text_frame
p = tf.paragraphs[0]
p.text = "让 AI 成为每位幼儿教师的得力助手"
p.font.size = Pt(24)
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER

# 保存
output = r"C:\Users\17699\.openclaw\workspace\商业计划书_图片丰富版.pptx"
prs.save(output)
print(f"Image-rich PPT saved: {output}")
print(f"Total: {len(prs.slides)} pages")