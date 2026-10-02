@echo off
title Facial Architecture Mini-Program Weixin Compiler
cd /d "%~dp0frontend"

echo ========================================================
echo  [阅骨见神] Uni-app 微信小程序开发编译监听中...
echo  编译输出目录: frontend\dist\dev\mp-weixin
echo ========================================================
call npm run dev:mp-weixin
pause
