[CmdletBinding()]
param(
    [string]$MemoryPath = "",
    [string]$CodexHome = "",
    [string]$PythonCommand = "python",
    [switch]$ForceSkillUpdate,
    [switch]$SkipPythonInstall,
    [switch]$SkipSmokeTest
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue)
}

function Assert-SafeSkillTarget {
    param(
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $true)][string]$SkillsRoot
    )

    $targetPath = Resolve-FullPath $Target
    $skillsPath = (Resolve-FullPath $SkillsRoot).TrimEnd("\")
    $parent = (Split-Path -Parent $targetPath).TrimEnd("\")
    $leaf = Split-Path -Leaf $targetPath

    if (
        -not $parent.Equals(
            $skillsPath,
            [System.StringComparison]::OrdinalIgnoreCase
        ) -or
        $leaf -ne "vla-research"
    ) {
        throw "Unsafe skill target: $targetPath"
    }
}

$repoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..")
$sourceSkill = Join-Path $repoRoot "skill\vla-research"
$templatePath = Join-Path $repoRoot "research-memory-template"

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        $CodexHome = $env:CODEX_HOME
    }
    else {
        $CodexHome = Join-Path $env:USERPROFILE ".codex"
    }
}

if ([string]::IsNullOrWhiteSpace($MemoryPath)) {
    if (-not [string]::IsNullOrWhiteSpace($env:VLA_RESEARCH_MEMORY)) {
        $MemoryPath = $env:VLA_RESEARCH_MEMORY
    }
    else {
        $MemoryPath = Join-Path $env:USERPROFILE "Documents\vla-research-memory"
    }
}

$resolvedCodexHome = Resolve-FullPath $CodexHome
$resolvedMemory = Resolve-FullPath $MemoryPath
$skillsRoot = Join-Path $resolvedCodexHome "skills"
$skillTarget = Join-Path $skillsRoot "vla-research"
$pythonExecutable = (Get-Command $PythonCommand -ErrorAction Stop).Source

if (-not $SkipPythonInstall) {
    $versionText = & $PythonCommand -c (
        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    )
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to run Python command: $PythonCommand"
    }
    $version = [version]$versionText.Trim()
    if ($version -lt [version]"3.10") {
        throw "Python 3.10 or newer is required; found $version"
    }

    & $PythonCommand -m pip install --user $repoRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Python package installation failed."
    }
}
else {
    Write-Output "SKIPPED Python package installation"
}

New-Item -ItemType Directory -Force -Path $skillsRoot | Out-Null
Assert-SafeSkillTarget -Target $skillTarget -SkillsRoot $skillsRoot

if (Test-Path -LiteralPath $skillTarget) {
    if ($ForceSkillUpdate) {
        Remove-Item -LiteralPath $skillTarget -Recurse -Force
        Write-Output "Removed existing skill for update: $skillTarget"
    }
    else {
        Write-Output (
            "Skill already exists; use -ForceSkillUpdate to replace it: " +
            $skillTarget
        )
    }
}

if (-not (Test-Path -LiteralPath $skillTarget)) {
    New-Item -ItemType Directory -Force -Path $skillTarget | Out-Null
    Get-ChildItem -LiteralPath $sourceSkill -Force |
        ForEach-Object {
            Copy-Item -LiteralPath $_.FullName `
                -Destination $skillTarget -Recurse -Force
        }
    Write-Output "Installed skill: $skillTarget"
}

& (Join-Path $PSScriptRoot "initialize-memory.ps1") `
    -MemoryPath $resolvedMemory `
    -TemplatePath $templatePath

if (-not $SkipSmokeTest) {
    $previousMemory = $env:VLA_RESEARCH_MEMORY
    try {
        $env:VLA_RESEARCH_MEMORY = $resolvedMemory
        & $PythonCommand -m vla_research.cli search "" --limit 1 |
            Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "CLI smoke test failed."
        }
    }
    finally {
        $env:VLA_RESEARCH_MEMORY = $previousMemory
    }
}
else {
    Write-Output "SKIPPED smoke test"
}

$escapedMemory = $resolvedMemory.Replace("\", "\\")
$escapedPython = $pythonExecutable.Replace("\", "\\")
Write-Output ""
Write-Output "Add this block to your Codex config.toml:"
Write-Output ""
Write-Output "[mcp_servers.vla_research]"
Write-Output ('command = "' + $escapedPython + '"')
Write-Output 'args = ["-m", "vla_research.server"]'
Write-Output "startup_timeout_sec = 30"
Write-Output ""
Write-Output "[mcp_servers.vla_research.env]"
Write-Output 'PYTHONUTF8 = "1"'
Write-Output ('VLA_RESEARCH_MEMORY = "' + $escapedMemory + '"')
Write-Output ""
Write-Output "Research memory: $resolvedMemory"
Write-Output "Codex skill: $skillTarget"
Write-Output "Restart Codex or open a new session after updating config.toml."
