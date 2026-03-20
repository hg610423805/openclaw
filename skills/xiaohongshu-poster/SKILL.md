# 小红书自动发布技能 (xiaohongshu-poster)

## 功能

自动在小红书发布图文笔记，支持：
- 标题 + 正文内容
- 多张图片上传（最多 9 张）
- 话题标签自动添加
- 定时发布（可选）
- 发布前预览确认

## 依赖

- Node.js 18+
- Playwright (自动安装)
- 小红书账号（需扫码登录）

## 安装

```bash
cd skills/xiaohongshu-poster
npm install
npx playwright install chromium
```

## 配置

编辑 `config.json`：

```json
{
  "account": {
    "name": "默认账号",
    "cookiePath": "./cookies.json"
  },
  "defaults": {
    "addTags": true,
    "confirmBeforePost": true
  }
}
```

## 使用方法

### 基础发布

```bash
node scripts/post.js --title "标题" --content "正文内容" --images "img1.jpg,img2.jpg"
```

### 带话题标签

```bash
node scripts/post.js --title "标题" --content "正文" --images "img1.jpg" --tags "#穿搭 #日常 #OOTD"
```

### 定时发布

```bash
node scripts/post.js --title "标题" --content "正文" --images "img1.jpg" --schedule "2024-01-01 18:00"
```

### 交互式发布（推荐新手）

```bash
node scripts/post.js --interactive
```

## 安全说明

- 首次运行需扫码登录，cookies 保存在本地
- 发布前会显示预览，需确认后才发布
- 不会自动点赞/评论/关注（避免风控）
- 建议发布间隔 > 5 分钟

## 注意事项

⚠️ 小红书风控严格，请遵守：
- 每天发布不超过 5 篇
- 图片需原创或已授权
- 避免敏感词汇
- 新号建议手动养号 1 周再用

## 故障排除

**Q: 登录失败/二维码不显示**
- 检查网络连接
- 删除 `cookies.json` 重新扫码

**Q: 发布失败**
- 检查内容是否违规
- 图片格式是否为 JPG/PNG
- 图片大小不超过 10MB

**Q: 被风控限流**
- 暂停发布 24-48 小时
- 降低发布频率
- 增加互动行为（手动）
