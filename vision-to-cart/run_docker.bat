@echo off
cd /d "%~dp0"
echo Building and starting Vision-to-Cart V4 Docker services... > docker_run_output.log
docker compose build >> docker_run_output.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker build failed. >> docker_run_output.log
    exit /b %ERRORLEVEL%
)
docker compose up -d >> docker_run_output.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo Docker compose up failed. >> docker_run_output.log
    exit /b %ERRORLEVEL%
)
echo Checking status: >> docker_run_output.log
docker compose ps >> docker_run_output.log 2>&1
echo Done. >> docker_run_output.log
