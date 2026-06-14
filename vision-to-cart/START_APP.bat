@echo off
title Vision-to-Cart Launcher
cd /d "%~dp0"

echo ============================================
echo   Vision-to-Cart V4 - Docker Stack Launcher
echo ============================================
echo.

:: Check Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.
echo [STEP 1] Stopping any existing containers...
docker compose down --remove-orphans

echo.
echo [STEP 2] Building and starting all services...
echo    - vision_cart_api   (FastAPI MCP Server) -> http://localhost:8000
echo    - vision_cart_frontend (nginx UI)        -> http://localhost:3000
echo    - vision_cart_redis  (Cache)             -> localhost:6379
echo.
docker compose up --build -d

if errorlevel 1 (
    echo.
    echo [ERROR] Docker Compose failed! Check the output above.
    pause
    exit /b 1
)

echo.
echo [STEP 3] Waiting 15 seconds for services to initialize...
timeout /t 15 /nobreak

echo.
echo [STEP 4] Checking container status...
docker compose ps

echo.
echo [STEP 5] Checking API health...
docker compose logs mcp-server --tail 20

echo.
echo ============================================
echo   App should be available at:
echo   Frontend : http://localhost:3000
echo   API      : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo ============================================
echo.
pause
