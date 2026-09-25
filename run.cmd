@echo off
setlocal
cd /d "%~dp0"

where docker >nul 2>&1
if errorlevel 1 (
  echo Docker was not found. Install Docker Desktop, start it, then run this command again.
  exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
  echo Docker is installed but not running. Start Docker Desktop, then try again.
  exit /b 1
)

docker build -t warehouse-project-template .
if errorlevel 1 exit /b 1

docker run --rm -v "%cd%:/workspace" -w /workspace warehouse-project-template python pipeline.py %*
exit /b %errorlevel%
