param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidatePattern('^[A-Za-z]:?$')]
    [string]$DriveLetter
)

# Normalize input so both "D" and "D:" work
$DriveLetter = $DriveLetter.TrimEnd(':').ToUpper()

$drive = Get-PSDrive -Name $DriveLetter -ErrorAction SilentlyContinue

if (-not $drive) {
    Write-Error "Drive '$DriveLetter`:' was not found."
    exit 1
}

$totalBytes = $drive.Used + $drive.Free

if ($totalBytes -le 0) {
    Write-Error "Unable to determine storage information for drive '$DriveLetter`:'."
    exit 1
}

$usedKB  = [math]::Round($drive.Used / 1KB, 1)
$freeKB  = [math]::Round($drive.Free / 1KB, 1)
$totalKB = [math]::Round($totalBytes / 1KB, 1)

$usedPercent = [math]::Round(($drive.Used / $totalBytes) * 100, 1)
$freePercent = [math]::Round(($drive.Free / $totalBytes) * 100, 1)

Write-Host ""
Write-Host "CircuitPython Storage - $DriveLetter`:"
Write-Host "--------------------------------"
Write-Host "Total     : $totalKB KB"
Write-Host "Used      : $usedKB KB"
Write-Host "Free      : $freeKB KB"
Write-Host "Usage     : $usedPercent% used / $freePercent% remaining"
Write-Host ""
```
