# -*- coding: utf-8 -*-
"""
OpenClaw 幼儿园 AI 数字员工 SaaS 商业计划书 - 豪华专业版
给特朗普汇报的高规格版本
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Cm, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_VERTICAL_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import nsmap, qn

# 创建演示文稿 - 16:9 比例
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# ============ 轻奢配色方案 ============
COLORS = {
    'primary': RGBColor(0x1A, 0x2B, 0x4A),      # 深海军蓝 - 主色调
    'secondary': RGBColor(0x00, 0x5A, 0xBE),    # 宝石蓝 - 副色
    'accent': RGBColor(0xD4, 0xAF, 0x37),       # 金色 - 高端点缀
    'accent_light': RGBColor(0xF5, 0xE6, 0xB3), # 浅金色
    'dark': RGBColor(0x2D, 0x34, 0x45),         # 深灰 - 文字
    'light': RGBColor(0xF8, 0xFA, 0xFC),        # 浅灰白 - 背景
    'white': RGBColor(0xFF, 0xFF, 0xFF),
    'gradient_start': RGBColor(0x1A, 0x2B, 0x4A),
    'gradient_end': RGBColor(0x00, 0x5A, 0xBE),
}

def set_shape_gradient(shape, color1, color2):
    """设置形状渐变"""
    # 使用模拟渐变效果 - 通过多个重叠形状
    pass  # 简化版本

def create_master_title_slide(prs, title, subtitle, tagline=""):
    """创建豪华标题页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 全屏渐变背景
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['primary']
    bg.line.fill.background()
    
    # 金色装饰线条 - 顶部
    line1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.8), prs.slide_width, Inches(0.02))
    line1.fill.solid()
    line1.fill.fore_color.rgb = COLORS['accent']
    line1.line.fill.background()
    
    # 金色装饰线条 - 底部
    line2 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, prs.slide_height - Inches(1), prs.slide_width, Inches(0.02))
    line2.fill.solid()
    line2.fill.fore_color.rgb = COLORS['accent']
    line2.line.fill.background()
    
    # 左侧金色竖条
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.15), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLORS['accent']
    bar.line.fill.background()
    
    # 右上角装饰圆
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11), Inches(0.3), Inches(1.5), Inches(1.5))
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['accent']
    circle.line.fill.background()
    circle.transparency = 0.7
    
    # 主标题 - 居中
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.2), Inches(11), Inches(1.8))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(52)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1))
    tf = subtitle_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(28)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER
    
    # 标签语
    if tagline:
        tagline_box = slide.shapes.add_textbox(Inches(1), Inches(5.2), Inches(11), Inches(0.6))
        tf = tagline_box.text_frame
        p = tf.paragraphs[0]
        p.text = tagline
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['white']
        p.font.italic = True
        p.transparency = 0.3
        p.alignment = PP_ALIGN.CENTER
    
    return slide

def create_premium_content_slide(prs, title, content_items, icon=None):
    """创建精品内容页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部深色标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 金色底线
    gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), prs.slide_width, Inches(0.05))
    gold_line.fill.solid()
    gold_line.fill.fore_color.rgb = COLORS['accent']
    gold_line.line.fill.background()
    
    # 标题图标（如果提供）
    if icon:
        icon_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(0.5), Inches(0.5))
        tf = icon_box.text_frame
        p = tf.paragraphs[0]
        p.text = icon
        p.font.size = Pt(32)
    
    # 标题文字
    title_box = slide.shapes.add_textbox(Inches(1), Inches(0.35), Inches(11), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 内容区域 - 带浅色背景
    content_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), Inches(1.5), Inches(12.3), Inches(5.5))
    content_bg.fill.solid()
    content_bg.fill.fore_color.rgb = COLORS['light']
    content_bg.line.color.rgb = COLORS['accent_light']
    content_bg.line.width = Pt(1)
    
    # 内容文字
    content_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        
        if item.startswith("##"):
            # 二级标题
            p.text = item.replace("## ", "")
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = COLORS['primary']
            p.space_before = Pt(18)
            p.space_after = Pt(8)
        elif item.startswith("•"):
            # 普通项目符号
            p.text = item
            p.font.size = Pt(18)
            p.font.color.rgb = COLORS['dark']
            p.space_after = Pt(10)
            p.level = 0
        else:
            p.text = item
            p.font.size = Pt(18)
            p.font.color.rgb = COLORS['dark']
            p.space_after = Pt(8)
    
    return slide

def create_two_col_premium(prs, title, left_title, left_items, right_title, right_items):
    """创建精品双栏页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部深色标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 金色底线
    gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), prs.slide_width, Inches(0.05))
    gold_line.fill.solid()
    gold_line.fill.fore_color.rgb = COLORS['accent']
    gold_line.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 左栏标题
    ltitle = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(5.8), Inches(0.5))
    tf = ltitle.text_frame
    p = tf.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']
    
    # 左栏内容
    lbox = slide.shapes.add_textbox(Inches(0.5), Inches(2.1), Inches(5.8), Inches(4.8))
    tf = lbox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(left_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(10)
    
    # 分隔线
    divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.3), Inches(1.5), Inches(0.03), Inches(5.5))
    divider.fill.solid()
    divider.fill.fore_color.rgb = COLORS['accent_light']
    divider.line.fill.background()
    
    # 右栏标题
    rtitle = slide.shapes.add_textbox(Inches(6.8), Inches(1.5), Inches(5.8), Inches(0.5))
    tf = rtitle.text_frame
    p = tf.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['secondary']
    
    # 右栏内容
    rbox = slide.shapes.add_textbox(Inches(6.8), Inches(2.1), Inches(5.8), Inches(4.8))
    tf = rbox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(right_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(10)
    
    return slide

def create_table_page(prs, title, headers, rows):
    """创建精品表格页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部深色标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), prs.slide_width, Inches(0.05))
    gold_line.fill.solid()
    gold_line.fill.fore_color.rgb = COLORS['accent']
    gold_line.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 表格
    table_rows = len(rows) + 1
    table_cols = len(headers)
    
    # 计算列宽
    table_width = Inches(12.3)
    col_width = table_width / table_cols
    
    table = slide.shapes.add_table(table_rows, table_cols, Inches(0.5), Inches(1.5), table_width, Inches(5.2)).table
    
    # 设置列宽（使用EMU单位）
    for i in range(table_cols):
        table.columns[i].width = int(col_width)
    
    # 表头样式
    for i, header in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = header
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['primary']
        tf = cell.text_frame
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = COLORS['white']
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 数据行样式
    for row_idx, row_data in enumerate(rows, 1):
        for col_idx, cell_data in enumerate(row_data[:table_cols]):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(cell_data)
            
            # 交替行颜色
            if row_idx % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLORS['light']
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLORS['white']
            
            tf = cell.text_frame
            tf.paragraphs[0].font.size = Pt(12)
            tf.paragraphs[0].font.color.rgb = COLORS['dark']
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            tf.word_wrap = True
    
    return slide

def create_timeline_premium(prs, title, phases):
    """创建精品时间线页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部深色标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    gold_line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), prs.slide_width, Inches(0.05))
    gold_line.fill.solid()
    gold_line.fill.fore_color.rgb = COLORS['accent']
    gold_line.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(32)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 时间线
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    start_x = Inches(0.8)
    circle_y = Inches(3.2)
    box_y = Inches(4.2)
    
    for i, phase in enumerate(phases):
        x = start_x + i * Inches(4.2)
        
        # 圆圈（带金边）
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, circle_y, Inches(1), Inches(1))
        circle.fill.solid()
        circle.fill.fore_color.rgb = colors[i % len(colors)]
        circle.line.color.rgb = COLORS['accent']
        circle.line.width = Pt(3)
        
        # 阶段号
        num_box = slide.shapes.add_textbox(x, circle_y + Inches(0.25), Inches(1), Inches(0.5))
        tf = num_box.text_frame
        p = tf.paragraphs[0]
        p.text = str(i + 1)
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER
        
        # 连接线
        if i < len(phases) - 1:
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(1), circle_y + Inches(0.48), Inches(3.2), Inches(0.04))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS['accent']
            line.line.fill.background()
        
        # 阶段标题
        title_box = slide.shapes.add_textbox(x - Inches(0.2), box_y, Inches(3.6), Inches(0.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = phase['title']
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = colors[i % len(colors)]
        p.alignment = PP_ALIGN.CENTER
        
        # 阶段内容
        content_box = slide.shapes.add_textbox(x - Inches(0.2), box_y + Inches(0.5), Inches(3.6), Inches(2.5))
        tf = content_box.text_frame
        tf.word_wrap = True
        for j, item in enumerate(phase['items']):
            if j == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(13)
            p.font.color.rgb = COLORS['dark']
            p.alignment = PP_ALIGN.CENTER
    
    return slide

def create_end_slide(prs, title, subtitle, contact=""):
    """创建结束页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 全屏渐变背景
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['primary']
    bg.line.fill.background()
    
    # 金色装饰
    line1 = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(3), prs.slide_width, Inches(0.02))
    line1.fill.solid()
    line1.fill.fore_color.rgb = COLORS['accent']
    line1.line.fill.background()
    
    # 中央金色圆
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.5), Inches(1.8), Inches(2.33), Inches(2.33))
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['accent']
    circle.line.fill.background()
    circle.transparency = 0.5
    
    # 主标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(11), Inches(1.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(5), Inches(11), Inches(0.8))
    tf = subtitle_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(24)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER
    
    # 联系信息
    if contact:
        contact_box = slide.shapes.add_textbox(Inches(1), Inches(6), Inches(11), Inches(0.5))
        tf = contact_box.text_frame
        p = tf.paragraphs[0]
        p.text = contact
        p.font.size = Pt(14)
        p.font.color.rgb = COLORS['white']
        p.transparency = 0.5
        p.alignment = PP_ALIGN.CENTER
    
    return slide

# ============ 创建PPT内容 ============

# 1. 封面
create_master_title_slide(
    prs,
    "OpenClaw 幼儿园 AI 数字员工 SaaS",
    "商业计划书",
    "让 AI 成为每位幼儿教师的得力助手"
)

# 2. 目录
create_premium_content_slide(
    prs,
    "📋 目录",
    [
        "## 项目核心定位",
        "• 打造国内首款面向幼儿园的私有化部署 AI 数字员工 SaaS",
        "• 聚焦解决民营中高端幼儿园四大核心痛点",
        "",
        "## 市场与痛点分析",
        "• 国内幼儿园超 28 万所，幼教信息化市场规模超 300 亿元",
        "• AI 自动化渗透率不足 5%，存在巨大市场空白",
        "",
        "## 产品与 MVP 方案",
        "• 核心产品架构：底层引擎 + 中层技能库 + 上层交互端",
        "• MVP 核心功能：家园智能助手、保教自动化、后勤自动化",
        "",
        "## 商业模式与盈利测算",
        "• 四层递进变现体系：B 端 SaaS 订阅 + 增值服务 + 生态层 + 平台层",
        "",
        "## 获客与落地执行计划",
        "• 种子客户 + 渠道合作 + 转化钩子 + 标杆打造",
        "",
        "## 团队与核心壁垒",
        "• 行业 Know-How + 数据合规 + 技术交付 + 网络效应",
        "",
        "## 风险与应对策略",
        "• 合规风险 + 竞争风险 + 技术风险 + 推广风险",
        "",
        "## 融资计划",
        "• 天使轮 500-1000 万，3-5 年实现行业并购或 IPO 退出"
    ]
)

# 3. 项目核心定位
create_premium_content_slide(
    prs,
    "🎯 项目核心定位",
    [
        "## 核心愿景",
        "打造国内首款面向幼儿园的私有化部署 AI 数字员工 SaaS",
        "",
        "## 四大核心痛点解决",
        "• 👩‍🏫 教师重复劳动多 → AI 自动化替代 80% 重复工作",
        "• 📱 家园沟通低效 → 智能沟通助手 24 小时响应",
        "• 🔒 数据安全合规难 → 本地私有化部署，数据不出园",
        "• 📊 管理流程不规范 → 标准化 AI 流程",
        "",
        "## 价值主张",
        "用 AI 自动化实现保教、家园、行政、后勤全流程提效"
    ]
)

# 4. 市场规模
create_two_col_premium(
    prs,
    "📊 市场规模与机会",
    "🎯 市场容量",
    [
        "• 国内幼儿园超 28 万所",
        "• 民营园占比超 60%",
        "• 幼教信息化市场规模超 300 亿元",
        "• 年复合增长率 15%+",
        "",
        "⚡ AI 渗透率不足 5%",
        "存在巨大市场空白"
    ],
    "💡 传统 SaaS 局限",
    [
        "• 仅停留在信息管理层面",
        "• 无法自动执行任务",
        "• 数据上公云，合规风险高",
        "• 无法真正减轻教师负担",
        "",
        "🚀 我们的机会：",
        "AI 自动化 + 私有化部署"
    ]
)

# 5. 核心痛点
create_premium_content_slide(
    prs,
    "😫 行业核心痛点",
    [
        "## 👩‍🏫 教师端",
        "• 80% 工作时间消耗在周报、通知、考勤、家长答疑等重复事务",
        "• 教学陪伴时间被严重挤压",
        "",
        "## 👨‍🏫 园长端",
        "• 多园管理难、数据不互通",
        "• 合规审计压力大、家园满意度难提升",
        "",
        "## 👨‍👩‍👧 家长端",
        "• 信息获取不及时、个性化需求难满足",
        "• 园所透明度低",
        "",
        "## 🏢 行业端",
        "• 传统 SaaS 数据上公云，幼儿隐私数据存在合规风险"
    ]
)

# 6. 差异化优势
create_premium_content_slide(
    prs,
    "🚀 三大差异化优势",
    [
        "## 🔒 技术壁垒",
        "• OpenClaw 开源引擎 + 国产大模型适配",
        "• 支持本地私有化部署，数据不出园",
        "• 完全符合教育数据合规要求",
        "",
        "## ⚡ 功能壁垒",
        "• 区别于传统 SaaS 的信息录入",
        "• 实现「自然语言指令→自动执行」",
        "• 真正替代人工完成重复工作",
        "",
        "## 🎁 交付壁垒",
        "• 5 分钟一键部署",
        "• 零代码操作",
        "• 园长/老师无需技术基础即可使用"
    ]
)

# 7. 产品架构
create_premium_content_slide(
    prs,
    "🏗️ 核心产品架构",
    [
        "## 上层：交互端",
        "• 微信/企业微信原生交互端",
        "• 园长管理后台",
        "• 家长端小程序",
        "",
        "## 中层：幼教专属技能库",
        "• 家园沟通模块",
        "• 保教管理模块",
        "• 行政后勤模块",
        "• 安全合规模块",
        "",
        "## 底层：AI 执行引擎",
        "• OpenClaw AI 执行引擎（私有化部署）",
        "• 国产大模型（通义千问/Qwen/文心一言）"
    ]
)

# 8. MVP 核心功能表格
create_table_page(
    prs,
    "📦 MVP 核心功能（0-3 个月落地）",
    ["模块", "核心技能", "解决痛点"],
    [
        ["家园智能助手", "• 自动生成周报/食谱/考勤\n• 24小时家长问题自动答疑\n• 特殊体质幼儿个性化提醒", "解放老师80%家园沟通时间"],
        ["保教自动化", "• 自动生成教案、活动方案\n• 自动整理观察笔记\n• 幼儿发展评估报告", "降低备课、评估工作量"],
        ["后勤自动化", "• 自动排班、考勤统计\n• 智能食谱+采购清单\n• 费用账单自动生成", "简化行政流程，减少出错"]
    ]
)

# 9. 产品迭代路线
create_timeline_premium(
    prs,
    "📅 产品迭代路线",
    [
        {
            "title": "0-3 个月 MVP",
            "items": ["完成核心3个模块", "5分钟一键部署", "对接微信/企业微信"]
        },
        {
            "title": "3-6 个月 完善",
            "items": ["完善安全合规模块", "推出集团多园管理版", "优化技能库"]
        },
        {
            "title": "6-12 个月 生态",
            "items": ["上线家长端增值服务", "幼教技能商店", "开放API对接"]
        }
    ]
)

# 10. 商业模式
create_premium_content_slide(
    prs,
    "💰 四层递进变现体系",
    [
        "## 1️⃣ 基础层：B 端 SaaS 订阅（核心现金流）",
        "• 标准版 2980 元/园/年 | 专业版 5980 元/园/年 | 集团版 29800 元/集团/年",
        "",
        "## 2️⃣ 增值层：高毛利服务",
        "• 部署实施费 1800-3600 元/园 | 定制开发 5000-20000 元/个",
        "• 年度运维 800 元/园/年",
        "",
        "## 3️⃣ 生态层：B2B2C 增值变现",
        "• C端家长增值 30-98 元/月 | 供应链分成 10%-30%",
        "",
        "## 4️⃣ 平台层：生态壁垒变现",
        "• 技能商店佣金 15%-30% | 认证培训 980-2980 元/人 | 引擎授权"
    ]
)

# 11. 版本定价表格
create_table_page(
    prs,
    "💎 SaaS 订阅版本定价",
    ["版本", "定价", "适配客群", "核心权益"],
    [
        ["标准版", "2980元\n/园/年", "10-15班\n民营园", "核心3模块\n云托管部署\n基础技术支持"],
        ["专业版", "5980元\n/园/年", "15-30班\n中高端园", "全模块功能\n本地私有化\n无限技能调用"],
        ["集团版", "29800元\n/集团/年", "连锁幼教\n集团", "多园统一管理\n定制化开发\n7×24支持"]
    ]
)

# 12. 盈利测算
create_table_page(
    prs,
    "📈 12 个月盈利测算（目标）",
    ["阶段", "园所", "订阅营收", "增值服务", "总营收", "核心目标"],
    [
        ["0-3月", "5家", "0\n(免费)", "0", "0", "验证产品价值"],
        ["3-6月", "50家", "20万", "5万", "25万", "月营收5万+"],
        ["6-12月", "200家", "100万", "40万", "140万", "单月盈利"]
    ]
)

# 13. 获客策略
create_premium_content_slide(
    prs,
    "🎣 获客策略（低成本起量）",
    [
        "## 🌱 种子客户",
        "• 3-5 家区域头部民营园/连锁幼教集团",
        "• 免费试用 1-3 个月，换取深度反馈与案例背书",
        "",
        "## 🤝 渠道合作",
        "• 幼教展会、园长社群、区域代理商、行业媒体",
        "• 按成交金额支付 20%-30% 佣金",
        "",
        "## 🎁 转化钩子",
        "•「免费试用 1 个月，教师工作时间减少 50%，无效全额退款」",
        "",
        "## 🏆 标杆打造",
        "• 打造 3 个标杆案例（单园、连锁园、区域集团）",
        "• 形成可复制的落地 SOP"
    ]
)

# 14. 执行路线图
create_timeline_premium(
    prs,
    "🗺️ 12 个月落地执行路线",
    [
        {
            "title": "阶段 1: 0-3 个月",
            "items": ["MVP验证期", "核心3模块开发", "签约5家种子园", "验证核心价值"]
        },
        {
            "title": "阶段 2: 3-6 个月",
            "items": ["规模化复制", "团队扩充8人", "签约50家园所", "月营收5万+"]
        },
        {
            "title": "阶段 3: 6-12 个月",
            "items": ["生态扩张期", "团队扩充15人", "签约200家园所", "启动天使轮"]
        }
    ]
)

# 15. 核心壁垒
create_premium_content_slide(
    prs,
    "🛡️ 四大核心壁垒",
    [
        "## 📚 行业 Know-How 壁垒",
        "• 深度贴合幼教政策、《3-6 岁儿童学习与发展指南》",
        "• 沉淀专属幼教技能库，形成行业护城河",
        "",
        "## 🔐 数据合规壁垒",
        "• 本地私有化部署，数据不出园",
        "• 权限隔离与审计日志，满足教育数据监管",
        "",
        "## ⚙️ 技术交付壁垒",
        "• 一键部署、零代码操作体系",
        "• 大幅降低落地门槛",
        "",
        "## 🌐 网络效应壁垒",
        "• 园所越多→家长越多→供应链越丰富→技能库越完善",
        "• 形成正向循环"
    ]
)

# 16. 风险与应对
create_table_page(
    prs,
    "⚠️ 风险与应对策略",
    ["风险类型", "具体风险", "应对方案"],
    [
        ["合规风险", "幼儿数据隐私\n政策监管", "本地部署+数据不出园\n提前对接教育部门备案\n完善权限隔离"],
        ["竞争风险", "传统SaaS厂商\nAI巨头入局", "聚焦垂直细分\n私有化部署差异化\n快速抢占标杆客户"],
        ["技术风险", "开源迭代\n模型适配", "深度参与社区迭代\n兼容多款国产大模型\n完善测试运维体系"],
        ["推广风险", "园长决策链长\n付费意愿低", "免费试用+ROI测算\n聚焦中高端民营园\n与代理商合作"]
    ]
)

# 17. 融资计划
create_premium_content_slide(
    prs,
    "💼 融资计划",
    [
        "## 融资轮次：天使轮",
        "## 融资金额：500-1000 万元",
        "## 出让股权：10%-15%",
        "",
        "## 资金用途：",
        "• 🏗️ 产品研发 40% - 完善技能库、生态平台、API对接",
        "• 📢 市场拓展 35% - 渠道建设、标杆案例、品牌推广",
        "• 👥 团队建设 20% - 扩充研发、销售、运营团队",
        "• 🔧 运营储备 5% - 客户成功、运维服务",
        "",
        "## 退出机制：",
        "• 3-5 年实现幼教垂直 AI 平台头部地位",
        "• 寻求行业并购或 IPO 退出"
    ]
)

# 18. 结束页
create_end_slide(
    prs,
    "携手共创幼教 AI 新未来",
    "让 AI 成为每位幼儿教师的得力助手",
    "OpenClaw 幼儿园 AI 数字员工 SaaS"
)

# 保存 PPT
output_path = r"C:\Users\17699\.openclaw\workspace\OpenClaw_Kindergarten_AI_Business_Plan_V2.pptx"
prs.save(output_path)
print(f"Premium PPT generated: {output_path}")
print(f"Total pages: {len(prs.slides)}")