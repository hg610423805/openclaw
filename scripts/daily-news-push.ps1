# 每日新闻推送脚本 - 期货 + A 股
# 每天早上 8 点执行

param(
    [switch]$TestMode
)

$ErrorActionPreference = "Stop"
$workspace = "C:\Users\17699\.openclaw\workspace"
$outputDir = "$workspace\news_data"
if (!(Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir | Out-Null }

# ==================== 配置 ====================
$FUTURE_KEYWORDS = @("锰硅", "硅锰", "锰硅合金", "硅锰合金")
$STOCK_SECTORS = @("算力", "电力", "储能电池", "机器人", "商业航天")
$DATE_RANGE = 1  # 过去 1 天

# ==================== 工具函数 ====================
function Get-NewsFromSource {
    param($source, $keywords)
    # 模拟新闻抓取（实际需调用 API）
    $news = @()
    
    # 这里需要接入真实 API：东方财富、财联社等
    # 暂时返回示例数据
    foreach ($kw in $keywords) {
        $news += [PSCustomObject]@{
            Time = (Get-Date).AddHours(-2).ToString("HH:mm")
            Title = "[$source] $kw 相关消息示例"
            Impact = "中性"
            Suggestion = "观望"
            Source = $source
        }
    }
    return $news
}

function Format-NewsReport {
    param($futureNews, $stockNews)
    
    $report = @"
# 📰 每日新闻推送 ($(Get-Date -Format "yyyy-MM-dd"))

## 🛢️ 期货锰硅新闻 (过去 24 小时)
"@
    
    if ($futureNews.Count -eq 0) {
        $report += "`n> 今日无重大消息`n"
    } else {
        foreach ($n in $futureNews) {
            $report += "`n### $($n.Time) - $($n.Title)"
            $report += "`n- 影响：$($n.Impact)"
            $report += "`n- 建议：$($n.Suggestion)"
            $report += "`n- 来源：$($n.Source)`n"
        }
    }
    
    $report += "`n## 📈 A 股板块新闻 (过去 24 小时)`n"
    
    if ($stockNews.Count -eq 0) {
        $report += "> 今日无重大消息`n"
    } else {
        foreach ($n in $stockNews) {
            $report += "`n### $($n.Time) - $($n.Title)"
            $report += "`n- 影响：$($n.Impact)"
            $report += "`n- 建议：$($n.Suggestion)"
            $report += "`n- 来源：$($n.Source)`n"
        }
    }
    
    return $report
}

# ==================== 主流程 ====================
Write-Host "🔍 开始抓取新闻..." -ForegroundColor Cyan

# 抓取期货新闻
Write-Host "  ├─ 期货锰硅新闻..." -ForegroundColor Yellow
$futureNews = Get-NewsFromSource -source "东方财富期货" -keywords $FUTURE_KEYWORDS

# 抓取 A 股新闻
Write-Host "  └─ A 股板块新闻..." -ForegroundColor Yellow
$stockNews = Get-NewsFromSource -source "财联社" -keywords $STOCK_SECTORS

# 生成报告
$report = Format-NewsReport -futureNews $futureNews -stockNews $stockNews

# 保存报告
$reportFile = "$outputDir\news-$(Get-Date -Format 'yyyy-MM-dd').md"
$report | Out-File -FilePath $reportFile -Encoding UTF8
Write-Host "✅ 报告已保存：$reportFile" -ForegroundColor Green

# 输出到控制台
Write-Host "`n$report"

# 如果配置了飞书推送，这里可以调用 openclaw send
# openclaw send --to "ou_2a456545aa7be2a12881fe2a3f21198e" --message $report

Write-Host "`n🎉 新闻推送完成！" -ForegroundColor Green
