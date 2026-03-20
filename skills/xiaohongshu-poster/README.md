# 🐱 小红书自动发布技能

> OpenClaw 技能 - 自动在小红书发布图文笔记

## 快速开始

### 1. 安装依赖

```bash
cd skills/xiaohongshu-poster
npm install
```

### 2. 运行（交互模式）

```bash
npm run interactive
```

或：

```bash
node scripts/post.js --interactive
```

### 3. 运行（命令行模式）

```bash
node scripts/post.js --title "我的标题" --content "正文内容" --images "image1.jpg,image2.jpg" --tags "#穿搭 #日常"
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--title` | 是 | 笔记标题 |
| `--content` | 是 | 笔记正文 |
| `--images` | 否 | 图片路径，逗号分隔 |
| `--tags` | 否 | 话题标签 |
| `--schedule` | 否 | 定时发布（开发中） |
| `--interactive` | 否 | 交互模式 |

## 首次使用

1. 运行 `npm run interactive`
2. 扫码登录小红书创作者平台
3. Cookies 会自动保存，下次无需重复登录

## 安全提示

⚠️ 请遵守小红书社区规范：
- 每天发布不超过 5 篇
- 图片需原创或已授权
- 避免敏感词汇
- 发布间隔建议 > 5 分钟

## 故障排除

**Q: 找不到 Chrome 浏览器**
- 安装 Google Chrome: https://www.google.com/chrome/

**Q: 登录失败**
- 删除 `cookies.json` 重新扫码
- 检查网络连接

**Q: 发布失败**
- 检查内容是否违规
- 图片格式是否为 JPG/PNG
- 图片大小不超过 10MB
