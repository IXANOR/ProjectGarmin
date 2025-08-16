$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $root) { $root = Get-Location }

# Backend (FastAPI) window
$backendScript = @"
Set-Location -Path '$root';
if (Test-Path -LiteralPath '.env') {
  Get-Content -LiteralPath '.env' | ForEach-Object {
    if ($_ -match '^\s*#' -or $_ -match '^\s*$') { return }
    $pair = $_ -split '=', 2
    if ($pair.Length -eq 2) {
      $key = $pair[0].Trim()
      $val = $pair[1].Trim()
      try { Set-Item -Path ("env:{0}" -f $key) -Value $val -ErrorAction Stop } catch {}
    }
  }
}
if (Get-Command poetry -ErrorAction SilentlyContinue) {
  poetry install --no-interaction --no-ansi
  poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
} else {
  if (-not (Test-Path -Path '$root\.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
    .\.venv\Scripts\python -m pip install fastapi 'uvicorn[standard]'
  }
  .\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}
"@

# Frontend (Vite) window
$frontendDir = Join-Path $root 'frontend'
$frontendScript = @'
Set-Location -LiteralPath '__FRONTEND_DIR__';

# Ensure Node on PATH for this session
$nodeDir = @(
  'C:\Program Files\nodejs',
  'C:\Program Files (x86)\nodejs',
  (Join-Path $env:LocalAppData 'Programs/nodejs')
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if ($nodeDir) {
  $env:Path = "$nodeDir;" + $env:Path
}
Write-Host ("Node search -> using: {0}" -f (if ($nodeDir) { $nodeDir } else { '<not found>' })) -ForegroundColor Cyan

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
'@

$frontendScript = $frontendScript.Replace("__FRONTEND_DIR__", $frontendDir)

Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit','-Command', $backendScript
Start-Process -FilePath 'powershell.exe' -ArgumentList '-NoExit','-Command', $frontendScript

Write-Host "Backend: http://127.0.0.1:8000 (health: /health)" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green


