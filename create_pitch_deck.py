# -*- coding: utf-8 -*-
"""
OpenClaw 幼儿园 AI 数字员工 SaaS 商业计划书 PPT 生成器
16:9 页面比例，专业设计风格
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Cm
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# 创建演示文稿 - 16:9 比例
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 品牌配色方案
COLORS = {
    'primary': RGBColor(0x25, 0x63, 0xEB),      # 深蓝 - 专业信任
    'secondary': RGBColor(0x10, 0xB9, 0x81),    # 绿色 - 成长希望
    'accent': RGBColor(0xF5, 0x9E, 0x0B),       # 橙色 - 活力创新
    'dark': RGBColor(0x1F, 0x29, 0x37),         # 深灰 - 文字
    'light': RGBColor(0xF3, 0xF4, 0xF6),        # 浅灰 - 背景
    'white': RGBColor(0xFF, 0xFF, 0xFF),
}

def create_title_slide(prs, title, subtitle):
    """创建标题页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 空白版式
    
    # 背景渐变效果（用矩形色块模拟）
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['primary']
    bg.line.fill.background()
    
    # 装饰元素
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10), Inches(0.5), Inches(2), Inches(2))
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['secondary']
    circle.line.fill.background()
    circle.transparency = 0.7
    
    circle2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(11), Inches(5), Inches(1.5), Inches(1.5))
    circle2.fill.solid()
    circle2.fill.fore_color.rgb = COLORS['accent']
    circle2.line.fill.background()
    circle2.transparency = 0.6
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(10), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(10), Inches(1))
    tf = subtitle_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(24)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    p.font.transparency = 0.2
    
    return slide

def create_section_slide(prs, section_num, section_title, icon="📊"):
    """创建章节页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 左侧色块
    left_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(4), prs.slide_height)
    left_bar.fill.solid()
    left_bar.fill.fore_color.rgb = COLORS['primary']
    left_bar.line.fill.background()
    
    # 章节号
    num_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(3), Inches(1.5))
    tf = num_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"{section_num}"
    p.font.size = Pt(72)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    p.font.transparency = 0.8
    
    # 章节标题
    title_box = slide.shapes.add_textbox(Inches(5), Inches(2.5), Inches(7), Inches(2))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"{icon} {section_title}"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = COLORS['dark']
    
    return slide

def create_content_slide(prs, title, content_items, notes=None):
    """创建内容页 - 支持列表"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 内容区域
    content_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.2), Inches(12), Inches(5.5))
    tf = content_box.text_frame
    tf.word_wrap = True
    
    for i, item in enumerate(content_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(18)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(12)
        if item.startswith("•"):
            p.font.size = Pt(18)
    
    return slide

def create_two_column_slide(prs, title, left_title, left_items, right_title, right_items):
    """创建双栏内容页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 左栏标题
    left_title_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.2), Inches(5.5), Inches(0.5))
    tf = left_title_box.text_frame
    p = tf.paragraphs[0]
    p.text = left_title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['primary']
    
    # 左栏内容
    left_box = slide.shapes.add_textbox(Inches(0.7), Inches(1.7), Inches(5.5), Inches(5))
    tf = left_box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(left_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(8)
    
    # 右栏标题
    right_title_box = slide.shapes.add_textbox(Inches(7), Inches(1.2), Inches(5.5), Inches(0.5))
    tf = right_title_box.text_frame
    p = tf.paragraphs[0]
    p.text = right_title
    p.font.size = Pt(20)
    p.font.bold = True
    p.font.color.rgb = COLORS['secondary']
    
    # 右栏内容
    right_box = slide.shapes.add_textbox(Inches(7), Inches(1.7), Inches(5.5), Inches(5))
    tf = right_box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(right_items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(16)
        p.font.color.rgb = COLORS['dark']
        p.space_after = Pt(8)
    
    return slide

def create_table_slide(prs, title, headers, rows, highlight_row=None):
    """创建表格页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 创建表格
    table_rows = len(rows) + 1
    table_cols = len(headers)
    
    table = slide.shapes.add_table(table_rows, table_cols, Inches(0.5), Inches(1.2), Inches(12.3), Inches(5.5)).table
    
    # 设置列宽
    col_widths = [Inches(3), Inches(3), Inches(3), Inches(3.3)]
    for i, width in enumerate(col_widths[:table_cols]):
        table.columns[i].width = width
    
    # 填充表头
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
    
    # 填充数据行
    for row_idx, row_data in enumerate(rows, 1):
        for col_idx, cell_data in enumerate(row_data[:table_cols]):
            cell = table.cell(row_idx, col_idx)
            cell.text = str(cell_data)
            
            # 高亮行
            if highlight_row and row_idx == highlight_row:
                cell.fill.solid()
                cell.fill.fore_color.rgb = COLORS['light']
            
            tf = cell.text_frame
            tf.paragraphs[0].font.size = Pt(12)
            tf.paragraphs[0].font.color.rgb = COLORS['dark']
            tf.paragraphs[0].alignment = PP_ALIGN.CENTER
            tf.word_wrap = True
    
    return slide

def create_timeline_slide(prs, title, phases):
    """创建时间线页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 顶部标题栏
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.8))
    header.fill.solid()
    header.fill.fore_color.rgb = COLORS['primary']
    header.line.fill.background()
    
    # 标题
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    
    # 时间线
    colors = [COLORS['primary'], COLORS['secondary'], COLORS['accent']]
    start_x = Inches(1)
    circle_y = Inches(3)
    box_y = Inches(4.2)
    
    for i, phase in enumerate(phases):
        x = start_x + i * Inches(4)
        
        # 圆圈
        circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, circle_y, Inches(1), Inches(1))
        circle.fill.solid()
        circle.fill.fore_color.rgb = colors[i % len(colors)]
        circle.line.fill.background()
        
        # 连接线
        if i < len(phases) - 1:
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(1), circle_y + Inches(0.45), Inches(3), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS['dark']
            line.line.fill.background()
            line.transparency = 0.5
        
        # 阶段标题
        title_box = slide.shapes.add_textbox(x, box_y, Inches(3.5), Inches(0.5))
        tf = title_box.text_frame
        p = tf.paragraphs[0]
        p.text = phase['title']
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = colors[i % len(colors)]
        p.alignment = PP_ALIGN.CENTER
        
        # 阶段内容
        content_box = slide.shapes.add_textbox(x, box_y + Inches(0.5), Inches(3.5), Inches(2.5))
        tf = content_box.text_frame
        tf.word_wrap = True
        for j, item in enumerate(phase['items']):
            if j == 0:
                p = tf.paragraphs[0]
            else:
                p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(12)
            p.font.color.rgb = COLORS['dark']
            p.alignment = PP_ALIGN.CENTER
    
    return slide

def create_end_slide(prs, title, subtitle, contact=None):
    """创建结束页"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # 背景
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLORS['primary']
    bg.line.fill.background()
    
    # 装饰
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(2), Inches(1), Inches(3), Inches(3))
    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS['secondary']
    circle.line.fill.background()
    circle.transparency = 0.8
    
    # 主标题
    title_box = slide.shapes.add_textbox(Inches(1), Inches(2.5), Inches(11), Inches(1.5))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    
    # 副标题
    subtitle_box = slide.shapes.add_textbox(Inches(1), Inches(4), Inches(11), Inches(1))
    tf = subtitle_box.text_frame
    p = tf.paragraphs[0]
    p.text = subtitle
    p.font.size = Pt(24)
    p.font.color.rgb = COLORS['white']
    p.alignment = PP_ALIGN.CENTER
    p.font.transparency = 0.2
    
    return slide

# ============ 创建 PPT 内容 ============

# 1. 封面
create_title_slide(
    prs,
    "OpenClaw 幼儿园 AI 数字员工 SaaS",
    "商业计划书 · 精简落地版"
)

# 2. 目录
create_content_slide(
    prs,
    "📋 目录",
    [
        "01 项目核心定位",
        "02 市场与痛点分析",
        "03 产品与 MVP 方案",
        "04 商业模式与盈利测算",
        "05 获客与落地执行计划",
        "06 团队与核心壁垒",
        "07 风险与应对策略",
        "08 融资计划"
    ]
)

# 3. 项目核心定位
create_content_slide(
    prs,
    "🎯 项目核心定位",
    [
        "核心愿景：打造国内首款面向幼儿园的私有化部署 AI 数字员工 SaaS",
        "",
        "四大核心痛点解决：",
        "• 教师重复劳动多 → AI 自动化替代",
        "• 家园沟通低效 → 智能沟通助手",
        "• 数据安全合规难 → 本地私有化部署",
        "• 管理流程不规范 → 标准化 AI 流程",
        "",
        "价值主张：用 AI 自动化实现保教、家园、行政、后勤全流程提效"
    ]
)

# 4. 市场规模
create_two_column_slide(
    prs,
    "📊 市场规模与机会",
    "市场容量",
    [
        "• 国内幼儿园超 28 万所",
        "• 民营园占比超 60%",
        "• 幼教信息化市场规模超 300 亿元",
        "• 年复合增长率 15%+",
        "",
        "AI 渗透率不足 5%",
        "存在巨大市场空白"
    ],
    "传统 SaaS 局限",
    [
        "• 仅停留在信息管理层面",
        "• 无法自动执行任务",
        "• 数据上公云，合规风险高",
        "• 无法真正减轻教师负担",
        "",
        "我们的机会：",
        "AI 自动化 + 私有化部署"
    ]
)

# 5. 核心痛点
create_content_slide(
    prs,
    "😫 行业核心痛点",
    [
        "教师端：",
        "• 80% 工作时间消耗在周报、通知、考勤、家长答疑等重复事务",
        "• 教学陪伴时间被严重挤压",
        "",
        "园长端：",
        "• 多园管理难、数据不互通",
        "• 合规审计压力大、家园满意度难提升",
        "",
        "家长端：",
        "• 信息获取不及时、个性化需求难满足",
        "• 园所透明度低",
        "",
        "行业端：",
        "• 传统 SaaS 数据上公云，幼儿隐私数据存在合规风险"
    ]
)

# 6. 差异化优势
create_content_slide(
    prs,
    "🚀 三大差异化优势",
    [
        "🔒 技术壁垒",
        "• OpenClaw 开源引擎 + 国产大模型适配",
        "• 支持本地私有化部署，数据不出园",
        "• 完全符合教育数据合规要求",
        "",
        "⚡ 功能壁垒",
        "• 区别于传统 SaaS 的信息录入",
        "• 实现「自然语言指令→自动执行」",
        "• 真正替代人工完成重复工作",
        "",
        "🎁 交付壁垒",
        "• 5 分钟一键部署",
        "• 零代码操作",
        "• 园长/老师无需技术基础即可使用"
    ]
)

# 7. 产品架构
create_content_slide(
    prs,
    "🏗️ 核心产品架构",
    [
        "上层：交互端",
        "• 微信/企业微信原生交互端",
        "• 园长管理后台",
        "• 家长端小程序",
        "",
        "中层：幼教专属技能库",
        "• 家园沟通模块",
        "• 保教管理模块",
        "• 行政后勤模块",
        "• 安全合规模块",
        "",
        "底层：AI 执行引擎",
        "• OpenClaw AI 执行引擎（私有化部署）",
        "• 国产大模型（通义千问/Qwen/文心一言）"
    ]
)

# 8. MVP 核心功能表格
create_table_slide(
    prs,
    "📦 MVP 核心功能（0-3 个月落地）",
    ["模块", "核心技能", "解决痛点"],
    [
        ["家园智能助手", "• 自动生成周报/食谱/考勤/缴费提醒\n• 24 小时家长问题自动答疑\n• 特殊体质幼儿个性化提醒", "解放老师 80% 家园沟通时间"],
        ["保教自动化", "• 自动生成教案、活动方案\n• 自动整理观察笔记\n• 幼儿发展评估报告", "降低备课、评估工作量"],
        ["后勤自动化", "• 自动排班、考勤统计\n• 智能食谱 + 采购清单\n• 费用账单自动生成", "简化行政流程，减少出错"]
    ]
)

# 9. 产品迭代路线
create_timeline_slide(
    prs,
    "📅 产品迭代路线",
    [
        {
            "title": "0-3 个月 MVP",
            "items": ["完成核心 3 个模块", "5 分钟一键部署", "对接微信/企业微信"]
        },
        {
            "title": "3-6 个月 完善",
            "items": ["完善安全合规模块", "推出集团多园管理版", "优化技能库"]
        },
        {
            "title": "6-12 个月 生态",
            "items": ["上线家长端增值服务", "幼教技能商店", "开放 API 对接"]
        }
    ]
)

# 10. 商业模式 - 四层变现
create_content_slide(
    prs,
    "💰 四层递进变现体系",
    [
        "1️⃣ 基础层：B 端 SaaS 订阅（核心现金流）",
        "• 标准版 2980 元/园/年 | 专业版 5980 元/园/年 | 集团版 29800 元/集团/年",
        "",
        "2️⃣ 增值层：高毛利服务",
        "• 部署实施费 1800-3600 元/园 | 定制开发 5000-20000 元/个",
        "• 年度运维 800 元/园/年",
        "",
        "3️⃣ 生态层：B2B2C 增值变现",
        "• C 端家长增值 30-98 元/月 | 供应链分成 10%-30%",
        "",
        "4️⃣ 平台层：生态壁垒变现",
        "• 技能商店佣金 15%-30% | 认证培训 980-2980 元/人 | 引擎授权"
    ]
)

# 11. 版本定价表格
create_table_slide(
    prs,
    "💎 SaaS 订阅版本定价",
    ["版本", "定价", "适配客群", "核心权益"],
    [
        ["标准版", "2980 元/园/年", "10-15 班民营园", "核心 3 模块基础功能\n云托管部署"],
        ["专业版", "5980 元/园/年", "15-30 班中高端园", "全模块功能\n本地私有化部署\n无限技能调用"],
        ["集团版", "29800 元/集团/年", "连锁幼教集团", "多园统一管理\n定制化开发\n7×24 小时支持"]
    ]
)

# 12. 盈利测算
create_table_slide(
    prs,
    "📈 12 个月盈利测算",
    ["阶段", "园所数量", "年订阅营收", "增值服务营收", "总营收", "核心目标"],
    [
        ["0-3 个月", "5 家种子园", "0（免费试用）", "0", "0", "验证产品价值"],
        ["3-6 个月", "50 家园所", "20 万", "5 万", "25 万", "月营收 5 万+"],
        ["6-12 个月", "200 家园所", "100 万", "40 万", "140 万", "单月盈利"]
    ],
    highlight_row=3
)

# 13. 获客策略
create_content_slide(
    prs,
    "🎣 获客策略（低成本起量）",
    [
        "🌱 种子客户",
        "• 3-5 家区域头部民营园/连锁幼教集团",
        "• 免费试用 1-3 个月，换取深度反馈与案例背书",
        "",
        "🤝 渠道合作",
        "• 幼教展会、园长社群、区域代理商、行业媒体",
        "• 按成交金额支付 20%-30% 佣金",
        "",
        "🎁 转化钩子",
        "•「免费试用 1 个月，教师工作时间减少 50%，无效全额退款」",
        "",
        "🏆 标杆打造",
        "• 打造 3 个标杆案例（单园、连锁园、区域集团）",
        "• 形成可复制的落地 SOP"
    ]
)

# 14. 执行路线图
create_timeline_slide(
    prs,
    "🗺️ 12 个月落地执行路线",
    [
        {
            "title": "阶段 1: 0-3 个月",
            "items": ["MVP 验证期", "完成核心 3 模块", "签约 5 家种子园", "验证核心价值"]
        },
        {
            "title": "阶段 2: 3-6 个月",
            "items": ["规模化复制期", "团队扩充至 8 人", "签约 50 家园所", "月营收 5 万+"]
        },
        {
            "title": "阶段 3: 6-12 个月",
            "items": ["生态扩张期", "团队扩充至 15 人", "签约 200 家园所", "启动天使轮融资"]
        }
    ]
)

# 15. 核心壁垒
create_content_slide(
    prs,
    "🛡️ 四大核心壁垒",
    [
        "📚 行业 Know-How 壁垒",
        "• 深度贴合幼教政策、《3-6 岁儿童学习与发展指南》",
        "• 沉淀专属幼教技能库，形成行业护城河",
        "",
        "🔐 数据合规壁垒",
        "• 本地私有化部署，数据不出园",
        "• 权限隔离与审计日志，满足教育数据监管",
        "",
        "⚙️ 技术交付壁垒",
        "• 一键部署、零代码操作体系",
        "• 大幅降低落地门槛",
        "",
        "🌐 网络效应壁垒",
        "• 园所越多→家长越多→供应链越丰富→技能库越完善",
        "• 形成正向循环"
    ]
)

# 16. 风险与应对
create_table_slide(
    prs,
    "⚠️ 风险与应对策略",
    ["风险类型", "具体风险", "应对方案"],
    [
        ["合规风险", "幼儿数据隐私合规\n教育信息化政策监管", "本地部署 + 数据不出园\n提前对接教育部门备案\n完善权限隔离与审计"],
        ["竞争风险", "传统 SaaS 厂商\nAI 巨头入局", "聚焦垂直细分\n私有化部署差异化\n快速抢占标杆客户"],
        ["技术风险", "开源迭代\n模型适配问题", "深度参与社区迭代\n兼容多款国产大模型\n完善测试运维体系"],
        ["推广风险", "园长决策链长\n付费意愿低", "免费试用+ROI 测算\n聚焦中高端民营园\n与代理商合作"]
    ]
)

# 17. 融资计划
create_content_slide(
    prs,
    "💼 融资计划",
    [
        "融资轮次：天使轮",
        "融资金额：500-1000 万元",
        "出让股权：10%-15%",
        "",
        "资金用途：",
        "• 产品研发 40% - 完善技能库、生态平台、API 对接",
        "• 市场拓展 35% - 渠道建设、标杆案例、品牌推广",
        "• 团队建设 20% - 扩充研发、销售、运营团队",
        "• 运营储备 5% - 客户成功、运维服务",
        "",
        "退出机制：",
        "• 3-5 年实现幼教垂直 AI 平台头部地位",
        "• 寻求行业并购或 IPO 退出"
    ]
)

# 18. 结束页
create_end_slide(
    prs,
    "携手共创幼教 AI 新未来",
    "让 AI 成为每位幼儿教师的得力助手"
)

# 保存 PPT
output_path = r"C:\Users\17699\.openclaw\workspace\OpenClaw 幼儿园 AI 数字员工商业计划书.pptx"
prs.save(output_path)
print(f"PPT 已生成：{output_path}")
print(f"共 {len(prs.slides)} 页")
