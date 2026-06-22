# run.ps1 -- pokretanje/build DZ1 "Planeta Zemlja" (OpenGL 4, JogAmp + JOML).
#
# Auto-detektuje Maven i JDK: prvo sa PATH-a, pa iz IntelliJ IDEA / JetBrains
# Toolbox instalacije (jer na ovoj masini mvn/java nisu na PATH-u).
#
#   .\run.ps1            # interaktivni meni
#   .\run.ps1 run        # build + pokreni simulaciju  (mvn compile exec:java)
#   .\run.ps1 build      # samo build/jar              (mvn package)
#   .\run.ps1 clean      # ocisti target/              (mvn clean)
#   .\run.ps1 check      # prikazi koje mvn/java koristi (+ verzije)
param(
    [string]$Command = "menu"
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$pom = Join-Path $root "pom.xml"

# --- pronadji java.exe (vrati koren JDK-a za JAVA_HOME) ---
function Resolve-JavaHome {
    $cmd = Get-Command java -ErrorAction SilentlyContinue
    if ($cmd) { return (Split-Path (Split-Path $cmd.Source -Parent) -Parent) }
    if ($env:JAVA_HOME -and (Test-Path (Join-Path $env:JAVA_HOME "bin\java.exe"))) { return $env:JAVA_HOME }
    $roots = @(
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA\jbr",
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA Community Edition\jbr"
    )
    foreach ($r in $roots) { if (Test-Path (Join-Path $r "bin\java.exe")) { return $r } }
    # JetBrains Toolbox / ostalo: potrazi bilo koji jbr/bin/java.exe
    $hit = Get-ChildItem "$env:LOCALAPPDATA\Programs","$env:LOCALAPPDATA\JetBrains" -Recurse -Filter java.exe -ErrorAction SilentlyContinue |
           Where-Object { $_.FullName -match '\\jbr\\bin\\java\.exe$' } | Select-Object -First 1
    if ($hit) { return (Split-Path (Split-Path $hit.FullName -Parent) -Parent) }
    return $null
}

# --- pronadji mvn(.cmd) ---
function Resolve-Mvn {
    $cmd = Get-Command mvn -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $roots = @(
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA\plugins\maven\lib\maven3\bin\mvn.cmd",
        "$env:LOCALAPPDATA\Programs\IntelliJ IDEA Community Edition\plugins\maven\lib\maven3\bin\mvn.cmd"
    )
    foreach ($r in $roots) { if (Test-Path $r) { return $r } }
    $hit = Get-ChildItem "$env:LOCALAPPDATA\Programs","$env:LOCALAPPDATA\JetBrains" -Recurse -Filter mvn.cmd -ErrorAction SilentlyContinue |
           Select-Object -First 1
    if ($hit) { return $hit.FullName }
    return $null
}

$javaHome = Resolve-JavaHome
$mvn = Resolve-Mvn

if (-not $javaHome) { Write-Host "Nije pronadjen JDK. Instaliraj JDK 9+ ili otvori projekat u IntelliJ-u." -ForegroundColor Red; exit 1 }
if (-not $mvn)      { Write-Host "Nije pronadjen Maven. Instaliraj Maven ili koristi IntelliJ-ev bundlovani." -ForegroundColor Red; exit 1 }
$env:JAVA_HOME = $javaHome

function Invoke-Mvn([string[]]$mvnArgs) {
    Write-Host ">> mvn $($mvnArgs -join ' ')" -ForegroundColor Cyan
    Write-Host "   JAVA_HOME = $javaHome" -ForegroundColor DarkGray
    & $mvn -f $pom @mvnArgs
}

function Show-Menu {
    Write-Host ""
    Write-Host "  DZ1 - Planeta Zemlja (OpenGL 4)" -ForegroundColor Green
    Write-Host "  --------------------------------"
    Write-Host "   1) run    - build + pokreni simulaciju"
    Write-Host "   2) build  - samo build (package)"
    Write-Host "   3) clean  - ocisti target/"
    Write-Host "   4) check  - alati i verzije"
    Write-Host "   0) izlaz"
    Write-Host ""
    $sel = Read-Host "Izbor"
    switch ($sel) {
        "1" { Invoke-Mvn @("compile", "exec:java") }
        "2" { Invoke-Mvn @("package") }
        "3" { Invoke-Mvn @("clean") }
        "4" { Cmd-Check }
        "0" { return }
        default { Write-Host "Nepoznat izbor." -ForegroundColor Yellow }
    }
}

function Cmd-Check {
    Write-Host "mvn  : $mvn" -ForegroundColor Cyan
    Write-Host "java : $javaHome\bin\java.exe" -ForegroundColor Cyan
    & "$javaHome\bin\java.exe" -version
    Invoke-Mvn @("-v")
}

switch ($Command.ToLower()) {
    "menu"  { Show-Menu }
    "run"   { Invoke-Mvn @("compile", "exec:java") }
    "build" { Invoke-Mvn @("package") }
    "clean" { Invoke-Mvn @("clean") }
    "check" { Cmd-Check }
    default { Write-Host "Nepoznata komanda '$Command'. Koristi: run | build | clean | check (ili bez argumenta za meni)." -ForegroundColor Yellow }
}
