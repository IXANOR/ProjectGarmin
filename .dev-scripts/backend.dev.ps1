$ErrorActionPreference = "Stop"
trap { Write-Host ("Backend error: {0}" -f ($_.Exception.Message)) -ForegroundColor Red; Read-Host 'Press Enter to close this window'; break }
Set-Location -Path "C:\Users\igpod\OneDrive\Pulpit\Projekt Garmin\ProjectGarmin";
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
  if ($LASTEXITCODE -ne 0) { Write-Host ("Uvicorn exited with code {0}" -f $LASTEXITCODE) -ForegroundColor Red; Read-Host 'Press Enter to close this window' }
} else {
  if (-not (Test-Path -Path '.venv\Scripts\python.exe')) {
    py -3 -m venv .venv
  }
  .\.venv\Scripts\python -m pip install --upgrade pip setuptools wheel
  .\.venv\Scripts\python -m pip install fastapi 'uvicorn[standard]' sqlmodel sqlalchemy chromadb pypdf python-multipart pillow pytesseract
  .\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  if ($LASTEXITCODE -ne 0) { Write-Host ("Uvicorn exited with code {0}" -f $LASTEXITCODE) -ForegroundColor Red; Read-Host 'Press Enter to close this window' }
}
Read-Host 'Backend window ready. Press Enter to close this window'
