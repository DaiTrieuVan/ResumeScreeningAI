# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

[CmdletBinding()]
param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath $Root).Path
$failures = [System.Collections.Generic.List[string]]::new()

Push-Location $repoRoot
try {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $tracked = @(git ls-files --cached --others --exclude-standard)
    } else {
        $tracked = @(Get-ChildItem -Recurse -File | ForEach-Object { [System.IO.Path]::GetRelativePath($repoRoot, $_.FullName).Replace('\', '/') })
    }

    $forbiddenTracked = @(
        $tracked | Where-Object {
            $_ -match '(^|/)(output|dist|build|test-results|playwright-report|evaluation/(private|raw))/' -or
            ($_ -match '(^|/)(storage|backend/storage)/' -and $_ -notmatch '\.gitkeep$') -or
            ($_ -match '(?i)(\.db|\.sqlite3?|\.pdf|\.docx?|\.pem|\.key|\.p12|\.pfx|\.zip|\.tar\.gz|\.rar)$') -or
            ($_ -match '(^|/)\.env($|\.)' -and $_ -notmatch '\.env\.example$')
        }
    )
    foreach ($path in $forbiddenTracked) { $failures.Add("Tracked release artifact/sensitive file: $path") }

    $secretPattern = '(?i)(api[_-]?key|client[_-]?secret|password|access[_-]?token|private[_-]?key)[ \t]*[:=][ \t]*["'']?([A-Za-z0-9_+\-/=]{12,})'
    $privateKeyPattern = '-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
    foreach ($path in $tracked) {
        $fullPath = Join-Path $repoRoot $path
        if (-not (Test-Path -LiteralPath $fullPath -PathType Leaf)) { continue }
        if ($path -match '(?i)\.(png|jpe?g|gif|ico|woff2?|ttf|zip|gz)$') { continue }
        $content = Get-Content -LiteralPath $fullPath -Raw -ErrorAction SilentlyContinue
        if ($null -eq $content) { continue }
        if ($content -match $privateKeyPattern) { $failures.Add("Private key marker found: $path") }
        foreach ($match in [regex]::Matches($content, $secretPattern)) {
            $value = $match.Groups[2].Value
            if ($value -notmatch '(?i)^(example|placeholder|changeme|your[_-])') {
                $failures.Add("Possible embedded secret in $path")
                break
            }
        }
    }

    $manifestPath = Join-Path $repoRoot 'evaluation/datasets/competition-v1/manifest.json'
    if (-not (Test-Path -LiteralPath $manifestPath)) {
        $failures.Add('Missing published synthetic evaluation manifest.')
    } else {
        try { $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json }
        catch { $failures.Add('Evaluation manifest is not valid JSON.'); $manifest = $null }
        if ($manifest) {
            if ($manifest.provenance.kind -ne 'SYNTHETIC') { $failures.Add('Evaluation provenance must be SYNTHETIC.') }
            if ([string]::IsNullOrWhiteSpace($manifest.provenance.statement)) { $failures.Add('Synthetic provenance statement is required.') }
            if (@($manifest.jobs).Count -lt 3) { $failures.Add('Evaluation dataset must contain at least 3 jobs.') }
            if (@($manifest.candidates).Count -lt 30) { $failures.Add('Evaluation dataset must contain at least 30 candidates.') }
            if (@($manifest.candidates | Where-Object { $_.id -notmatch '^(be|da|po)-\d{2}$' }).Count -gt 0) {
                $failures.Add('Evaluation candidate identifiers must remain synthetic IDs.')
            }
        }
    }

    if ($failures.Count) {
        $failures | ForEach-Object { Write-Error $_ }
        exit 1
    }
    Write-Output "Release safety checks passed for $($tracked.Count) tracked files; dataset is synthetic (3+ jobs, 30+ candidates)."
}
finally {
    Pop-Location
}
