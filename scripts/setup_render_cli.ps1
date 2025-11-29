$ErrorActionPreference = 'Stop'

# Read RENDER_API from project .env
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$envPath = Join-Path $projectRoot '.env'
if (!(Test-Path $envPath)) { throw "Arquivo .env não encontrado: $envPath" }

$token = $null
Get-Content $envPath | ForEach-Object {
  if ($_ -match '^\s*RENDER_API\s*=\s*(.*)\s*$') { $token = $Matches[1] }
}
if (-not $token) { throw 'Variável RENDER_API não definida no .env' }

# Write CLI config to user profile
$cfgDir = Join-Path $HOME '.config\render'
$cfgFile = Join-Path $cfgDir 'config.yaml'
New-Item -ItemType Directory -Path $cfgDir -Force | Out-Null

$yaml = @()
$yaml += "token: $token"
$yaml += "workspace:"  # opcional, CLI poderá solicitar set posterior
Set-Content -Path $cfgFile -Value ($yaml -join "`n") -NoNewline

Write-Output "Render CLI configurado: $cfgFile"
