@echo off
cd /d "%~dp0"
py frontend_usuario\app_usuario.py
if errorlevel 1 python frontend_usuario\app_usuario.py
pause
