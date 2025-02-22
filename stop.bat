@echo off
if not exist server.pid (
    echo server.pid 文件不存在，服务器可能未启动。
    exit
)

set /p pid=<server.pid
taskkill /f /pid %pid%
del server.pid
