# -*- coding: utf-8 -*-
"""
超精美商业计划书 PPT - 使用真实高质量图片背景
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.slide import Slide

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
}

def add_picture_as_background(slide, image_path, overlay_alpha=0.4):
    """添加图片作为背景"""
    # 计算缩放以覆盖整个幻灯片
    slide_width = prs.slide_width
    slide_height = prs.slide_height
    
    # 添加图片
    pic = slide.shapes.add_picture(
        image_path,
        Inches(0), Inches(0),
        width=slide_width
    )
    
    # 调整图片位置确保覆盖
    if pic.height < slide_height:
        pic.top = int((slide_height - pic.height) / 2)
    
    # 添加半透明黑色遮罩
    overlay = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, slide_width, slide_height
    )
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = COLORS['overlay']
    overlay.fill.transparency = overlay_alpha
    overlay.line.fill.background()
    
    return slide

def add_content_overlay(slide, title, items):
    """添加内容层"""
    # 顶部半透明背景
    header = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.4)
    )
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.fill.transparency = 0.85
    header.line.fill.background()
    
    # 金色底线
    gold = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, Inches(1.35), prs.slide_width, Inches(0.04)
    )
    gold.fill.solid()
    gold.fill.fore_color.rgb = COLORS['accent']
    gold.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 内容背景
    content_bg = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.3), Inches(1.6), Inches(12.7), Inches(5.5)
    )
    content_bg.fill.solid()
    content_bg.fill.fore_color.rgb = COLORS['white']
    content_bg.fill.transparency = 0.92
    content_bg.line.color.rgb = COLORS['accent']
    content_bg.line.width = Pt(1)
    
    # 内容文字
    content_box = slide.shapes.add_textbox(Inches(0.6), Inches(1.8), Inches(12), Inches(5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        
        if item.startswith("##"):
            p.text = item.replace("## ", "")
            p.font.size = Pt(22)
            p.font.bold = True
            p.font.color.rgb = COLORS['primary']
            p.space_before = Pt(16)
            p.space_after = Pt(8)
        elif item.startswith("•"):
            p.text = item
            p.font.size = Pt(16)
            p.font.color.rgb = COLORS['dark']
            p.space_after = Pt(8)
        else:
            p.text = item
            p.font.size = Pt(16)
            p.font.color.rgb = COLORS['dark']
            p.space_after = Pt(6)

def create_title_slide(slide, title, subtitle, tagline=""):
    """创建标题页"""
    # 使用高质量背景图
    add_picture_as_background(slide, os.path.join(IMG_DIR, "title_bg.jpg"), 0.5)
    
    # 左侧金色竖条
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.12), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = COLORS['accent']
    bar.line.fill.background()
    
    # 顶部装饰线
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.8), prs.slide_width, Inches(0.03))
    line.fill.solid()
    line.fill.fore_color.rgb = COLORS['accent']
    line.line.fill.background()
    
    # 主标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.5))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(54)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    sub = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(0.8))
    tf = sub.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(28)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER
    
    # 标签语
    if tagline:
        tag = slide.shapes.add_textbox(Inches(1), Inches(5), Inches(11), Inches(0.5))
        tf = tag.text_frame
        p = tf.paragraphs[0]
        p.text = tagline
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['white']
        p.font.italic = True
        p.transparency = 0.4
        p.alignment = PP_ALIGN.CENTER
    
    # 底部装饰
    bottom = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, prs.slide_height - Inches(0.8), prs.slide_width, Inches(0.03))
    bottom.fill.solid()
    bottom.fill.fore_color.rgb = COLORS['accent']
    bottom.line.fill.background()

def create_content_slide(slide, title, items):
    """创建内容页"""
    # 使用商务背景图
    add_picture_as_background(slide, os.path.join(IMG_DIR, "business.jpg"), 0.55)
    add_content_overlay(slide, title, items)

def create_two_col_slide(slide, title, left_title, left_items, right_title, right_items):
    """创建双栏页"""
    add_picture_as_background(slide, os.path.join(IMG_DIR, "tech.jpg"), 0.55)
    
    # 顶部背景
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.4))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.fill.transparency = 0.85
    header.line.fill.background()
    
    gold = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.35), prs.slide_width, Inches(0.04))
    gold.fill.solid()
    gold.fill.fore_color.rgb = COLORS['accent']
    gold.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 左栏背景
    lbg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.3), Inches(1.6), Inches(6), Inches(5.5))
    lbg.fill.solid()
    lbg.fill.fore_color.rgb = COLORS['white']
    lbg.fill.transparency = 0.9
    lbg.line.color.rgb = COLORS['accent']
    lbg.line.width = Pt(1)
    
    # 左栏标题
    ltitle = slide.shapes.add_textbox(Inches(0.5), Inches(1.7), Inches(5.5), Inches(0.5))
    tf = ltitle.text_frame
    p = tf.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']
    
    # 左栏内容
    lbox = slide.shapes.add_textbox(Inches(0.5), Inches(2.3), Inches(5.5), Inches(4.5))
    tf = lbox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(left_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(15)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(8)
    
    # 分隔线
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.5), Inches(1.6), Inches(0.03), Inches(5.5))
    div.fill.solid()
    div.fill.fore_color.rgb = COLORS['accent']
    div.line.fill.background()
    
    # 右栏背景
    rbg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.7), Inches(1.6), Inches(6), Inches(5.5))
    rbg.fill.solid()
    rbg.fill.fore_color.rgb = COLORS['white']
    rbg.fill.transparency = 0.9
    rbg.line.color.rgb = COLORS['secondary']
    rbg.line.width = Pt(1)
    
    # 右栏标题
    rtitle = slide.shapes.add_textbox(Inches(6.9), Inches(1.7), Inches(5.5), Inches(0.5))
    tf = rtitle.text_frame
    p = tf.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = COLORS['secondary']
    
    # 右栏内容
    rbox = slide.shapes.add_textbox(Inches(6.9), Inches(2.3), Inches(5.5), Inches(4.5))
    tf = rbox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(right_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(15)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(8)

def create_table_slide(slide, title, headers, rows):
    """创建表格页"""
    add_picture_as_background(slide, os.path.join(IMG_DIR, "office.jpg"), 0.55)
    
    # 顶部背景
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.4))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.fill.transparency = 0.85
    header.line.fill.background()
    
    gold = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.35), prs.slide_width, Inches(0.04))
    gold.fill.solid()
    gold.fill.fore_color.rgb = COLORS['accent']
    gold.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.4), Inches(12), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 表格
    table_rows = len(rows) + 1
    table_cols = len(headers)
    
    table = slide.shapes.add_table(
        table_rows, table_cols,
        Inches(0.5), Inches(1.6),
        Inches(12.3), Inches(5.2)
    ).table
    
    # 列宽
    col_w = Inches(12.3) / table_cols
    for i in range(table_cols):
        table.columns[i].width = int(col_w)
    
    # 表头
    for i, h in enumerate(headers):
        cell = table.cell(0, i)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['primary']
        tf = cell.text_frame
        tf.paragraphs[0].font.size = Pt(14)
        tf.paragraphs[0].font.bold = True
        tf.paragraphs[0].font.color.rgb = COLORS['white']
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    
    # 数据
    for r, row in enumerate(rows, 1):
        for c, val in enumerate(row[:table_cols]):
            cell = table.cell(r, c)
            cell.text = str(val)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLORS['white'] if r % 2 == 0 else COLORS['light']
            tf = cell.text_frame
            tf.paragraphs[0].font.size = Pt(12)
            tf.paragraphs[0].font.color.rgb = COLORS['dark']
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            tf.word_wrap = True

def create_end_slide(slide, title, subtitle):
    """结束页"""
    add_picture_as_background(slide, os.path.join(IMG_DIR, "gradient_dark_blue.jpg"), 0.2)
    
    # 中央金色圆
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.5), Inches(2), Inches(2.33), Inches(2.33))
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['accent']
    circle.line.fill.background()
    circle.transparency = 0.4
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1.2))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(42)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    sub = slide.shapes.add_textbox(Inches(1), Inches(5.2), Inches(11), Inches(0.8))
    tf = sub.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(24)
    p.font.color.rgb = COLORS['accent']
    p.alignment = PP_ALIGN.CENTER

# ============ 创建 PPT ============
import os

# 1. 封面
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_title_slide(slide, "OpenClaw 幼儿园 AI 数字员工 SaaS", "商业计划书", "让 AI 成为每位幼儿教师的得力助手")

# 2. 目录
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "📋 目录", [
    "## 项目核心定位",
    "• 打造国内首款面向幼儿园的私有化部署 AI 数字员工 SaaS",
    "",
    "## 市场与痛点分析",
    "• 国内幼儿园超 28 万所，幼教信息化市场规模超 300 亿元",
    "",
    "## 产品与 MVP 方案",
    "• 核心产品架构：底层引擎 + 中层技能库 + 上层交互端",
    "",
    "## 商业模式与盈利测算",
    "• 四层递进变现体系",
    "",
    "## 获客与落地执行计划",
    "## 团队与核心壁垒",
    "## 风险与应对策略",
    "## 融资计划"
])

# 3. 项目定位
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "🎯 项目核心定位", [
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
])

# 4. 市场规模
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_two_col_slide(slide, "📊 市场规模与机会",
    "🎯 市场容量",
    ["• 国内幼儿园超 28 万所", "• 民营园占比超 60%", "• 幼教信息化市场规模超 300 亿元", "• 年复合增长率 15%+", "", "⚡ AI 渗透率不足 5%", "存在巨大市场空白"],
    "💡 传统 SaaS 局限",
    ["• 仅停留在信息管理层面", "• 无法自动执行任务", "• 数据上公云，合规风险高", "• 无法真正减轻教师负担", "", "🚀 我们的机会：", "AI 自动化 + 私有化部署"]
)

# 5. 核心痛点
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "😫 行业核心痛点", [
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
    "• 园所透明度低"
])

# 6. 差异化优势
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "🚀 三大差异化优势", [
    "## 🔒 技术壁垒",
    "• OpenClaw 开源引擎 + 国产大模型适配",
    "• 支持本地私有化部署，数据不出园",
    "• 完全符合教育数据合规要求",
    "",
    "## ⚡ 功能壁垒",
    "• 实现「自然语言指令→自动执行」",
    "• 真正替代人工完成重复工作",
    "",
    "## 🎁 交付壁垒",
    "• 5 分钟一键部署",
    "• 零代码操作"
])

# 7. 产品架构
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "🏗️ 核心产品架构", [
    "## 上层：交互端",
    "• 微信/企业微信原生交互端",
    "• 园长管理后台",
    "• 家长端小程序",
    "",
    "## 中层：幼教专属技能库",
    "• 家园沟通模块 • 保教管理模块",
    "• 行政后勤模块 • 安全合规模块",
    "",
    "## 底层：AI 执行引擎",
    "• OpenClaw AI 执行引擎（私有化部署）",
    "• 国产大模型（通义千问/Qwen/文心一言）"
])

# 8. MVP 功能
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_table_slide(slide, "📦 MVP 核心功能",
    ["模块", "核心技能", "解决痛点"],
    [
        ["家园智能助手", "• 自动生成周报/食谱\n• 24小时答疑\n• 个性化提醒", "解放80%沟通时间"],
        ["保教自动化", "• 自动生成教案\n• 观察笔记整理\n• 发展评估报告", "降低备课工作量"],
        ["后勤自动化", "• 自动排班考勤\n• 智能食谱\n• 账单自动生成", "简化行政流程"]
    ]
)

# 9. 产品迭代
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "📅 产品迭代路线", [
    "## 🚀 0-3 个月 MVP",
    "• 完成核心 3 个模块",
    "• 5 分钟一键部署",
    "• 对接微信/企业微信",
    "",
    "## 📈 3-6 个月 完善",
    "• 完善安全合规模块",
    "• 推出集团多园管理版",
    "• 优化技能库",
    "",
    "## 🌟 6-12 个月 生态",
    "• 上线家长端增值服务",
    "• 幼教技能商店",
    "• 开放 API 对接"
])

# 10. 商业模式
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "💰 四层递进变现体系", [
    "## 1️⃣ 基础层：B 端 SaaS 订阅",
    "• 标准版 2980 元/园/年",
    "• 专业版 5980 元/园/年",
    "• 集团版 29800 元/集团/年",
    "",
    "## 2️⃣ 增值层：高毛利服务",
    "• 部署实施费 1800-3600 元/园",
    "• 定制开发 5000-20000 元/个",
    "",
    "## 3️⃣ 生态层：B2B2C 变现",
    "• C端家长增值 30-98 元/月",
    "• 供应链分成 10%-30%",
    "",
    "## 4️⃣ 平台层：生态壁垒",
    "• 技能商店佣金 15%-30%"
])

# 11. 定价表格
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_table_slide(slide, "💎 SaaS 订阅版本定价",
    ["版本", "定价", "适配客群", "核心权益"],
    [
        ["标准版", "2980元\n园/年", "10-15班\n民营园", "核心3模块\n云托管"],
        ["专业版", "5980元\n园/年", "15-30班\n中高端园", "全模块\n私有化部署"],
        ["集团版", "29800元\n集团/年", "连锁幼教\n集团", "多园管理\n定制开发"]
    ]
)

# 12. 盈利测算
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_table_slide(slide, "📈 12 个月盈利测算",
    ["阶段", "园所", "订阅营收", "增值", "总营收", "目标"],
    [
        ["0-3月", "5家", "0", "0", "0", "验证价值"],
        ["3-6月", "50家", "20万", "5万", "25万", "月5万+"],
        ["6-12月", "200家", "100万", "40万", "140万", "单月盈利"]
    ]
)

# 13. 获客策略
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "🎣 获客策略", [
    "## 🌱 种子客户",
    "• 3-5 家区域头部民营园/连锁幼教集团",
    "• 免费试用 1-3 个月",
    "",
    "## 🤝 渠道合作",
    "• 幼教展会、园长社群、区域代理商",
    "• 20%-30% 佣金",
    "",
    "## 🎁 转化钩子",
    "•「免费试用 1 个月，无效全额退款」",
    "",
    "## 🏆 标杆打造",
    "• 3 个标杆案例，可复制 SOP"
])

# 14. 核心壁垒
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "🛡️ 四大核心壁垒", [
    "## 📚 行业 Know-How",
    "• 深度贴合幼教政策",
    "• 专属幼教技能库护城河",
    "",
    "## 🔐 数据合规",
    "• 本地私有化部署",
    "• 权限隔离与审计",
    "",
    "## ⚙️ 技术交付",
    "• 一键部署、零代码",
    "",
    "## 🌐 网络效应",
    "• 园所越多→越完善"
])

# 15. 风险应对
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_table_slide(slide, "⚠️ 风险与应对",
    ["风险", "具体风险", "应对方案"],
    [
        ["合规", "数据隐私\n政策监管", "本地部署\n提前备案"],
        ["竞争", "SaaS厂商\nAI巨头", "垂直细分\n差异化"],
        ["技术", "开源迭代\n模型适配", "社区迭代\n多模型兼容"],
        ["推广", "决策链长\n付费意愿", "免费试用\nROI测算"]
    ]
)

# 16. 融资计划
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_content_slide(slide, "💼 融资计划", [
    "## 天使轮",
    "• 融资金额：500-1000 万元",
    "• 出让股权：10%-15%",
    "",
    "## 资金用途",
    "• 🏗️ 产品研发 40%",
    "• 📢 市场拓展 35%",
    "• 👥 团队建设 20%",
    "• 🔧 运营储备 5%",
    "",
    "## 退出机制",
    "• 3-5 年实现行业并购或 IPO"
])

# 17. 结束页
slide = prs.slides.add_slide(prs.slide_layouts[6])
create_end_slide(slide, "携手共创幼教 AI 新未来", "让 AI 成为每位幼儿教师的得力助手")

# 保存
output = r"C:\Users\17699\.openclaw\workspace\OpenClaw_Kindergarten_Business_Plan_V3.pptx"
prs.save(output)
print(f"Ultra Premium PPT saved: {output}")
print(f"Total: {len(prs.slides)} pages")