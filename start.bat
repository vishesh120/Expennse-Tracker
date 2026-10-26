@echo off
echo ====================================================
echo Starting AI Smart Expense Tracker (Backend + Frontend)
echo ====================================================

echo 1. Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "Backend - FastAPI" python run.py

echo 2. Starting React Vite Frontend on http://127.0.0.1:5173 ...
cd frontend
npm run dev
