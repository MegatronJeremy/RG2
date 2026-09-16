# run.ps1 -- pokretanje/build DZ1 "Planeta Zemlja" (OpenGL 4, JogAmp + JOML).
#
# Auto-detektuje Maven i JDK: prvo sa PATH-a, pa iz samostalne Maven instalacije
# i bilo kog JetBrains IDE-a (Rider, PyCharm, IDEA, Gateway...), jer na ovoj
# masini mvn/java nisu na PATH-u.
#
#   .\run.ps1            # interaktivni meni
#   .\run.ps1 run        # build + pokreni simulaciju  (mvn compile exec:exec)
#   .\run.ps1 build      # samo build/jar              (mvn package)
#   .\run.ps1 clean      # ocisti target/              (mvn clean)
#   .\run.ps1 check      # prikazi koje mvn/java koristi (+ verzije)
param(
    [string]$Command = "menu"
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$pom = Join-Path $root "pom.xml"

# Vrati prvu putanju koja postoji; obrasci sa * se razresavaju wildcard-om
# (npr. "apache-maven-*" pokriva svaku verziju bez zakucavanja broja).
function First-Existing([string[]]$patterns) {
    foreach ($p in $patterns) {
        $hit = Get-Item $p -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($hit) { return $hit.FullName }
    }
    return $null
}

# --- pronadji java.exe (vrati koren JDK-a za JAVA_HOME) ---
function Resolve-JavaHome {
    $cmd = Get-Command java -ErrorAction SilentlyContinue
    if ($cmd) { return (Split-Path (Split-Path $cmd.Source -Parent) -Parent) }
    if ($env:JAVA_HOME -and (Test-Path (Join-Path $env:JAVA_HOME "bin\java.exe"))) { return $env:JAVA_HOME }
    # Svaki JetBrains IDE nosi svoj JBR (JDK 17/21) -- bilo koji je dovoljan za release 9.
    # Ne gadjamo samo IDEA-u: na ovoj masini postoje Rider/PyCharm, ne i IDEA.
    $hit = First-Existing @(
        "$env:LOCALAPPDATA\Programs\*\jbr\bin\java.exe",
        "$env:LOCALAPPDATA\JetBrains\*\jbr\bin\java.exe",
        "$env:ProgramFiles\JetBrains\*\jbr\bin\java.exe",
        "$env:ProgramFiles\Eclipse Adoptium\jdk-*\bin\java.exe",
        "$env:ProgramFiles\Java\jdk-*\bin\java.exe"
    )
    if ($hit) { return (Split-Path (Split-Path $hit -Parent) -Parent) }
    # Poslednja linija odbrane: rekurzivna pretraga (sporo, pa tek ovde).
    $deep = Get-ChildItem "$env:LOCALAPPDATA\Programs","$env:LOCALAPPDATA\JetBrains" -Recurse -Filter java.exe -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match '\\jbr\\bin\\java\.exe$' } | Select-Object -First 1
    if ($deep) { return (Split-Path (Split-Path $deep.FullName -Parent) -Parent) }
    return $null
}

# --- pronadji mvn(.cmd) ---
function Resolve-Mvn {
    $cmd = Get-Command mvn -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    # Ne zvati promenljivu $home -- to je rezervisano ime u PowerShell-u (read-only).
    foreach ($mavenRoot in @($env:MAVEN_HOME, $env:M2_HOME)) {
        if ($mavenRoot -and (Test-Path (Join-Path $mavenRoot "bin\mvn.cmd"))) {
            return (Join-Path $mavenRoot "bin\mvn.cmd")
        }
    }
    # Samostalna instalacija (bilo koja verzija) + Maven koji bundluje IntelliJ IDEA.
    $hit = First-Existing @(
        "C:\Dev\tools\apache-maven-*\bin\mvn.cmd",
        "C:\tools\apache-maven-*\bin\mvn.cmd",
        "$env:ProgramFiles\apache-maven-*\bin\mvn.cmd",
        "$env:LOCALAPPDATA\Programs\*\plugins\maven\lib\maven3\bin\mvn.cmd",
        "$env:LOCALAPPDATA\JetBrains\*\plugins\maven\lib\maven3\bin\mvn.cmd"
    )
    if ($hit) { return $hit }
    $deep = Get-ChildItem "$env:LOCALAPPDATA\Programs","$env:LOCALAPPDATA\JetBrains" -Recurse -Filter mvn.cmd -ErrorAction SilentlyContinue |
            Select-Object -First 1
    if ($deep) { return $deep.FullName }
    return $null
}

$javaHome = Resolve-JavaHome
$mvn = Resolve-Mvn

if (-not $javaHome) { Write-Host "Nije pronadjen JDK. Instaliraj JDK 9+ ili postavi JAVA_HOME." -ForegroundColor Red; exit 1 }
if (-not $mvn) {
    Write-Host "Nije pronadjen Maven. Raspakuj apache-maven u C:\Dev\tools\ ili postavi MAVEN_HOME." -ForegroundColor Red
    exit 1
}
$env:JAVA_HOME = $javaHome

# Iza korporativnog TLS proxyja (npr. Zscaler) JBR-ov cacerts ne veruje presretnutom
# sertifikatu Maven Central-a -> "PKIX path building failed". Windows cert store vec
# ima korenski CA proxyja, pa reci Javi da koristi njega za resolver/preuzimanja.
# (Ne dira se nijedan cacerts fajl; cisto runtime opcija.)
$env:MAVEN_OPTS = ($env:MAVEN_OPTS + " -Djavax.net.ssl.trustStoreType=WINDOWS-ROOT").Trim()

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
        "1" { Invoke-Mvn @("compile", "exec:exec") }
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
    "run"   { Invoke-Mvn @("compile", "exec:exec") }
    "build" { Invoke-Mvn @("package") }
    "clean" { Invoke-Mvn @("clean") }
    "check" { Cmd-Check }
    default { Write-Host "Nepoznata komanda '$Command'. Koristi: run | build | clean | check (ili bez argumenta za meni)." -ForegroundColor Yellow }
}
