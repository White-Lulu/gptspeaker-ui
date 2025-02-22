@echo off
cd /d "%~dp0"

call .venv\Scripts\activate

start /min cmd /c "python server.py"

timeout /t 2 >nul

start "" "http://localhost:5000/static/speaker.html"