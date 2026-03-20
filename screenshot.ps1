Add-Type -AssemblyName System.Windows.Forms
$bmp = New-Object System.Drawing.Bitmap(1920, 1080)
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen(0, 0, 0, 0, (New-Object System.Drawing.Size(1920, 1080)))
$bmp.Save("C:\Users\17699\.openclaw\workspace\screenshot.png")
$bmp.Dispose()
Write-Host "Screenshot saved"