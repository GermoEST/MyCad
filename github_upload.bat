@echo off
chcp 65001 >nul
setlocal
title MyCAD - GitHubi saatmine
cd /d "%~dp0"

set "REPO=https://github.com/GermoEST/MyCad.git"

where git >nul 2>nul
if errorlevel 1 (
    echo [VIGA] Git puudub. Paigalda see aadressilt https://git-scm.com/download/win
    echo        ja kaivita see fail uuesti.
    goto :end
)

if not exist ".git" (
    echo Loon git-hoidla...
    git init -b main
    git remote add origin %REPO%
)

rem Nimi ja e-post commitide jaoks (ainult selles kaustas, kui pole juba seatud)
git config user.name  >nul 2>nul || git config user.name "Germo"
git config user.email >nul 2>nul || git config user.email "germotammela@gmail.com"

git add -A
git diff --cached --quiet
if errorlevel 1 (
    set "MSG="
    set /p MSG=Kirjelda muudatust (Enter = "Uuendus"): 
    if not defined MSG set "MSG=Uuendus"
    call git commit -m "%%MSG%%"
) else (
    echo Uusi muudatusi pole, saadan olemasoleva.
)

echo.
echo Saadan GitHubi: %REPO%
echo (esimesel korral avaneb brauseris GitHubi sisselogimine)
git push -u origin main
if errorlevel 1 (
    echo.
    echo [VIGA] Saatmine ebaonnestus - vaata ules pandud teadet.
) else (
    echo.
    echo VALMIS: https://github.com/GermoEST/MyCad
)

:end
echo.
pause
