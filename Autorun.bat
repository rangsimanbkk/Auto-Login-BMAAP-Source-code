@echo off

set LOG_FILE="log.txt"

:CHECK_CONNECTION
set TIMESTAMP=%date% %time%
curl -s --head https://www.google.com >nul 2>&1
IF %ERRORLEVEL% EQU 0 (
    echo %TIMESTAMP% - Internet connection is working. Skipping login script. >> %LOG_FILE%
    echo %TIMESTAMP% - Internet connection is working. Skipping login script.
) ELSE (
    echo %TIMESTAMP% - Internet connection is not working. Running login script... >> %LOG_FILE%
    echo %TIMESTAMP% - Internet connection is not working. Running login script...
    REM Replace with your Python script path
    python C:\Auto-Login-BMAAP\Wifi-Login.py
)

timeout /t 60 /nobreak >nul
goto CHECK_CONNECTION