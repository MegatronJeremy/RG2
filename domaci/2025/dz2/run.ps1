# run.ps1 -- pokretanje DZ2 "Vodena povrs" (Unity, Built-in RP).
#
# Auto-detektuje Unity editor cija verzija odgovara ProjectSettings/ProjectVersion.txt:
# prvo standardna Hub putanja, pa klasicna instalacija, pa bilo koja 2022.3.x kao rezerva.
#
#   .\run.ps1            # interaktivni meni
#   .\run.ps1 editor     # otvori projekat u Unity Editoru (scena Water), Play se pritiska rucno
#   .\run.ps1 game       # build standalone playera + pokreni ga
#   .\run.ps1 build      # samo build playera u Build\
#   .\run.ps1 check      # prikazi koji Unity se koristi (+ verzija projekta)
param(
    [string]$Command = "menu"
)
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$playerExe = Join-Path $root "Build\DZ2.exe"
$logFile = Join-Path $root "Build\build.log"

function Get-ProjectVersion {
    $file = Join-Path $root "ProjectSettings\ProjectVersion.txt"
    if (-not (Test-Path $file)) { return $null }
    $line = Select-String -Path $file -Pattern '^m_EditorVersion:\s*(.+)$' | Select-Object -First 1
    if ($line) { return $line.Matches[0].Groups[1].Value.Trim() }
    return $null
}

function Resolve-Unity([string]$version) {
    $candidates = @()
    if ($version) {
        $candidates += "$env:ProgramFiles\Unity\Hub\Editor\$version\Editor\Unity.exe"
        $candidates += "$env:ProgramFiles\Unity $version\Editor\Unity.exe"
    }
    foreach ($c in $candidates) { if (Test-Path $c) { return $c } }

    # Rezerva: bilo koji instaliran editor iste major.minor linije.
    $fallback = Get-Item "$env:ProgramFiles\Unity\Hub\Editor\*\Editor\Unity.exe",
                         "$env:ProgramFiles\Unity 20*\Editor\Unity.exe" -ErrorAction SilentlyContinue |
                Select-Object -First 1
    if ($fallback) { return $fallback.FullName }
    return $null
}

$projectVersion = Get-ProjectVersion
$unity = Resolve-Unity $projectVersion

if (-not $unity) {
    Write-Host "Nije pronadjen Unity editor $projectVersion. Instaliraj ga kroz Unity Hub." -ForegroundColor Red
    exit 1
}

# Editor drzi projekat zakljucanim; drugi proces na istom projektu puca ili ceka.
function Test-EditorRunning {
    $lock = Join-Path $root "Temp\UnityLockfile"
    if (-not (Test-Path $lock)) { return $false }
    try {
        $stream = [System.IO.File]::Open($lock, 'Open', 'ReadWrite', 'None')
        $stream.Close()
        return $false
    } catch {
        return $true
    }
}

function Cmd-Editor {
    if (Test-EditorRunning) {
        Write-Host "Unity vec drzi ovaj projekat otvoren; prebaci se na taj prozor." -ForegroundColor Yellow
        return
    }
    Write-Host ">> otvaram projekat u Unity Editoru (Play se pritiska rucno)" -ForegroundColor Cyan
    Write-Host "   $unity" -ForegroundColor DarkGray
    # Unity nema CLI opciju koja otvara scenu (-openfile se ignorise), pa scenu otvara
    # editor metoda; bez toga svez checkout starta na praznoj "Untitled" sceni.
    Start-Process -FilePath $unity -ArgumentList @(
        "-projectPath", $root,
        "-executeMethod", "SceneLauncher.OpenWaterScene"
    )
}

function Cmd-Build {
    if (Test-EditorRunning) {
        Write-Host "Unity drzi projekat otvoren; zatvori editor pre build-a." -ForegroundColor Yellow
        return $false
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $playerExe -Parent) | Out-Null
    Write-Host ">> build standalone playera -> $playerExe" -ForegroundColor Cyan
    Write-Host "   log: $logFile" -ForegroundColor DarkGray

    # Unity.exe je GUI aplikacija: pozvan preko "&" ne blokira konzolu i $LASTEXITCODE
    # ostaje prazan. Start-Process -Wait ceka kraj i daje stvarni exit kod.
    $proc = Start-Process -FilePath $unity -Wait -PassThru -ArgumentList @(
        "-batchmode", "-quit",
        "-projectPath", $root,
        "-executeMethod", "PlayerBuild.BuildFromCommandLine",
        "-buildOutput", $playerExe,
        "-logFile", $logFile
    )
    $code = $proc.ExitCode

    if ($code -ne 0 -or -not (Test-Path $playerExe)) {
        Write-Host "Build nije uspeo (exit $code). Poslednje greske iz loga:" -ForegroundColor Red
        if (Test-Path $logFile) {
            Select-String -Path $logFile -Pattern 'error CS|Shader error|BuildFailedException|RG2 build:' |
                Select-Object -Last 15 | ForEach-Object { Write-Host "   $($_.Line)" -ForegroundColor DarkGray }
        }
        return $false
    }

    Write-Host "Build OK." -ForegroundColor Green
    return $true
}

function Cmd-Game {
    if (-not (Cmd-Build)) { return }
    Write-Host ">> pokrecem player (Esc/Alt+F4 za izlaz)" -ForegroundColor Cyan
    Start-Process -FilePath $playerExe -ArgumentList @(
        "-screen-fullscreen", "0", "-screen-width", "1280", "-screen-height", "720"
    )
}

function Cmd-Check {
    Write-Host "projekat : $root" -ForegroundColor Cyan
    Write-Host "verzija  : $projectVersion (iz ProjectVersion.txt)" -ForegroundColor Cyan
    Write-Host "unity    : $unity" -ForegroundColor Cyan
    Write-Host "editor otvoren: $(Test-EditorRunning)" -ForegroundColor Cyan
    if (Test-Path $playerExe) {
        Write-Host "player   : $playerExe ($(( Get-Item $playerExe ).LastWriteTime))" -ForegroundColor Cyan
    } else {
        Write-Host "player   : nije build-ovan" -ForegroundColor DarkGray
    }
}

function Show-Menu {
    Write-Host ""
    Write-Host "  DZ2 - Vodena povrs (Unity)" -ForegroundColor Green
    Write-Host "  --------------------------"
    Write-Host "   1) editor - otvori projekat u Unity Editoru"
    Write-Host "   2) game   - build + pokreni standalone player"
    Write-Host "   3) build  - samo build playera"
    Write-Host "   4) check  - koji Unity/verzija se koristi"
    Write-Host "   0) izlaz"
    Write-Host ""
    switch (Read-Host "Izbor") {
        "1" { Cmd-Editor }
        "2" { Cmd-Game }
        "3" { Cmd-Build | Out-Null }
        "4" { Cmd-Check }
        "0" { return }
        default { Write-Host "Nepoznat izbor." -ForegroundColor Yellow }
    }
}

switch ($Command.ToLower()) {
    "menu"   { Show-Menu }
    "editor" { Cmd-Editor }
    "game"   { Cmd-Game }
    "build"  { Cmd-Build | Out-Null }
    "check"  { Cmd-Check }
    default  { Write-Host "Nepoznata komanda '$Command'. Koristi: editor | game | build | check." -ForegroundColor Yellow }
}
