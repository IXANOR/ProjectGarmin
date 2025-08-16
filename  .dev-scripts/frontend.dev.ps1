$ErrorActionPreference = "Stop"
trap { Write-Host ("Frontend error: {0}" -f ($_.Exception.Message)) -ForegroundColor Red; Read-Host 'Press Enter to close this window'; break }
Set-Location -LiteralPath 'C:\Users\igpod\OneDrive\Pulpit\Projekt Garmin\ProjectGarmin\frontend';

# Ensure Node on PATH for this session
$nodeDir = @(
  'C:\Program Files\nodejs',
  'C:\Program Files (x86)\nodejs',
  (Join-Path $env:LocalAppData 'Programs/nodejs')
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($nodeDir) {
  $env:Path = "$nodeDir;" + $env:Path
}
$nodeName = if ($nodeDir) { $nodeDir } else { '<not found>' }
Write-Host ("Node search -> using: {0}" -f $nodeName) -ForegroundColor Cyan

# Verify node is runnable now
$nodeOk = $false
try {
  $nv = (& node -v) 2>$null
  if ($LASTEXITCODE -eq 0 -or $nv) { $nodeOk = $true; Write-Host ("node -v => {0}" -f $nv) -ForegroundColor DarkCyan }
} catch { $nodeOk = $false }
if (-not $nodeOk) {
  # try explicit node.exe inside nodeDir
  if ($nodeDir) {
    $nodeExe = Join-Path $nodeDir 'node.exe'
    if (Test-Path $nodeExe) {
      Set-Alias node $nodeExe -Scope Process
      $nv = (& node -v) 2>$null
      if ($LASTEXITCODE -eq 0 -or $nv) { $nodeOk = $true; Write-Host ("node -v => {0}" -f $nv) -ForegroundColor DarkCyan }
    }
  }
}
if (-not $nodeOk) {
  Write-Host 'Node is not available on PATH in this window. Ensure Node.js 20+ is installed and restart.' -ForegroundColor Yellow
  Read-Host 'Press Enter to close this window'
  exit 1
}

# Resolve npm
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
  $fallbackNpm = @(
    'C:\Program Files\nodejs\npm.cmd',
    'C:\Program Files (x86)\nodejs\npm.cmd',
    (Join-Path $env:LocalAppData 'Programs/nodejs/npm.cmd')
  ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}
$npm = if ($npmCmd) { $npmCmd.Source } else { $fallbackNpm }
if (-not $npm) {
  Write-Host 'npm not found. Install Node.js 20+ and reopen PowerShell, or add Node dir to PATH.' -ForegroundColor Yellow
  Read-Host 'Press Enter to close this window'
  exit 1
}
Write-Host "Using npm: $npm" -ForegroundColor Cyan

# Clean potentially locked node_modules on OneDrive
if (Test-Path -LiteralPath 'node_modules') {
  Write-Host 'Cleaning node_modules (may take a moment)...' -ForegroundColor DarkGray
  $removed = $false
  try {
    Remove-Item -Recurse -Force -LiteralPath 'node_modules' -ErrorAction Stop
    $removed = $true
  } catch { $removed = $false }
  if (-not $removed) {
    $tempName = ('node_modules.__delete__{0}' -f ([guid]::NewGuid().ToString('N')))
    try { Rename-Item -LiteralPath 'node_modules' -NewName $tempName -ErrorAction Stop } catch {}
    if (Test-Path -LiteralPath $tempName) {
      Start-Process -FilePath 'cmd.exe' -ArgumentList '/d','/c','rmdir','/s','/q', $tempName -WindowStyle Hidden -Wait | Out-Null
    }
  }
}

# Install deps and start Vite
& $npm install --no-audit --no-fund
if ($LASTEXITCODE -ne 0) {
  Write-Host 'npm install failed. Ensure node is on PATH in this window and retry.' -ForegroundColor Red
  Read-Host 'Press Enter to close this window'
  exit 1
}

& $npm run dev
if ($LASTEXITCODE -ne 0) { Write-Host ("npm dev exited with code {0}" -f $LASTEXITCODE) -ForegroundColor Red; Read-Host 'Press Enter to close this window' }
Read-Host 'Frontend window ready. Press Enter to close this window'
