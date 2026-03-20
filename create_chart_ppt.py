# -*- coding: utf-8 -*-
"""
真正带图表的商业计划书 - 数据可视化
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
import os

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

IMG_DIR = r"C:\Users\17699\.openclaw\workspace\images"

COLORS = {
    'primary': RGBColor(26, 43, 74),
    'secondary': RGBColor(0, 90, 190),
    'accent': RGBColor(212, 175, 55),
    'white': RGBColor(255, 255, 255),
    'dark': RGBColor(45, 52, 69),
    'light': RGBColor(248, 250, 252),
    'success': RGBColor(39, 174, 96),
}

def add_bg(slide, img):
    img_path = os.path.join(IMG_DIR, img) if os.path.exists(os.path.join(IMG_DIR, img)) else None
    if img_path:
        pic = slide.shapes.add_picture(img_path, Inches(0), Inches(0), width=prs.slide_width)
        if pic.height < prs.slide_height:
            pic.top = int((prs.slide_height - pic.height) / 2)
    else:
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLORS['primary']
    
    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = COLORS['primary']
    overlay.fill.transparency = 0.5
    overlay.line.fill.background()

def add_header(slide, title):
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.fill.transparency = 0.85
    
    gold = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(1.15), prs.slide_width, Inches(0.05))
    gold.fill.solid()
    gold.fill.fore_color.rgb = COLORS['accent']
    
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.35), Inches(12), Inches(0.6))
    title_box.text_frame.paragraphs[0].text = title
    title_box.text_frame.paragraphs[0].font.size = Pt(34)
    title_box.text_frame.paragraphs[0].font.bold = True
    title_box.text_frame.paragraphs[0].font.color.rgb = COLORS['white']

# ============ 1. 封面 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "title_bg.jpg")

bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.1), prs.slide_height)
bar.fill.solid()
bar.fill.fore_color.rgb = COLORS['accent']

title = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.5))
p = title.text_frame.paragraphs[0]
p.text = "OpenClaw 幼儿园 AI 数字员工 SaaS"
p.font.size = Pt(48)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

sub = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(0.8))
p = sub.text_frame.paragraphs[0]
p.text = "商业计划书"
p.font.size = Pt(28)
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER

# ============ 2. 市场规模 - 柱状图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "tech.jpg")
add_header(slide, "📊 市场规模（数据可视化）")

# 添加柱状图
chart_data = CategoryChartData()
chart_data.categories = ['幼儿园数量', '民营园占比', '市场规模(百亿)', '年增速(%)']
chart_data.add_series('数据', (28, 60, 3, 15))

x, y, w, h = Inches(0.5), Inches(1.5), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, w, h, chart_data
).chart

chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM

# 右侧数据卡
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7), Inches(1.5), Inches(6), Inches(4.5))
card.fill.solid()
card.fill.fore_color.rgb = COLORS['white']
card.fill.transparency = 0.9
card.line.color.rgb = COLORS['accent']

txt = slide.shapes.add_textbox(Inches(7.3), Inches(1.8), Inches(5.5), Inches(3.5))
tf = txt.text_frame
p = tf.paragraphs[0]
p.text = "🚀 市场机会"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = COLORS['primary']

for item in ["• 国内幼儿园超 28 万所", "• 民营园占比超 60%", "• 市场规模超 300 亿元", "• 年复合增长率 15%+", "", "⚡ AI 渗透率不足 5%"]:
    p = tf.add_paragraph()
    p.text = item
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS['dark']

# ============ 3. 核心痛点 - 饼图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "business.jpg")
add_header(slide, "😫 教师工作时间分配（数据可视化）")

# 饼图数据
chart_data = CategoryChartData()
chart_data.categories = ['重复事务', '教学陪伴']
chart_data.add_series('时间', (80, 20))

x, y, w, h = Inches(0.5), Inches(1.5), Inches(5), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE, x, y, w, h, chart_data
).chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.RIGHT

# 痛点说明
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6), Inches(1.5), Inches(7), Inches(4.5))
card.fill.solid()
card.fill.fore_color.rgb = COLORS['white']
card.fill.transparency = 0.9

txt = slide.shapes.add_textbox(Inches(6.3), Inches(1.8), Inches(6.5), Inches(3.5))
tf = txt.text_frame
p = tf.paragraphs[0]
p.text = "💡 核心痛点"
p.font.size = Pt(24)
p.font.bold = True
p.font.color.rgb = COLORS['primary']

for item in ["80% 时间消耗在：", "• 周报撰写", "• 通知发布", "• 考勤统计", "• 家长答疑", "", "解决方案：AI 自动化"]:
    p = tf.add_paragraph()
    p.text = item
    p.font.size = Pt(16)
    p.font.color.rgb = COLORS['dark']

# ============ 4. 产品架构 - 层级图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "office.jpg")
add_header(slide, "🏗️ 产品架构")

# 三层架构可视化
# 上层
top = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(1.8), Inches(11.3), Inches(1.2))
top.fill.solid()
top.fill.fore_color.rgb = COLORS['accent']

txt = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11.3), Inches(0.8))
p = txt.text_frame.paragraphs[0]
p.text = "📱 交互端：微信/企业微信 + 园长后台 + 家长小程序"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 中层
mid = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(3.3), Inches(11.3), Inches(1.2))
mid.fill.solid()
mid.fill.fore_color.rgb = COLORS['secondary']

txt = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(11.3), Inches(0.8))
p = txt.text_frame.paragraphs[0]
p.text = "⚙️ 技能库：家园沟通 + 保教管理 + 行政后勤 + 安全合规"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 底层
bot = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1), Inches(4.8), Inches(11.3), Inches(1.2))
bot.fill.solid()
bot.fill.fore_color.rgb = COLORS['primary']

txt = slide.shapes.add_textbox(Inches(1), Inches(5), Inches(11.3), Inches(0.8))
p = txt.text_frame.paragraphs[0]
p.text = "🔧 引擎：OpenClaw + 国产大模型（通义千问/Qwen/文心一言）"
p.font.size = Pt(18)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# ============ 5. MVP功能 - 图表 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "tech.jpg")
add_header(slide, "📦 MVP 核心功能")

# 环形图 - 效率提升
chart_data = CategoryChartData()
chart_data.categories = ['AI完成', '人工处理']
chart_data.add_series('效率', (80, 20))

x, y, w, h = Inches(0.5), Inches(1.5), Inches(4), Inches(4)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.DOUGHNUT, x, y, w, h, chart_data
).chart

txt = slide.shapes.add_textbox(Inches(0.5), Inches(5.2), Inches(4), Inches(0.5))
p = txt.text_frame.paragraphs[0]
p.text = "AI 提升效率 80%"
p.font.size = Pt(14)
p.font.bold = True
p.alignment = PP_ALIGN.CENTER

# 功能列表
features = [
    ("🏠 家园智能助手", "周报/食谱/考勤 自动生成"),
    ("📚 保教自动化", "教案/活动方案/评估报告"),
    ("🍽️ 后勤自动化", "排班/食谱/采购/账单")
]

for i, (title, desc) in enumerate(features):
    x = 5 + i * 2.8
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.8), Inches(2.6), Inches(2.2))
    card.fill.solid()
    card.fill.fore_color.rgb = COLORS['white']
    card.fill.transparency = 0.85
    card.line.color.rgb = COLORS['accent']
    
    txt = slide.shapes.add_textbox(Inches(x+0.15), Inches(2), Inches(2.3), Inches(1.5))
    p = txt.text_frame.paragraphs[0]
    p.text = f"{title}\n\n{desc}"
    p.font.size = Pt(14)
    p.font.color.rgb = COLORS['dark']
    p.alignment = PP_ALIGN.CENTER

# ============ 6. 产品迭代 - 时间线图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "gradient_dark_blue.jpg")
add_header(slide, "📅 产品迭代路线")

phases = [
    ("0-3月", "MVP", ["核心3模块", "5分钟部署", "5家种子园"]),
    ("3-6月", "完善", ["安全合规", "集团版", "50家园所"]),
    ("6-12月", "生态", ["家长增值", "技能商店", "200家园所"])
]

colors = [COLORS['accent'], COLORS['secondary'], COLORS['success']]

for i, (phase, title, items) in enumerate(phases):
    x = 0.8 + i * 4.3
    
    # 圆点
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(3), Inches(0.7), Inches(0.7))
    circle.fill.solid()
    circle.fill.fore_color.rgb = colors[i]
    circle.line.color.rgb = COLORS['white']
    circle.line.width = Pt(2)
    
    # 连接线
    if i < 2:
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x+0.7), Inches(3.3), Inches(3.3), Inches(0.1))
        line.fill.solid()
        line.fill.fore_color.rgb = COLORS['accent']
    
    # 标题
    txt = slide.shapes.add_textbox(Inches(x), Inches(3.9), Inches(2.5), Inches(0.5))
    p = txt.text_frame.paragraphs[0]
    p.text = f"{phase}\n{title}"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = colors[i]
    p.alignment = PP_ALIGN.CENTER
    
    # 内容
    txt = slide.shapes.add_textbox(Inches(x), Inches(4.5), Inches(2.5), Inches(2))
    tf = txt.text_frame
    for item in items:
        p = tf.add_paragraph()
        p.text = f"• {item}"
        p.font.size = Pt(12)
        p.font.color.rgb = COLORS['white']
        p.alignment = PP_ALIGN.CENTER

# ============ 7. 商业模式 - 漏斗图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "business.jpg")
add_header(slide, "💰 商业模式（四层变现）")

models = [
    ("💳 基础层：B端SaaS", "2980-29800元/园/年", COLORS['primary']),
    ("🔧 增值层：服务", "1800-20000元/次", COLORS['secondary']),
    ("🌐 生态层：B2B2C", "30-98元/月", COLORS['accent']),
    ("🏛️ 平台层：生态", "15-30% 佣金", COLORS['success'])
]

for i, (title, price, color) in enumerate(models):
    w = 12 - i * 0.5
    x = 0.25 + i * 0.25
    
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.8), Inches(w), Inches(1))
    card.fill.solid()
    card.fill.fore_color.rgb = color
    
    txt = slide.shapes.add_textbox(Inches(x+0.3), Inches(2), Inches(w-0.6), Inches(0.6))
    p = txt.text_frame.paragraphs[0]
    p.text = f"{title}\n{price}"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER

# ============ 8. 盈利测算 - 表格+图 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "office.jpg")
add_header(slide, "📈 盈利测算")

# 表格
table = slide.shapes.add_table(4, 5, Inches(0.5), Inches(1.5), Inches(12.3), Inches(4)).table
headers = ["阶段", "园所", "订阅营收", "增值服务", "总营收"]
for i, h in enumerate(headers):
    cell = table.cell(0, i)
    cell.text = h
    cell.fill.solid()
    cell.fill.fore_color.rgb = COLORS['primary']
    cell.text_frame.paragraphs[0].font.color.rgb = COLORS['white']
    cell.text_frame.paragraphs[0].font.bold = True

data = [
    ["0-3月", "5家", "0", "0", "0"],
    ["3-6月", "50家", "20万", "5万", "25万"],
    ["6-12月", "200家", "100万", "40万", "140万"]
]
for r, row in enumerate(data, 1):
    for c, v in enumerate(row):
        cell = table.cell(r, c)
        cell.text = v
        cell.fill.solid()
        cell.fill.fore_color.rgb = COLORS['white'] if r % 2 == 0 else COLORS['light']
        cell.text_frame.paragraphs[0].font.color.rgb = COLORS['dark']

# ============ 9. 融资计划 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "gradient_dark_blue.jpg")
add_header(slide, "💼 融资计划")

# 融资金额大卡片
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2), Inches(2), Inches(9.3), Inches(2))
card.fill.solid()
card.fill.fore_color.rgb = COLORS['primary']

txt = slide.shapes.add_textbox(Inches(2.5), Inches(2.5), Inches(8.5), Inches(1.5))
p = txt.text_frame.paragraphs[0]
p.text = "500-1000万 天使轮"
p.font.size = Pt(40)
p.font.bold = True
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER
p = txt.text_frame.add_paragraph()
p.text = "出让 10%-15% 股权"
p.font.size = Pt(20)
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

# 资金用途饼图
chart_data = CategoryChartData()
chart_data.categories = ['产品研发', '市场拓展', '团队建设', '运营储备']
chart_data.add_series('资金', (40, 35, 20, 5))

chart = slide.shapes.add_chart(
    XL_CHART_TYPE.PIE, Inches(4), Inches(4.3), Inches(5.3), Inches(3), chart_data
).chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM

# ============ 10. 结束页 ============
slide = prs.slides.add_slide(prs.slide_layouts[6])
add_bg(slide, "gradient_dark_blue.jpg")

circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(5.3), Inches(2), Inches(2.7), Inches(2.7))
circle.fill.solid()
circle.fill.fore_color.rgb = COLORS['accent']
circle.transparency = 0.5

txt = slide.shapes.add_textbox(Inches(1), Inches(4.2), Inches(11), Inches(1))
p = txt.text_frame.paragraphs[0]
p.text = "携手共创幼教 AI 新未来"
p.font.size = Pt(38)
p.font.bold = True
p.font.color.rgb = COLORS['white']
p.alignment = PP_ALIGN.CENTER

txt = slide.shapes.add_textbox(Inches(1), Inches(5.2), Inches(11), Inches(0.6))
p = txt.text_frame.paragraphs[0]
p.text = "让 AI 成为每位幼儿教师的得力助手"
p.font.size = Pt(20)
p.font.color.rgb = COLORS['accent']
p.alignment = PP_ALIGN.CENTER

# 保存
output = r"C:\Users\17699\.openclaw\workspace\商业计划书_图表版.pptx"
prs.save(output)
print(f"Chart PPT saved: {output}")
print(f"Pages: {len(prs.slides)}")