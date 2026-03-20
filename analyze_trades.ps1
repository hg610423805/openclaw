# 期货交易分析脚本 - PowerShell 版本

# 读取文件
$content = Get-Content "C:\Users\17699\.openclaw\workspace\summary.txt" -Raw -Encoding UTF8
if ($content[0] -eq [char]0xFEFF) {
    $content = $content.Substring(1)
}

Write-Host "📊 开始分析交易数据..."

# 解析交易
$trades = @()
$lines = $content -split "`r?`n"

foreach ($line in $lines) {
    if ($line -match '^(?<date>[0-9]{4}-[0-9]{2}-[0-9]{2})\s+(?<product>\S+)\s+(?<dir>LONG|SHORT)') {
        if ($line -match '(?<lots>\d+) 手' -and $line -match '(?<pnl>[+-]?[\d.]+) 元\s*$') {
            $trades += @{
                date = $matches.date
                product = $matches.product
                direction = $matches.dir
                lots = [int]$matches.lots
                pnl = [double]$matches.pnl
            }
        }
    }
}

Write-Host "✅ 总交易笔数：$($trades.Count)"

if ($trades.Count -eq 0) {
    Write-Host "❌ 未找到交易数据"
    exit
}

# 按月份统计
$monthly = @{}
foreach ($t in $trades) {
    $month = $t.date.Substring(0, 7)
    if (-not $monthly.ContainsKey($month)) {
        $monthly[$month] = @{ total = 0; trades = 0; wins = 0; losses = 0 }
    }
    $monthly[$month].total += $t.pnl
    $monthly[$month].trades++
    if ($t.pnl -gt 0) { $monthly[$month].wins++ }
    elseif ($t.pnl -lt 0) { $monthly[$month].losses++ }
}

# 按品种统计
$byProduct = @{}
foreach ($t in $trades) {
    if (-not $byProduct.ContainsKey($t.product)) {
        $byProduct[$t.product] = @{ total = 0; trades = 0; wins = 0; losses = 0 }
    }
    $byProduct[$t.product].total += $t.pnl
    $byProduct[$t.product].trades++
    if ($t.pnl -gt 0) { $byProduct[$t.product].wins++ }
    elseif ($t.pnl -lt 0) { $byProduct[$t.product].losses++ }
}

# 计算累计
$sorted = $trades | Sort-Object date
$cumulative = @()
$sum = 0
foreach ($t in $sorted) {
    $sum += $t.pnl
    $cumulative += @{ date = $t.date; pnl = $t.pnl; cumulative = $sum }
}

$totalPnl = $cumulative[-1].cumulative
$totalTrades = $trades.Count
$winningTrades = ($trades | Where-Object { $_.pnl -gt 0 }).Count
$winRate = [math]::Round(($winningTrades / $totalTrades) * 100, 1)

Write-Host "✅ 总盈亏：$totalPnl 元"
Write-Host "✅ 胜率：$winRate%"
Write-Host "✅ 月份数：$($monthly.Count)"
Write-Host "✅ 品种数：$($byProduct.Count)"

# 生成 JSON
$data = @{
    trades = $trades
    monthly = $monthly
    byProduct = $byProduct
    cumulative = $cumulative
    totalPnl = $totalPnl
    totalTrades = $totalTrades
    winRate = $winRate
    generatedAt = (Get-Date).ToString('o')
}

$data | ConvertTo-Json -Depth 10 | Out-File "C:\Users\17699\.openclaw\workspace\analysis_data.json" -Encoding UTF8
Write-Host "✅ 数据已保存到 analysis_data.json"

# 准备图表数据
$months = $monthly.Keys | Sort-Object
$monthlyData = $months | ForEach-Object {
    @{ month = $_; pnl = $monthly[$_].total; trades = $monthly[$_].trades; wins = $monthly[$_].wins; losses = $monthly[$_].losses }
}

$products = $byProduct.Keys
$productData = $products | ForEach-Object {
    @{
        name = $_
        pnl = $byProduct[$_].total
        trades = $byProduct[$_].trades
        winRate = if ($byProduct[$_].trades -gt 0) { [math]::Round(($byProduct[$_].wins / $byProduct[$_].trades) * 100, 1) } else { 0 }
    }
}

# 生成 HTML
$html = @"
<!DOCTYPE html>
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
    @@media (max-width: 768px) { .chart-row { grid-template-columns: 1fr; } th, td { padding: 8px 10px; font-size: 14px; } }
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
      <div class="card"><h3>总盈亏</h3><div class="value $(if ($totalPnl -ge 0) {'positive'} else {'negative'})">$(if ($totalPnl -ge 0) {'+'} else {''})$([math]::Round($totalPnl)) 元</div></div>
      <div class="card"><h3>总交易笔数</h3><div class="value">$totalTrades</div></div>
      <div class="card"><h3>胜率</h3><div class="value">$winRate%</div></div>
      <div class="card"><h3>回测月份</h3><div class="value">$($months.Count) 个月</div></div>
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
      <tbody>
$(foreach ($p in $productData) {
    $className = if ($p.pnl -ge 0) {'positive'} else {'negative'}
    $sign = if ($p.pnl -ge 0) {'+'} else {''}
    $tagName = $p.name -replace '主连',''
    "        <tr><td><span class=\"product-tag $tagName\">$($p.name)</span></td><td>$($p.trades)</td><td class=\"$className\">$sign$([math]::Round($p.pnl))</td><td>$($p.winRate)%</td></tr>`n"
})
      </tbody>
    </table>
    <h2>📅 月度详细数据</h2>
    <table>
      <thead><tr><th>月份</th><th>交易次数</th><th>盈利</th><th>亏损</th><th>净盈亏 (元)</th></tr></thead>
      <tbody>
$(foreach ($m in $monthlyData) {
    $className = if ($m.pnl -ge 0) {'positive'} else {'negative'}
    $sign = if ($m.pnl -ge 0) {'+'} else {''}
    "        <tr><td>$($m.month)</td><td>$($m.trades)</td><td class=\"positive\">$($m.wins)</td><td class=\"negative\">$($m.losses)</td><td class=\"$className\">$sign$([math]::Round($m.pnl))</td></tr>`n"
})
      </tbody>
    </table>
  </div>
  <script>
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    new Chart(document.getElementById('monthlyChart'), {
      type: 'bar',
      data: {
        labels: $($monthlyData | ForEach-Object { "\"$($_.month)\"" } | Join-String -Separator ','),
        datasets: [{
          label: '月度盈亏 (元)',
          data: $($monthlyData | ForEach-Object { $_.pnl } | Join-String -Separator ','),
          backgroundColor: $($monthlyData | ForEach-Object { if ($_.pnl -ge 0) {'rgba(82, 196, 26, 0.7)'} else {'rgba(245, 34, 45, 0.7)'} } | Join-String -Separator ','),
          borderColor: $($monthlyData | ForEach-Object { if ($_.pnl -ge 0) {'#52c41a'} else {'#f5222d'} } | Join-String -Separator ','),
          borderWidth: 1
        }]
      },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true }, x: { grid: { display: false } } } }
    });
    new Chart(document.getElementById('cumulativeChart'), {
      type: 'line',
      data: {
        labels: $($cumulative | ForEach-Object { "\"$($_.date)\"" } | Select-Object -First 50 | Join-String -Separator ','),
        datasets: [{ label: '累计收益 (元)', data: $($cumulative | ForEach-Object { $_.cumulative } | Select-Object -First 50 | Join-String -Separator ','), borderColor: '#1890ff', backgroundColor: 'rgba(24, 144, 255, 0.1)', fill: true, tension: 0.1, pointRadius: 2 }]
      },
      options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#f0f0f0' } }, x: { grid: { display: false } } } }
    });
    new Chart(document.getElementById('productPnlChart'), {
      type: 'bar',
      data: {
        labels: $($productData | ForEach-Object { "\"$($_.name)\"" } | Join-String -Separator ','),
        datasets: [{ label: '总盈亏 (元)', data: $($productData | ForEach-Object { $_.pnl } | Join-String -Separator ','), backgroundColor: $($productData | ForEach-Object { if ($_.pnl -ge 0) {'rgba(82, 196, 26, 0.7)'} else {'rgba(245, 34, 45, 0.7)'} } | Join-String -Separator ','), borderColor: $($productData | ForEach-Object { if ($_.pnl -ge 0) {'#52c41a'} else {'#f5222d'} } | Join-String -Separator ','), borderWidth: 1 }]
      },
      options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } } }
    });
    new Chart(document.getElementById('productWinRateChart'), {
      type: 'doughnut',
      data: { labels: $($productData | ForEach-Object { "\"$($_.name)\"" } | Join-String -Separator ','), datasets: [{ data: $($productData | ForEach-Object { $_.trades } | Join-String -Separator ','), backgroundColor: ['#1890ff', '#fa8c16', '#52c41a', '#eb2f96'] }] },
      options: { responsive: true, plugins: { legend: { position: 'bottom' }, title: { display: true, text: '交易次数分布' } } }
    });
  </script>
</body>
</html>
"@

$html | Out-File "C:\Users\17699\.openclaw\workspace\trading_report.html" -Encoding UTF8
Write-Host "✅ H5 报告已生成：trading_report.html"
