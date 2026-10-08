param(
    [int]$Port = 18081,
    [string]$EnvFile,
    [ValidateSet('dashscope','bge')][string]$EmbeddingBackend = 'dashscope',
    [ValidateSet('cpu','cuda')][string]$Device = 'cpu',
    [ValidateSet('hybrid_window','hybrid','adaptive','dense')][string]$Mode = 'hybrid_window',
    [int]$ContextChars = 24000
)
$ErrorActionPreference = 'Stop'
if ($EnvFile) {
    foreach ($line in Get-Content -LiteralPath $EnvFile -Encoding UTF8) {
        if ($line -match '^\s*(#|$)') { continue }
        if ($line -notmatch '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') { throw 'Invalid environment file line.' }
        $settingName = $Matches[1]
        $settingValue = $Matches[2].Trim()
        if (($settingValue.StartsWith('"') -and $settingValue.EndsWith('"')) -or ($settingValue.StartsWith("'") -and $settingValue.EndsWith("'"))) {
            $settingValue = $settingValue.Substring(1, $settingValue.Length - 2)
        }
        [Environment]::SetEnvironmentVariable($settingName, $settingValue, 'Process')
    }
}
$projectPath = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv-cycle2\Scripts\python.exe'
if ($EmbeddingBackend -eq 'bge' -or -not (Test-Path -LiteralPath $pythonPath)) {
    $pythonPath = Join-Path $projectPath 'models\.venv\Scripts\python.exe'
}
if (-not (Test-Path -LiteralPath $pythonPath)) { $pythonPath = 'python' }
$env:AE_EMBEDDING_BACKEND = $EmbeddingBackend
if ($EmbeddingBackend -eq 'bge') {
    $env:AE_EMBEDDING_PATH = Join-Path $projectPath 'MemoryBench-Shared\models\embeddings\bge-small-en-v1.5'
} elseif (-not $env:DASHSCOPE_API_KEY -or -not $env:AE_EMBEDDING_URL) {
    throw 'Set DASHSCOPE_API_KEY and AE_EMBEDDING_URL before starting the Cycle 2 service.'
}
# Windows uses a separate local data directory, not Docker's /data mount.
$env:AE_DATABASE = Join-Path $PSScriptRoot "runs\context-weave-v031-$EmbeddingBackend\memory.sqlite3"
$env:AE_ADD_INDEXER = '1'
if (-not $env:OPENROUTER_API_KEY) { throw 'Set OPENROUTER_API_KEY before starting version 0.3.1.' }
$env:AE_DEVICE = $Device
$env:AE_MODE = $Mode
$env:AE_CONTEXT_CHARS = [string]$ContextChars
$env:PYTHONPATH = $PSScriptRoot
if (-not $env:MEMORY_API_KEY) { throw 'Set MEMORY_API_KEY before starting the service.' }
& $pythonPath -m uvicorn adaptive_evidence.api:app --host 127.0.0.1 --port $Port --workers 1 --no-access-log
exit $LASTEXITCODE
