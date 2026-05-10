@echo off
:: ============================================================
:: uninstall.bat  —  wsl-mcp-shutdown uninstaller
:: ============================================================

setlocal
set "REPO_DIR=%~dp0"
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\wsl-mcp-shutdown.bat"

echo.
echo  Removing startup shortcut...
if exist "%SHORTCUT%" (
    del /f /q "%SHORTCUT%"
    echo  Removed: %SHORTCUT%
) else (
    echo  Shortcut not found — already removed.
)

echo.
echo  Removing virtual environment...
if exist "%REPO_DIR%.venv" (
    rmdir /s /q "%REPO_DIR%.venv"
    echo  Removed: .venv
) else (
    echo  .venv not found — already removed.
)

echo.
echo  Removing generated launcher...
if exist "%REPO_DIR%start_mcp.bat" (
    del /f /q "%REPO_DIR%start_mcp.bat"
    echo  Removed: start_mcp.bat
)

echo.
echo  Uninstall complete.
echo  The repo folder itself has NOT been deleted.
echo.
