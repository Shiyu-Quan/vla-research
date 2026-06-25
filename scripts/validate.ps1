[CmdletBinding()]
param(
    [string]$PythonCommand = "python",
    [string]$QuickValidatePath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue)
}

$repoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..")
$env:PYTHONUTF8 = "1"
$sourcePath = Join-Path $repoRoot "src"
if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) {
    $env:PYTHONPATH = $sourcePath
}
else {
    $env:PYTHONPATH = (
        $sourcePath +
        [System.IO.Path]::PathSeparator +
        $env:PYTHONPATH
    )
}

if ([string]::IsNullOrWhiteSpace($QuickValidatePath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        $codexHome = $env:CODEX_HOME
    }
    else {
        $codexHome = Join-Path $env:USERPROFILE ".codex"
    }
    $QuickValidatePath = Join-Path $codexHome (
        "skills\.system\skill-creator\scripts\quick_validate.py"
    )
}

$validator = Resolve-FullPath $QuickValidatePath
if (-not (Test-Path -LiteralPath $validator -PathType Leaf)) {
    throw (
        "Skill validator not found: $validator. " +
        "Supply -QuickValidatePath with the path to quick_validate.py."
    )
}

Write-Output "Running Python tests..."
& $PythonCommand -m unittest discover `
    -s (Join-Path $repoRoot "tests") `
    -v
if ($LASTEXITCODE -ne 0) {
    throw "Python test suite failed."
}

Write-Output "Validating Codex skill..."
& $PythonCommand $validator (Join-Path $repoRoot "skill\vla-research")
if ($LASTEXITCODE -ne 0) {
    throw "Skill validation failed."
}

Write-Output "Checking CLI..."
& $PythonCommand -m vla_research.cli --help | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "CLI smoke test failed."
}

Write-Output "VALIDATION PASSED"
