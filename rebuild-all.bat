@echo off
chcp 65001 >nul
title Rebuild reactbits-all-in-one
echo.
echo   Rebuilding reactbits-all-in-one.html ...
echo.
"C:\Users\18629\.workbuddy\binaries\python\envs\default\Scripts\python.exe" "%~dp0tools\build_all_in_one.py"
echo.
echo   Done. Press any key to close.
pause >nul
