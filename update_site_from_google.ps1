param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

Write-Host "Updating publications in index.html from Google Scholar..."
& $Python -u "scripts\update_from_scholar.py"

Write-Host "Generating cv.html from index.html..."
& $Python -u "scripts\generate_cv.py"

Write-Host "Done."

