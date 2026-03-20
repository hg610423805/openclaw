/**
 * 交易记录分析脚本
 * 解析 summary.txt，生成月度盈利分析和 H5 可视化页面
 */

const fs = require('fs');
const path = require('path');

// 读取文件，跳过 BOM
let rawData = fs.readFileSync('C:/Users/17699/.openclaw/workspace/summary.txt', 'utf-8');
if (rawData.charCodeAt(0) === 0xFEFF) {
  rawData = rawData.slice(1);
}

console.log('📊 开始分析交易数据...');

// 解析交易明细
function parseTrades(text) {
  const trades = [];
  const lines = text.split(/\r?\n/);
  
  for (const line of lines) {
    // 使用 [0-9] 代替 \d
    if (/^[0-9]{4}-[0-9]{2}-[0-9]{2}\s+\S+\s+(LONG|SHORT)/.test(line)) {
      const date = line.substring(0, 10);
      const rest = line.substring(11);
      const parts = rest.split(/\s+/);
      const product = parts[0];
      const direction = parts[1];
      
      const lotsMatch = line.match(/(\d+) 手/);
      const pnlMatch = line.match(/([+-]?[\d.]+) 元\s*$/);
      
      if (lotsMatch && pnlMatch) {
        trades.push({
          date,
          product,
          direction,
          lots: parseInt(lotsMatch[1]),
          pnl: parseFloat(pnlMatch[1])
        });
      }
    }
  }
  
  return trades;
}

// 解析品种汇总
function parseSummary(text) {
  const summary = {};
  const productRegex = /(\S+ 主连)\s*\([^)]+\):[\s\S]*?交易次数：(\d+)[\s\S]*?累计盈亏：([+-]?[\d.]+) 元[\s\S]*?胜率：([\d.]+)%/g;
  let match;
  
  while ((match = productRegex.exec(text)) !== null) {
    const [, name, trades, pnl, winRate] = match;
    summary[name] = {
      trades: parseInt(trades),
      pnl: parseFloat(pnl),
      winRate: parseFloat(winRate)
    };
  }
  
  return summary;
}

// 按月份统计
function groupByMonth(trades) {
  const monthly = {};
  
  for (const trade of trades) {
    const month = trade.date.substring(0, 7);
    if (!monthly[month]) {
      monthly[month] = { total: 0, trades: 0, wins: 0, losses: 0, byProduct: {} };
    }
    
    monthly[month].total += trade.pnl;
    monthly[month].trades++;
    
    if (trade.pnl > 0) monthly[month].wins++;
    else if (trade.pnl < 0) monthly[month].losses++;
    
    if (!monthly[month].byProduct[trade.product]) monthly[month].byProduct[trade.product] = 0;
    monthly[month].byProduct[trade.product] += trade.pnl;
  }
  
  return monthly;
}

// 按品种统计
function groupByProduct(trades) {
  const byProduct = {};
  
  for (const trade of trades) {
    if (!byProduct[trade.product]) {
      byProduct[trade.product] = { total: 0, trades: 0, wins: 0, losses: 0, monthly: {} };
    }
    
    byProduct[trade.product].total += trade.pnl;
    byProduct[trade.product].trades++;
    
    if (trade.pnl > 0) byProduct[trade.product].wins++;
    else if (trade.pnl < 0) byProduct[trade.product].losses++;
    
    const month = trade.date.substring(0, 7);
    if (!byProduct[trade.product].monthly[month]) byProduct[trade.product].monthly[month] = 0;
    byProduct[trade.product].monthly[month] += trade.pnl;
  }
  
  return byProduct;
}

// 计算累计收益
function calculateCumulative(trades) {
  const sorted = [...trades].sort((a, b) => a.date.localeCompare(b.date));
  const cumulative = [];
  let sum = 0;
  
  for (const trade of sorted) {
    sum += trade.pnl;
    cumulative.push({ date: trade.date, pnl: trade.pnl, cumulative: sum });
  }
  
  return cumulative;
}

// 解析数据
const trades = parseTrades(rawData);
const summary = parseSummary(rawData);
const monthly = groupByMonth(trades);
const byProduct = groupByProduct(trades);
const cumulative = calculateCumulative(trades);

console.log(`✅ 总交易笔数：${trades.length}`);
console.log(`✅ 总盈亏：${cumulative.length > 0 ? cumulative[cumulative.length - 1].cumulative : 0} 元`);
console.log(`✅ 月份数：${Object.keys(monthly).length}`);
console.log(`✅ 品种数：${Object.keys(byProduct).length}`);

// 保存 JSON
fs.writeFileSync(
  path.join(__dirname, 'analysis_data.json'),
  JSON.stringify({ trades, summary, monthly, byProduct, cumulative, generatedAt: new Date().toISOString() }, null, 2),
  'utf-8'
);

// 生成 H5
generateH5(monthly, byProduct, cumulative, trades);

function generateH5(monthly, byProduct, cumulative, allTrades) {
  const months = Object.keys(monthly).sort();
  const monthlyData = months.map(m => ({
    month: m, pnl: monthly[m].total, trades: monthly[m].trades, wins: monthly[m].wins, losses: monthly[m].losses
  }));
  
  const products = Object.keys(byProduct);
  const productData = products.map(p => ({
    name: p, pnl: byProduct[p].total, trades: byProduct[p].trades,
    winRate: byProduct[p].trades > 0 ? ((byProduct[p].wins / byProduct[p].trades) * 100).toFixed(1) : 0
  }));
  
  const totalPnl = cumulative.length > 0 ? cumulative[cumulative.length - 1].cumulative : 0;
  const totalTrades = allTrades.length;
  const winningTrades = allTrades.filter(t => t.pnl > 0).length;
  const winRate = totalTrades > 0 ? ((winningTrades / totalTrades) * 100).toFixed(1) : 0;
  
  const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>期货交易回测报告</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; padding: 20px; }
    .container { max-width: 1200px; margin: 0 auto; }
    h1 { text-align: center; color: #333; margin-bottom: 30px; font-size: 28px; }
    h2 { color: #444; margin: 30px 0 15px; font-size: 20px; border-left: 4px solid #1890ff; padding-left: 10px; }
    .summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
    .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .card h3 { color: #666; font-size: 14px; margin-bottom: 10px; }
    .card .value { font-size: 28px; font-weight: bold; color: #333; }
    .card .value.positive { color: #52c41a; }
    .card .value.negative { color: #f5222d; }
    .chart-container { background: white; border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .chart-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
    table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; }
    th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
    th { background: #fafafa; font-weight: 600; color: #333; }
    tr:hover { background: #f5f5f5; }
    .positive { color: #52c41a; font-weight: 600; }
    .negative { color: #f5222d; font-weight: 600; }
    .product-tag { display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 4px; }
    .product-tag 豆粕 { background: #e6f7ff; color: #1890ff; }
    .product-tag 鸡蛋 { background: #fff7e6; color: #fa8c16; }
    .product-tag 尿素 { background: #f6ffed; color: #52c41a; }
    .product-tag 硅铁 { background: #fff0f6; color: #eb2f96; }
    .info-box { background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
    .info-box p { color: #0050b3; margin: 5px 0; }
    @media (max-width: 768px) { .chart-row { grid-template-columns: 1fr; } th, td { padding: 8px 10px; font-size: 14px; } }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 期货交易回测报告</h1>
    <div class="info-box">
      <p><strong>回测时间：</strong>2025-03-19 至 2026-03-19</p>
      <p><strong>总资金：</strong>每个品种 100,000 元（独立测试）</p>
      <p><strong>仓位比例：</strong>20% - 30%</p>
    </div>
    <div class="summary-cards">
      <div class="card"><h3>总盈亏</h3><div class="value ${totalPnl >= 0 ? 'positive' : 'negative'}">${totalPnl >= 0 ? '+' : ''}${totalPnl.toFixed(0)} 元</div></div>
      <div class="card"><h3>总交易笔数</h3><div class="value">${totalTrades}</div></div>
      <div class="card"><h3>胜率</h3><div class="value">${winRate}%</div></div>
      <div class="card"><h3>回测月份</h3><div class="value">${months.length} 个月</div></div>
    </div>
    <h2>📈 月度盈亏走势</h2>
    <div class="chart-container"><canvas id="monthlyChart"></canvas></div>
    <h2>📉 累计收益曲线</h2>
    <div class="chart-container"><canvas id="cumulativeChart"></canvas></div>
    <h2>🎯 品种表现对比</h2>
    <div class="chart-row">
      <div class="chart-container"><canvas id="productPnlChart"></canvas></div>
      <div class="chart-container"><canvas id="productWinRateChart"></canvas></div>
    </div>
    <h2>📋 品种详细数据</h2>
    <table>
      <thead><tr><th>品种</th><th>交易次数</th><th>总盈亏 (元)</th><th>胜率</th></tr></thead>
      <tbody>${productData.map(p => `<tr><td><span class="product-tag ${p.name.replace('主连', '')}">${p.name}</span></td><td>${p.trades}</td><td class="${p.pnl >= 0 ? 'positive' : 'negative'}">${p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(0)}</td><td>${p.winRate}%</td></tr>`).join('')}</tbody>
    </table>
    <h2>📅 月度详细数据</h2>
    <table>
      <thead><tr><th>月份</th><th>交易次数</th><th>盈利</th><th>亏损</th><th>净盈亏 (元)</th></tr></thead>
      <tbody>${monthlyData.map(m => `<tr><td>${m.month}</td><td>${m.trades}</td><td class="positive">${m.wins}</td><td class="negative">${m.losses}</td><td class="${m.pnl >= 0 ? 'positive' : 'negative'}">${m.pnl >= 0 ? '+' : ''}${m.pnl.toFixed(0)}</td></tr>`).join('')}</tbody>
    </table>
  </div>
  <script>
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    new Chart(document.getElementById('monthlyChart'), {
      type: 'bar',
      data: {
        labels: ${JSON.stringify(monthlyData.map(m => m.month))},
        datasets: [{
          label: '月度盈亏 (元)',
          data: ${JSON.stringify(monthlyData.map(m => m.pnl))},
          backgroundColor: ${JSON.stringify(monthlyData.map(m => m.pnl >= 0 ? 'rgba(82, 196, 26, 0.7)' : 'rgba(245, 34, 45, 0.7)'))},
          borderColor: ${JSON.stringify(monthlyData.map(m => m.pnl >= 0 ? '#52c41a' : '#f5222d'))},
          borderWidth: 1
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => ctx.parsed.y >= 0 ? '+' + ctx.parsed.y.toFixed(0) + '元' : ctx.parsed.y.toFixed(0) + '元' } } }, scales: { y: { beginAtZero: true, grid: { color: '#f0f0f0' } }, x: { grid: { display: false } } } }
    });
    new Chart(document.getElementById('cumulativeChart'), {
      type: 'line',
      data: {
        labels: ${JSON.stringify(cumulative.map(c => c.date))},
        datasets: [{ label: '累计收益 (元)', data: ${JSON.stringify(cumulative.map(c => c.cumulative))}, borderColor: '#1890ff', backgroundColor: 'rgba(24, 144, 255, 0.1)', fill: true, tension: 0.1, pointRadius: 2 }]
      },
      options: { responsive: true, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => '累计：' + ctx.parsed.y.toFixed(0) + '元' } } }, scales: { y: { grid: { color: '#f0f0f0' } }, x: { grid: { display: false }, ticks: { maxTicksLimit: 10 } } } }
    });
    new Chart(document.getElementById('productPnlChart'), {
      type: 'bar',
      data: {
        labels: ${JSON.stringify(productData.map(p => p.name))},
        datasets: [{ label: '总盈亏 (元)', data: ${JSON.stringify(productData.map(p => p.pnl))}, backgroundColor: ${JSON.stringify(productData.map(p => p.pnl >= 0 ? 'rgba(82, 196, 26, 0.7)' : 'rgba(245, 34, 45, 0.7)'))}, borderColor: ${JSON.stringify(productData.map(p => p.pnl >= 0 ? '#52c41a' : '#f5222d'))}, borderWidth: 1 }]
      },
      options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { grid: { color: '#f0f0f0' } }, y: { grid: { display: false } } } }
    });
    new Chart(document.getElementById('productWinRateChart'), {
      type: 'doughnut',
      data: { labels: ${JSON.stringify(productData.map(p => p.name))}, datasets: [{ data: ${JSON.stringify(productData.map(p => p.trades))}, backgroundColor: ['#1890ff', '#fa8c16', '#52c41a', '#eb2f96'] }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom' }, title: { display: true, text: '交易次数分布' } } }
    });
  </script>
</body>
</html>`;

  fs.writeFileSync(path.join(__dirname, 'trading_report.html'), html, 'utf-8');
  console.log('✅ H5 报告已生成：trading_report.html');
}
