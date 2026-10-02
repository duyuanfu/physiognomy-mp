@echo off
title Build WeChat Mini-Program for Release
cd /d "%~dp0frontend"

echo ========================================================
echo  [阅骨见神] 正在进行微信小程序正式生产打包...
echo ========================================================
call npm run build:mp-weixin

echo.
echo ========================================================
echo  打包完成！正式代码已输出至:
echo  frontend\dist\build\mp-weixin
echo ========================================================
pause
