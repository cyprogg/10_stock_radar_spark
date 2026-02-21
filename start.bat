@echo off
REM 동적 웹 서버 시작 및 index.html 자동 실행
cd /d %~dp0
REM 서버 실행 및 대시보드 자동 오픈
cd backend
start uvicorn server:app --host 0.0.0.0 --port 8125
cd ..
start http://localhost:8125/
