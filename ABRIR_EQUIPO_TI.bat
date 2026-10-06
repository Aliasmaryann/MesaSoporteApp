@echo off
cd /d "%~dp0"
py frontend_ti\app_ti.py
if errorlevel 1 python frontend_ti\app_ti.py
pause
