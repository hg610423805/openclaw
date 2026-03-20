$raw = [System.IO.File]::ReadAllText("C:/Users/17699/.openclaw/workspace/summary.txt", [System.Text.Encoding]::UTF8)
$lines = $raw -split "`r?`n"

$trades = @()
foreach($l in $lines){
    if($l -match '^[0-9]{4}-[0-9]{2}-[0-9]{2}\s+\S+\s+(LONG|SHORT)'){
        if($l -match '(\d+) shou'){
            $lots = [int]$matches[1]
        }else{continue}
        if($l -match '([+-]?[\d.]+) yuan\s*$'){
            $pnl = [double]$matches[1]
        }else{continue}
        $date = $l.Substring(0,10)
        $rest = $l.Substring(11)
        $parts = $rest -split '\s+'
        $product = $parts[0]
        $dir = $parts[1]
        $trades += @{date=$date;product=$product;dir=$dir;lots=$lots;pnl=$pnl}
    }
}

Write-Host "Trades: $($trades.Count)"
