@echo off
chcp 65001 >nul
title Auto rebuild - reactbits-all-in-one
echo.
echo   Watching the four component pages for changes...
echo   Keep this window open. Press Ctrl+C to stop.
echo.
"C:\Users\18629\.workbuddy\binaries\python\envs\default\Scripts\python.exe" "%~dp0tools\watch_and_rebuild.py"
echo.
pause >nul
