@echo off
cd /d "%~dp0"

REM 激活虚拟环境
call .venv\Scripts\activate

REM 启动服务器
start /min cmd /c "python server.py"

REM 等待2秒
timeout /t 2 >nul

REM 打开网页
start "" "http://localhost:5000/static/speaker.html"