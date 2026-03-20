# Auto-update GitHub hosts script
# Source: https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$backupPath = "C:\Users\17699\.openclaw\workspace\hosts.backup"
$newHostsUrl = "https://gitlab.com/ineo6/hosts/-/raw/master/next-hosts"
$tempFile = "C:\Users\17699\.openclaw\workspace\hosts_new"

Write-Host "========================================"
Write-Host "Updating GitHub hosts..."
Write-Host "========================================"
Write-Host ""

# Backup current hosts
try {
    Copy-Item $hostsPath $backupPath -Force
    Write-Host "[OK] Backup created"
} catch {
    Write-Host "[FAIL] Backup: $_"
    exit 1
}

# Download new hosts
try {
    Write-Host "Downloading latest hosts..."
    Invoke-RestMethod -Uri $newHostsUrl -OutFile $tempFile -UseBasicParsing
    Write-Host "[OK] Downloaded"
} catch {
    Write-Host "[FAIL] Download: $_"
    exit 1
}

# Read new hosts content
$newHostsContent = Get-Content $tempFile -Raw

# Read original hosts
$originalHosts = Get-Content $hostsPath -Raw

# Check if GitHub section exists
$githubSectionStart = "# GitHub Start"
$githubSectionEnd = "# GitHub End"

if ($originalHosts -match [regex]::Escape($githubSectionStart)) {
    $pattern = [regex]::Escape($githubSectionStart) + ".*?" + [regex]::Escape($githubSectionEnd)
    $newContent = $originalHosts -replace $pattern, ($githubSectionStart + "`r`n" + $newHostsContent + "`r`n" + $githubSectionEnd)
    Write-Host "Replacing existing GitHub entries"
} else {
    $newContent = $originalHosts + "`r`n" + $githubSectionStart + "`r`n" + $newHostsContent + "`r`n" + $githubSectionEnd + "`r`n"
    Write-Host "Adding new GitHub entries"
}

# Write hosts file
try {
    Set-Content -Path $hostsPath -Value $newContent -Encoding ASCII -Force
    Write-Host "[OK] hosts updated"
} catch {
    Write-Host "[FAIL] Write: $_"
    Write-Host "Need admin rights"
    exit 1
}

# Flush DNS
Write-Host "Flushing DNS..."
ipconfig /flushdns | Out-Null
Write-Host "[OK] DNS flushed"

Write-Host ""
Write-Host "========================================"
Write-Host "Done!"
Write-Host "========================================"
Write-Host ""
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
