@echo off
echo ====================================
echo   Sistema de Compatibilidades - Servidor Dev
echo ====================================
cd /d "%~dp0..\src"
start "Sistema de Compatibilidades - Servidor" cmd /k python run.py
timeout /t 2 /nobreak >nul
start "" http://localhost:5003
