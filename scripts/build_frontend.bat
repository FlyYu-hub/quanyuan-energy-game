@echo off
cd /d %~dp0\..\frontend
npm install
npm run build
pause
