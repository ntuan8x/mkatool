@echo off
chcp 65001 >nul
echo ================================================
echo  Cai dat pre-commit hook cho MKAtools
echo ================================================
echo.

:: Kiem tra Windows hay Git Bash
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python khong tim thay. Vui long cai dat Python.
    exit /b 1
)

:: Kiem tra git
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git khong tim thay. Vui long cai dat Git.
    exit /b 1
)

:: Xac dinh script can copy
if exist "scripts\pre-commit.bat" (
    set "HOOK_FILE=scripts\pre-commit.bat"
) else if exist "scripts\pre-commit" (
    set "HOOK_FILE=scripts\pre-commit"
) else (
    echo [ERROR] Khong tim thay pre-commit script.
    exit /b 1
)

:: Copy vao .git/hooks
if not exist ".git\hooks" mkdir ".git\hooks"
copy /Y "%HOOK_FILE%" ".git\hooks\pre-commit" >nul
if %errorlevel% equ 0 (
    echo [OK] Da copy %HOOK_FILE% vao .git\hooks\pre-commit
    echo.
    echo Pre-commit hook da duoc cai dat!
    echo Moi lan commit se tu dong kiem tra version.
) else (
    echo [ERROR] Khong the copy hook. Thu chay CMD voi quyen Admin.
    exit /b 1
)

:: Test script bump_version
echo.
echo Testing bump_version.py...
python scripts\bump_version.py set 2.2.1 >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] bump_version.py hoat dong tot
) else (
    echo [WARNING] bump_version.py co van de, vui long kiem tra.
)

echo.
echo ================================================
echo  Hoan tat cai dat!
echo ================================================
echo.
echo Huong dan su dung:
echo   1. Bat ky thay doi code nao -> commit
echo   2. Neu co code thay doi, hook se yeu cau tang version
echo   3. Chon PATCH/MINOR/MAJOR theo loai thay doi
echo.
echo Hoac chay thu cong:
echo   python scripts\bump_version.py patch
echo   python scripts\bump_version.py minor
echo   python scripts\bump_version.py major
pause
