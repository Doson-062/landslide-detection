@echo off
cd /d "%~dp0"
title Landslide Detection System - Web Server
echo ===================================================
echo     KHOI DONG HE THONG CANH BAO SAT LO (FastAPI)
echo ===================================================
echo.
echo Dang mo Server tai cong 8000 (Localhost)...
echo Nhan Ctrl+C de dung may chu.
echo.

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

pause
