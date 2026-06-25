[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$MemoryPath,

    [string]$TemplatePath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-FullPath {
    param([Parameter(Mandatory = $true)][string]$PathValue)
    return [System.IO.Path]::GetFullPath($PathValue)
}

$repoRoot = Resolve-FullPath (Join-Path $PSScriptRoot "..")
if ([string]::IsNullOrWhiteSpace($TemplatePath)) {
    $TemplatePath = Join-Path $repoRoot "research-memory-template"
}

$templateRoot = Resolve-FullPath $TemplatePath
$memoryRoot = Resolve-FullPath $MemoryPath

if (-not (Test-Path -LiteralPath $templateRoot -PathType Container)) {
    throw "Memory template does not exist: $templateRoot"
}

New-Item -ItemType Directory -Force -Path $memoryRoot | Out-Null

Get-ChildItem -LiteralPath $templateRoot -Recurse -File |
    Sort-Object FullName |
    ForEach-Object {
        $relative = $_.FullName.Substring($templateRoot.Length).TrimStart("\")
        $destination = Join-Path $memoryRoot $relative
        $destinationDirectory = Split-Path -Parent $destination

        New-Item -ItemType Directory -Force -Path $destinationDirectory |
            Out-Null

        if (Test-Path -LiteralPath $destination) {
            Write-Output "SKIPPED $destination"
        }
        else {
            Copy-Item -LiteralPath $_.FullName -Destination $destination
            Write-Output "CREATED $destination"
        }
    }

Write-Output "Research memory ready: $memoryRoot"
