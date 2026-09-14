# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

[CmdletBinding()]
param(
    [ValidateSet('Archive', 'WorkingTree')]
    [string]$SourceMode = 'Archive',
    [switch]$SkipInstall,
    [switch]$KeepWorkspace,
    [string]$RecordPath = ''
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Split-Path -Parent $PSScriptRoot)).Path
$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$cleanRoot = Join-Path $tempRoot ("ResumeScreeningAI-CleanRoom-" + [guid]::NewGuid().ToString('N'))
$startedAt = Get-Date
$sourceCommit = (git -C $repoRoot rev-parse HEAD)
$originalTemp = $env:TEMP
$originalTmp = $env:TMP
$steps = [System.Collections.Generic.List[object]]::new()

function Invoke-Gate {
    param([string]$Name, [scriptblock]$Action)
    $stepStart = Get-Date
    & $Action
    if ($LASTEXITCODE -ne 0) { throw "$Name failed with exit code $LASTEXITCODE" }
    $steps.Add([pscustomobject]@{ name = $Name; status = 'PASSED'; seconds = [math]::Round(((Get-Date) - $stepStart).TotalSeconds, 2) })
}

New-Item -ItemType Directory -Path $cleanRoot | Out-Null
try {
    if ($SourceMode -eq 'Archive') {
        $archivePath = Join-Path $cleanRoot 'source.tar'
        Push-Location $repoRoot
        try { git archive --format=tar --output=$archivePath HEAD; if ($LASTEXITCODE -ne 0) { throw 'git archive failed' } }
        finally { Pop-Location }
        tar -xf $archivePath -C $cleanRoot
        Remove-Item -LiteralPath $archivePath
    } else {
        Push-Location $repoRoot
        try { $sourceFiles = @(git ls-files --cached --others --exclude-standard) }
        finally { Pop-Location }
        foreach ($relativePath in $sourceFiles) {
            $source = Join-Path $repoRoot $relativePath
            if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { continue }
            $destination = Join-Path $cleanRoot $relativePath
            $destinationDirectory = Split-Path -Parent $destination
            if (-not (Test-Path -LiteralPath $destinationDirectory)) { New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null }
            Copy-Item -LiteralPath $source -Destination $destination
        }
    }

    $env:OFFLINE_MODE = 'true'
    $env:DISABLE_EMBEDDING_MODEL = 'true'
    $env:GEMINI_API_KEY = ''
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $testTemp = Join-Path $cleanRoot '.test-tmp'
    New-Item -ItemType Directory -Path $testTemp | Out-Null
    $env:TEMP = $testTemp
    $env:TMP = $testTemp

    Push-Location $cleanRoot
    try {
        Invoke-Gate 'release-safety' { & './scripts/check_release_safety.ps1' }
        Invoke-Gate 'open-source-compliance' { & './scripts/check_open_source_compliance.ps1' }
        Copy-Item -LiteralPath 'backend/.env.example' -Destination 'backend/.env'

        $pythonPath = Join-Path $cleanRoot '.clean-venv/Scripts/python.exe'
        if (-not $SkipInstall) {
            Invoke-Gate 'python-venv' { python -m venv '.clean-venv' }
            Invoke-Gate 'backend-dependencies' { & $pythonPath -m pip install --disable-pip-version-check -r 'backend/requirements.txt' }
            Invoke-Gate 'frontend-dependencies' { Push-Location 'frontend'; try { npm ci } finally { Pop-Location } }
        } elseif (-not (Test-Path -LiteralPath $pythonPath)) {
            throw '-SkipInstall chỉ dùng được khi clean workspace đã có dependency; workspace mới hiện chưa có.'
        }

        Invoke-Gate 'backend-tests' { Push-Location 'backend'; try { & $pythonPath -m pytest -q -p no:cacheprovider } finally { Pop-Location } }
        Invoke-Gate 'ai-benchmark' { & $pythonPath 'scripts/run_ai_benchmark.py' --dataset 'competition-v1' --output-dir 'artifacts/benchmark' --release-version '1.1.0-competition' --commit-sha $sourceCommit.Substring(0, 7) }
        Invoke-Gate 'frontend-tests' { Push-Location 'frontend'; try { npm test -- --run } finally { Pop-Location } }
        Invoke-Gate 'frontend-build' { Push-Location 'frontend'; try { npm run build } finally { Pop-Location } }
        Invoke-Gate 'showcase-e2e' { Push-Location 'frontend'; try { npm run test:e2e } finally { Pop-Location } }
    }
    finally { Pop-Location }

    $record = [ordered]@{
        status = 'PASSED'
        source_mode = $SourceMode
        source_commit = $sourceCommit
        started_at = $startedAt.ToUniversalTime().ToString('o')
        completed_at = (Get-Date).ToUniversalTime().ToString('o')
        duration_minutes = [math]::Round(((Get-Date) - $startedAt).TotalMinutes, 2)
        offline_mode = $true
        workspace = $cleanRoot
        steps = $steps
    }
    $json = $record | ConvertTo-Json -Depth 5
    Write-Output $json
    if ($RecordPath) {
        $resolvedRecord = if ([System.IO.Path]::IsPathRooted($RecordPath)) { $RecordPath } else { Join-Path $repoRoot $RecordPath }
        $json | Set-Content -LiteralPath $resolvedRecord -Encoding utf8
    }
}
finally {
    $env:TEMP = $originalTemp
    $env:TMP = $originalTmp
    if (-not $KeepWorkspace -and (Test-Path -LiteralPath $cleanRoot)) {
        $resolvedClean = [System.IO.Path]::GetFullPath($cleanRoot)
        if (-not $resolvedClean.StartsWith($tempRoot, [System.StringComparison]::OrdinalIgnoreCase) -or -not (Split-Path -Leaf $resolvedClean).StartsWith('ResumeScreeningAI-CleanRoom-')) {
            throw "Refusing to remove unexpected path: $resolvedClean"
        }
        Remove-Item -LiteralPath $resolvedClean -Recurse -Force
    }
}
