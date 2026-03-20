/**
 * 小红书自动发布脚本
 * 使用 Playwright 进行网页自动化
 */

const { chromium } = require('playwright');
const { execSync } = require('child_process');

// 查找系统 Chrome 路径
function findChromePath() {
  const paths = [
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    process.env['PROGRAMFILES'] + '\\Google\\Chrome\\Application\\chrome.exe',
    process.env['PROGRAMFILES(X86)'] + '\\Google\\Chrome\\Application\\chrome.exe'
  ];
  
  for (const p of paths) {
    try {
      execSync(`where "${p}"`, { stdio: 'ignore' });
      return p;
    } catch (e) {
      continue;
    }
  }
  return null;
}

// 启动浏览器
async function launchBrowser() {
  const chromePath = findChromePath();
  return await chromium.launch({
    headless: false,
    executablePath: chromePath || undefined,
    args: chromePath ? [] : ['--no-sandbox']
  });
}
const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CONFIG_PATH = path.join(__dirname, '..', 'config.json');
const COOKIES_PATH = path.join(__dirname, '..', 'cookies.json');
const XHS_URL = 'https://creator.xiaohongshu.com';

// 命令行参数解析
const args = process.argv.slice(2);
const argMap = {};
args.forEach((arg, i) => {
  if (arg.startsWith('--')) {
    const key = arg.slice(2);
    const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
    argMap[key] = value;
  }
});

// 配置加载
function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
  }
  return {
    account: { name: '默认账号', cookiePath: COOKIES_PATH },
    defaults: { addTags: true, confirmBeforePost: true }
  };
}

// 交互式输入
function askQuestion(query) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise(resolve => rl.question(query, answer => {
    rl.close();
    resolve(answer);
  }));
}

// 加载 Cookies
async function loadCookies(page) {
  if (fs.existsSync(COOKIES_PATH)) {
    const cookies = JSON.parse(fs.readFileSync(COOKIES_PATH, 'utf-8'));
    await page.context().addCookies(cookies);
    console.log('✅ Cookies 已加载');
    return true;
  }
  return false;
}

// 保存 Cookies
async function saveCookies(page) {
  const cookies = await page.context().cookies();
  fs.writeFileSync(COOKIES_PATH, JSON.stringify(cookies, null, 2));
  console.log('✅ Cookies 已保存');
}

// 登录
async function login(page) {
  console.log('📱 请访问小红书创作者平台扫码登录...');
  await page.goto(XHS_URL, { waitUntil: 'networkidle' });
  
  // 等待登录完成（检测是否出现发布按钮）
  console.log('⏳ 等待登录完成（最长 60 秒）...');
  try {
    await page.waitForSelector('button:has-text("发布笔记")', { timeout: 60000 });
    console.log('✅ 登录成功！');
    await saveCookies(page);
    return true;
  } catch (e) {
    console.log('❌ 登录超时，请重试');
    return false;
  }
}

// 发布笔记
async function publishNote(page, title, content, images, tags) {
  console.log('\n📝 开始发布笔记...');
  console.log(`标题：${title}`);
  console.log(`内容：${content.substring(0, 50)}${content.length > 50 ? '...' : ''}`);
  console.log(`图片：${images.length} 张`);
  console.log(`标签：${tags || '无'}`);
  
  // 点击发布按钮
  const publishBtn = await page.$('button:has-text("发布笔记")');
  if (!publishBtn) {
    console.log('❌ 未找到发布按钮，可能未登录');
    return false;
  }
  await publishBtn.click();
  await page.waitForTimeout(1000);
  
  // 填写标题
  const titleInput = await page.$('input[placeholder="填写标题会有更多赞哦~"]');
  if (titleInput) {
    await titleInput.fill(title);
    console.log('✅ 标题已填写');
  }
  
  // 上传图片
  if (images.length > 0) {
    const fileInput = await page.$('input[type="file"]');
    if (fileInput) {
      await fileInput.setInputFiles(images);
      console.log('✅ 图片已上传');
      await page.waitForTimeout(3000); // 等待上传完成
    }
  }
  
  // 填写内容
  const contentEditor = await page.$('.editor-content textarea, [contenteditable="true"]');
  if (contentEditor) {
    await contentEditor.fill(content);
    console.log('✅ 内容已填写');
  }
  
  // 添加标签
  if (tags) {
    const tagInput = await page.$('input[placeholder="@好友 #话题"]');
    if (tagInput) {
      await tagInput.fill(tags);
      await page.keyboard.press('Enter');
      console.log('✅ 标签已添加');
    }
  }
  
  // 预览确认
  console.log('\n⚠️  发布前预览：');
  console.log('─────────────────');
  console.log(`【标题】${title}`);
  console.log(`【内容】${content}`);
  console.log(`【标签】${tags || '无'}`);
  console.log('─────────────────');
  
  const confirm = await askQuestion('\n确认发布？(y/n): ');
  if (confirm.toLowerCase() !== 'y') {
    console.log('❌ 已取消发布');
    return false;
  }
  
  // 点击发布
  const submitBtn = await page.$('button:has-text("发布")');
  if (submitBtn) {
    await submitBtn.click();
    await page.waitForTimeout(3000);
    console.log('✅ 发布成功！');
    return true;
  } else {
    console.log('❌ 未找到发布按钮');
    return false;
  }
}

// 主函数
async function main() {
  const config = loadConfig();
  
  // 交互模式
  if (argMap.interactive) {
    console.log('🐱 小红书发布助手 - 交互模式\n');
    
    const title = await askQuestion('请输入标题：');
    const content = await askQuestion('请输入内容：');
    const imagesStr = await askQuestion('图片路径（逗号分隔，留空跳过）：');
    const tags = await askQuestion('话题标签（可选）：');
    
    const images = imagesStr ? imagesStr.split(',').map(p => path.resolve(p.trim())) : [];
    
    const browser = await launchBrowser();
    const page = await browser.newPage();
    
    const hasCookies = await loadCookies(page);
    if (!hasCookies) {
      const logged = await login(page);
      if (!logged) {
        await browser.close();
        return;
      }
    }
    
    await publishNote(page, title, content, images, tags);
    await browser.close();
    return;
  }
  
  // 命令行模式
  const title = argMap.title;
  const content = argMap.content;
  const imagesStr = argMap.images;
  const tags = argMap.tags;
  const schedule = argMap.schedule;
  
  if (!title || !content) {
    console.log('❌ 缺少必要参数');
    console.log('用法：node post.js --title "标题" --content "内容" --images "img1.jpg,img2.jpg" [--tags "#标签"]');
    console.log('或：node post.js --interactive');
    return;
  }
  
  const images = imagesStr ? imagesStr.split(',').map(p => path.resolve(p.trim())) : [];
  
  const browser = await launchBrowser();
  const page = await browser.newPage();
  
  const hasCookies = await loadCookies(page);
  if (!hasCookies) {
    const logged = await login(page);
    if (!logged) {
      await browser.close();
      return;
    }
  }
  
  if (schedule) {
    console.log(`⏰ 定时发布：${schedule}`);
    // TODO: 实现定时发布逻辑
    console.log('⚠️  定时发布功能开发中，将立即发布...');
  }
  
  await publishNote(page, title, content, images, tags);
  await browser.close();
}

main().catch(console.error);
