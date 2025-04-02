@echo off
set "EXE_PATH=C:\Auto-Login-BMAAP\Login-encrypt.exe"  REM Change this to the actual path
set "SHORTCUT_PATH=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\Login-encrypt.lnk"

:: Create the shortcut using PowerShell
powershell -command "$WScriptShell = New-Object -ComObject WScript.Shell; $Shortcut = $WScriptShell.CreateShortcut('%SHORTCUT_PATH%'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.WorkingDirectory = [System.IO.Path]::GetDirectoryName('%EXE_PATH%'); $Shortcut.Save()"

echo Shortcut added to Startup folder successfully!
pause
