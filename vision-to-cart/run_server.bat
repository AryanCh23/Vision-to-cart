@echo off
echo ====================================================
echo  Vision-to-Cart V4 MCP Server
echo ====================================================
echo.
echo Installing required packages...
"C:\Program Files\PostgreSQL\16\pgAdmin 4\python\python.exe" -m pip install fastapi uvicorn[standard] --quiet
echo.
echo Starting FastAPI MCP Server on http://localhost:8000
echo Press Ctrl+C to stop.
echo.
"C:\Program Files\PostgreSQL\16\pgAdmin 4\python\python.exe" -m uvicorn mcp_server.main:app --host 0.0.0.0 --port 8000 --reload
pause
