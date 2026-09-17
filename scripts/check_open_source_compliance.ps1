# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

[CmdletBinding()]
param()

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$failures = [System.Collections.Generic.List[string]]::new()
$requiredFiles = @(
    "LICENSE", "NOTICE", "README.md", "CHANGELOG.md", "DEPENDENCIES.md",
    "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
    "backend/.env.example", "docs/ARCHITECTURE.md", "docs/AI_SYSTEM.md",
    "docs/BUILD_AND_DEPLOYMENT.md", "docs/TESTING.md",
    "docs/PRIVACY_AND_RESPONSIBLE_AI.md", "docs/DEMO_GUIDE.md",
    "docs/COMPETITION_CHECKLIST.md"
)

Push-Location $repositoryRoot
try {
    git rev-parse --is-inside-work-tree 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $allFiles = @(git ls-files --cached --others --exclude-standard)
    } else {
        $global:LASTEXITCODE = 0
        $allFiles = @(Get-ChildItem -Recurse -File | ForEach-Object { [System.IO.Path]::GetRelativePath($repositoryRoot, $_.FullName).Replace('\', '/') })
    }
    foreach ($relativePath in $requiredFiles) {
        if (-not (Test-Path -LiteralPath $relativePath -PathType Leaf)) {
            $failures.Add("Missing required file: $relativePath")
        }
    }

    $codeFiles = @($allFiles | Where-Object { $_ -match '\.(py|js|jsx|css|ps1)$' })
    foreach ($relativePath in $codeFiles) {
        if (-not (Select-String -LiteralPath $relativePath -SimpleMatch "SPDX-License-Identifier: MIT" -Quiet)) {
            $failures.Add("Missing SPDX header: $relativePath")
        }
    }

    $forbiddenTracked = $allFiles | Where-Object {
        $_ -match '(^|/)(node_modules|venv|dist)(/|$)' -or
        $_ -match '\.(db|sqlite|sqlite3|rar|zip)$' -or
        $_ -match '(^|/)\.env$'
    }
    foreach ($relativePath in $forbiddenTracked) {
        $failures.Add("Forbidden generated or sensitive file is tracked: $relativePath")
    }

    if (Select-String -LiteralPath "backend/requirements.txt" -Pattern '^pymupdf' -Quiet) {
        $failures.Add("PyMuPDF is not accepted in the MIT dependency set; use pdfplumber.")
    }

    if ($failures.Count -gt 0) {
        $failures | ForEach-Object { Write-Error $_ }
        exit 1
    }

    Write-Output "Open-source compliance checks passed for $($codeFiles.Count) tracked code files."
}
finally {
    Pop-Location
}
