@echo off
REM run-game.bat -- build standalone playera u Build\ pa ga pokrece.
REM Trazi zatvoren Unity Editor, jer batch build ne moze preko zakljucanog projekta.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run.ps1" game
