# SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai
# SPDX-License-Identifier: MIT

[CmdletBinding()]
param()

$repositoryRoot = Split-Path -Parent $PSScriptRoot
$copyright = "SPDX-FileCopyrightText: 2026 226789SBTC - Trieu Van Dai"
$license = "SPDX-License-Identifier: MIT"
$utf8NoBom = [System.Text.UTF8Encoding]::new($false)

Push-Location $repositoryRoot
try {
    $trackedCode = git ls-files "*.py" "*.js" "*.jsx" "*.css" "*.ps1"
    foreach ($relativePath in $trackedCode) {
        $absolutePath = Join-Path $repositoryRoot $relativePath
        $content = [System.IO.File]::ReadAllText($absolutePath)
        if ($content.Contains($license)) {
            continue
        }

        if ([System.IO.Path]::GetExtension($absolutePath) -in @(".py", ".ps1")) {
            $header = "# $copyright`r`n# $license`r`n`r`n"
        }
        else {
            $header = "/* $copyright */`r`n/* $license */`r`n`r`n"
        }

        [System.IO.File]::WriteAllText($absolutePath, $header + $content, $utf8NoBom)
        Write-Output $relativePath
    }
}
finally {
    Pop-Location
}
