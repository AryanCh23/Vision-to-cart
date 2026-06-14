@echo off
echo ====================================================
echo  Vision-to-Cart V4 — Docker Build and Run
echo ====================================================
echo.
echo [1/3] Building Docker image...
docker compose build --no-cache
if %ERRORLEVEL% neq 0 (
    echo ERROR: Docker build failed. Make sure Docker Desktop is running.
    pause
    exit /b 1
)

echo.
echo [2/3] Starting all services...
docker compose up -d
if %ERRORLEVEL% neq 0 (
    echo ERROR: docker compose up failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Checking service status...
timeout /t 5 /nobreak >nul
docker compose ps

echo.
echo ====================================================
echo  Services are running!
echo  - MCP API Server : http://localhost:8000
echo  - Frontend UI    : http://localhost:3000
echo  - API Docs       : http://localhost:8000/docs
echo ====================================================
echo.
echo Press any key to view live logs (Ctrl+C to stop logs, services keep running)
pause >nul
docker compose logs -f
