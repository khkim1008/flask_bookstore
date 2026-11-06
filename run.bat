@echo off
chcp 65001 > nul
echo ===================================================
echo [도서관리시스템] Flask 웹서비스를 시작합니다...
echo 접속 주소: http://localhost:5000
echo 종료하려면 창을 닫거나 Ctrl+C를 누르세요.
echo ===================================================
python app.py
pause
