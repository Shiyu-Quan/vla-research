[CmdletBinding()]
param(
    [string]$CodexHome = "",
    [string]$PythonCommand = "python",
    [switch]$SkipPythonUninstall,
    [switch]$RemoveMemory,
    [string]$MemoryPath = ""
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

if ([string]::IsNullOrWhiteSpace($CodexHome)) {
    if (-not [string]::IsNullOrWhiteSpace($env:CODEX_HOME)) {
        $CodexHome = $env:CODEX_HOME
    }
    else {
        $CodexHome = Join-Path $env:USERPROFILE ".codex"
    }
}

if ($RemoveMemory -and [string]::IsNullOrWhiteSpace($MemoryPath)) {
    throw "-MemoryPath is required when -RemoveMemory is supplied."
}

$resolvedCodexHome = Resolve-FullPath $CodexHome
$skillsRoot = Join-Path $resolvedCodexHome "skills"
$skillTarget = Join-Path $skillsRoot "vla-research"

Assert-SafeSkillTarget -Target $skillTarget -SkillsRoot $skillsRoot
Write-Output "Skill target: $skillTarget"

if (Test-Path -LiteralPath $skillTarget) {
    Remove-Item -LiteralPath $skillTarget -Recurse -Force
    Write-Output "Removed skill: $skillTarget"
}
else {
    Write-Output "Skill not installed: $skillTarget"
}

if (-not $SkipPythonUninstall) {
    & $PythonCommand -m pip uninstall -y vla-research
    if ($LASTEXITCODE -ne 0) {
        throw "Python package uninstallation failed."
    }
}
else {
    Write-Output "SKIPPED Python package uninstallation"
}

if ($RemoveMemory) {
    $resolvedMemory = Resolve-FullPath $MemoryPath
    $repoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..")
    if (
        $resolvedMemory.Equals(
            $repoRoot,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) {
        throw "Refusing to remove the repository checkout as research memory."
    }

    Write-Output "Memory target: $resolvedMemory"
    if (Test-Path -LiteralPath $resolvedMemory) {
        Remove-Item -LiteralPath $resolvedMemory -Recurse -Force
        Write-Output "Removed research memory: $resolvedMemory"
    }
    else {
        Write-Output "Research memory not found: $resolvedMemory"
    }
}
else {
    Write-Output "Research memory was preserved."
}
