@echo off
title gov.guide Backend (FastAPI / Uvicorn)
echo ======================================================
echo Starting gov.guide Backend on http://127.0.0.1:8000
echo API Documentation: http://127.0.0.1:8000/docs
echo ======================================================
cd /d "%~dp0backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
