$ErrorActionPreference = 'Stop'

# Resolve paths
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$envPath = Join-Path $projectRoot '.env'
$binDir = Join-Path $projectRoot 'bin'
$renderExe = Join-Path $binDir 'render.exe'

if (!(Test-Path $envPath)) { throw "Arquivo .env não encontrado: $envPath" }

# Load env vars
Get-Content $envPath | ForEach-Object {
  if ($_ -match '^\s*([^=]+)\s*=\s*(.*)\s*$') { [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2]) }
}

if (-not $env:RENDER_API -and -not $env:RENDER_API_KEY) { throw 'Defina RENDER_API ou RENDER_API_KEY no .env' }
if ($env:RENDER_API -and -not $env:RENDER_API_KEY) { $env:RENDER_API_KEY = $env:RENDER_API }

# Ensure bin dir
New-Item -ItemType Directory -Force -Path $binDir | Out-Null

# Download Render CLI latest for Windows if missing
if (!(Test-Path $renderExe)) {
  Write-Output 'Baixando Render CLI (Windows)...'
  $headers = @{ 'User-Agent' = 'Trae-AI'; 'Accept' = 'application/vnd.github+json' }
  $rel = Invoke-RestMethod -Uri 'https://api.github.com/repos/render-oss/cli/releases/latest' -Headers $headers
  $asset = $rel.assets | Where-Object { $_.name -match 'windows.*(x86_64|amd64).*\.(exe|zip)$' }
  if (-not $asset) { $asset = $rel.assets | Where-Object { $_.name -match 'windows.*\.(exe|zip)$' } }
  if (-not $asset) { throw 'Não foi possível localizar asset do Render CLI para Windows (.exe/.zip)' }
  $tmpFile = Join-Path $binDir $asset.name
  Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $tmpFile
  if ($tmpFile.ToLower().EndsWith('.zip')) {
    Expand-Archive -Path $tmpFile -DestinationPath $binDir -Force
    $cand = Get-ChildItem -Path $binDir -Recurse -Filter 'render*.exe' | Select-Object -First 1
    if (-not $cand) { throw 'Zip baixado, mas não encontrei render.exe dentro' }
    Copy-Item $cand.FullName $renderExe -Force
  } else {
    Copy-Item $tmpFile $renderExe -Force
  }
}

# Validate CLI works with API key (non-interativo)
& $renderExe --help | Out-Null

# Deploy blueprint para garantir recursos (web, db, worker de migrações)
Write-Output 'Aplicando blueprint...'
& $renderExe blueprints deploy --path (Join-Path $projectRoot 'render.yaml') --confirm --output text | Out-Null

# Encontrar serviço de migrações e disparar deploy (aguardar conclusão)
Write-Output 'Localizando serviço de migrações...'
$servicesJson = & $renderExe services --output json --confirm
$services = $servicesJson | ConvertFrom-Json
$mig = $services | Where-Object { $_.name -eq 'sistema-pdf-migrations' }
if (-not $mig) { throw 'Serviço de migrações não encontrado. Verifique se blueprint criou o serviço.' }

Write-Output "Disparando deploy para $($mig.id)..."
& $renderExe deploys create $mig.id --wait --confirm --output text | Out-Null

Write-Output 'Migrações executadas com sucesso.'
