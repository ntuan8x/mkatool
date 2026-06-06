@echo off
chcp 65001 >nul
:: pre-commit hook: Kiem tra version truoc khi commit
::
:: Bat buoc tat ca cac file sau phai dong nhat version:
::   1. src/config/app_config.py -> VERSION = "x.x.x"
::   2. update.json -> "latest_version": "x.x.x"
::
:: Neu co thay doi code (.py), yeu cau tang version.
::
:: Cach cai dat:
::   copy scripts\pre-commit.bat "%USERPROFILE%\.git\hooks\pre-commit.bat"
:: Hoac tren WSL/Git Bash:
::   cp scripts/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

setlocal enabledelayedexpansion

set "APP_CONFIG=src\config\app_config.py"
set "UPDATE_JSON=update.json"
set "CHANGELOG=CHANGELOG.md"

:: Lay version tu app_config.py
for /f "tokens=2 delims=='" %%a in ('findstr /C:"VERSION = " "%APP_CONFIG%" 2^>nul') do (
    set "VER_CONFIG=%%a"
)
set "VER_CONFIG=%VER_CONFIG:"=%"
set "VER_CONFIG=%VER_CONFIG: =%"

:: Lay version tu update.json
for /f "tokens=2 delims=:" %%a in ('findstr /C:"\"latest_version\"" "%UPDATE_JSON%" 2^>nul') do (
    set "VER_JSON=%%a"
)
set "VER_JSON=%VER_JSON:"=%
set "VER_JSON=%VER_JSON:,=%
set "VER_JSON=%VER_JSON: =%"

:: Kiem tra dong bo
if "%VER_CONFIG%" neq "%VER_JSON%" (
    echo [ERROR] Version mismatch!
    echo   app_config.py: %VER_CONFIG%
    echo   update.json:   %VER_JSON%
    echo   Phai dong bo 2 file ve cung version.
    exit /b 1
)

:: Kiem tra co file .py nao thay doi (ngoai tru config)
git status --porcelain > "%TEMP%\mka_git_status.txt"
findstr /V /C:"%APP_CONFIG%" /C:"%UPDATE_JSON%" /C:"%CHANGELOG%" "%TEMP%\mka_git_status.txt" | findstr /R "\.py$" >nul
set "HAS_CODE=!errorlevel!"

if !HAS_CODE! equ 0 (
    echo.
    echo [CODE CHANGES DETECTED]
    findstr /V /C:"%APP_CONFIG%" /C:"%UPDATE_JSON%" /C:"%CHANGELOG%" "%TEMP%\mka_git_status.txt" | findstr /R "\.py$"
    echo.
    echo Version hien tai: %VER_CONFIG%
    echo.
    echo Ban co muon tang version?
    echo   1. Tang PATCH  - Fix nho
    echo   2. Tang MINOR - Tinh nang moi
    echo   3. Tang MAJOR - Break change
    echo   4. Bo qua     - Chi commit
    echo.
    set /p CHOICE="Chon [1-4]: "

    if "!CHOICE!"=="1" (
        python scripts/bump_version.py patch
    ) else if "!CHOICE!"=="2" (
        python scripts/bump_version.py minor
    ) else if "!CHOICE!"=="3" (
        python scripts/bump_version.py major
    ) else if "!CHOICE!"=="4" (
        echo Bo qua tang version.
    ) else (
        echo Lua chon khong hop le.
        exit /b 1
    )
)

:: Git add cac file version
git add "%APP_CONFIG%" "%UPDATE_JSON%" "%CHANGELOG%" 2>nul

echo.
echo [OK] Pre-commit check passed!
exit /b 0
