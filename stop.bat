@echo off
if not exist server.pid (
    echo server.pid No file exits.
    exit
)

set /p pid=<server.pid
taskkill /f /pid %pid%
del server.pid
