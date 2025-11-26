@echo off
conda activate web
title DeepSeek Backend Launcher

echo ========================================================
echo        DeepSeek Project One-Click Launcher
echo ========================================================
echo.

:: 1. 启动 Redis
:: 如果你的 redis-server 不在环境变量里，请写绝对路径，例如 "C:\Redis\redis-server.exe"
echo [1/3] Starting Redis...
start "Redis Server" redis-server

:: 等待 2 秒确保 Redis 启动
timeout /t 2 >nul

:: 2. 启动 Celery Worker
:: Windows 下必须加 -P eventlet，否则无法支持并发
echo [2/3] Starting Celery Worker...
start "Celery Worker" celery -A worker.celery_app worker --loglevel=info -P eventlet

:: 3. 启动 FastAPI
echo [3/3] Starting FastAPI...
start "FastAPI Web" uvicorn main:app --reload --port 8000

echo.
echo ========================================================
echo  SUCCESS! All services started in new windows.
echo  Swagger UI: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause