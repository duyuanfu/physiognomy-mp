@echo off
title Facial Architecture Mini-Program Frontend
cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo ========================================================
    echo  [Notice] node_modules not detected. Installing dependencies...
    echo ========================================================
    call npm install
)

echo ========================================================
echo  FACIAL ARCHITECTURE // Uni-app Dev Server Starting...
echo ========================================================
call npm run dev:h5
pause
