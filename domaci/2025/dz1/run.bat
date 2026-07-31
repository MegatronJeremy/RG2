@echo off
REM run.bat -- wrapper koji poziva run.ps1 (zaobilazi ExecutionPolicy).
REM   run.bat            interaktivni meni
REM   run.bat run        build + pokreni simulaciju
REM   run.bat build      samo build (package)
REM   run.bat clean      ocisti target/
REM   run.bat check      alati i verzije
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" %*
