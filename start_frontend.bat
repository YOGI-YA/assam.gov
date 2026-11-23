@echo off
title gov.guide Frontend (Next.js)
echo ======================================================
echo Starting gov.guide Frontend on http://localhost:3000
echo AI Chat URL: http://localhost:3000/chat
echo ======================================================
cd /d "%~dp0frontend"
npm run dev
pause
