@echo off
title SDES ERP Server
color 0A
echo.
echo  ==========================================
echo   SDES ERP - Starting Production Server
echo  ==========================================
echo.
echo  Network URL: http://172.16.2.3:9001
echo.

cd /d E:\Testing\projects\erp_project
python serve.py

echo.
echo  Server stopped.
pause
