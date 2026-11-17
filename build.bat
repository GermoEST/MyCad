@echo off
chcp 65001 >nul
setlocal
title MyCAD - exe ehitamine
cd /d "%~dp0"

echo ================================================
echo   MyCAD - exe ehitamine (PyInstaller)
echo ================================================
echo.

rem --- Pythoni leidmine: eelistatult "py" launcher, muidu "python" ---
set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY (
    where python >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo [VIGA] Pythonit ei leitud. Paigalda Python 3.8+ aadressilt python.org
    echo        ja vali paigaldamisel "Add python.exe to PATH".
    goto :fail
)
echo Python:
%PY% --version
echo.

if not exist "mycad.pyw" (
    echo [VIGA] mycad.pyw puudub selles kaustas: %CD%
    goto :fail
)
if not exist "lang\et.json" (
    echo [VIGA] lang\ kaust voi keelefailid puuduvad.
    goto :fail
)

rem --- PyInstaller (paigaldatakse ainult vajadusel; programm ise seda ei vaja) ---
%PY% -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo PyInstallerit pole, paigaldan...
    %PY% -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo [VIGA] PyInstalleri paigaldamine ebaonnestus.
        goto :fail
    )
)

rem --- Kui kaustas on mycad.ico, kasutatakse seda exe ikoonina ---
set "ICON="
if exist "mycad.ico" set "ICON=--icon mycad.ico"

rem --- Vana exe ei tohi lahti olla ---
tasklist /FI "IMAGENAME eq MyCAD.exe" 2>nul | find /I "MyCAD.exe" >nul
if not errorlevel 1 (
    echo [VIGA] MyCAD.exe on praegu lahti. Sulge programm ja proovi uuesti.
    goto :fail
)

echo.
echo Ehitan exe-faili, see votab umbes minuti...
echo.
%PY% -m PyInstaller --onefile --windowed --clean --noconfirm --name MyCAD %ICON% --add-data "lang;lang" mycad.pyw
if errorlevel 1 (
    echo.
    echo [VIGA] Ehitamine ebaonnestus - vaata ules pandud teateid.
    goto :fail
)

if not exist "dist\MyCAD.exe" (
    echo [VIGA] dist\MyCAD.exe ei tekkinud.
    goto :fail
)

rem --- Juhendid exe korvale ---
if exist "Info.txt"    copy /Y "Info.txt"    "dist\" >nul
if exist "Info_EN.txt" copy /Y "Info_EN.txt" "dist\" >nul

rem --- Ajutiste failide koristus ---
if exist "build" rmdir /S /Q "build"
if exist "MyCAD.spec" del /Q "MyCAD.spec"

echo.
echo ================================================
echo   VALMIS: %CD%\dist\MyCAD.exe
echo ================================================
echo Esimesel kaivitusel loob programm exe korvale
echo lang\, library\ ja config.json.
echo.
explorer "dist"
pause
exit /b 0

:fail
echo.
pause
exit /b 1
