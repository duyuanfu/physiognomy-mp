@echo off
title Facial Architecture API
cd /d "%~dp0backend"
echo ========================================================
echo  FACIAL ARCHITECTURE // FastAPI Server Starting...
echo ========================================================
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 75 --reload
pause
