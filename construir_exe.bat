@echo off
setlocal
cd /d "%~dp0"
REM Uso: construir_exe.bat          -> dist\MichiNotes.exe
REM      construir_exe.bat debug    -> dist\MichiNotes_debug.exe (con consola, para ver errores)
set NOMBRE=MichiNotes
if /i "%1"=="debug" (set MN_DEBUG=1& set NOMBRE=MichiNotes_debug)

set PY=
where py >nul 2>nul && set PY=py -3
if "%PY%"=="" (where python >nul 2>nul && set PY=python)
if "%PY%"=="" goto :sinpython
%PY% --version >nul 2>nul || goto :sinpython

echo [1/4] Creando entorno...
%PY% -m venv .venv || goto :error
call .venv\Scripts\activate || goto :error
echo [2/4] Instalando librerias (puede tardar unos minutos)...
python -m pip install --upgrade pip >nul
pip install -r requirements.txt pyinstaller || goto :error
echo [3/4] Generando el ejecutable...
pyinstaller --noconfirm --clean MichiNotes.spec || goto :error

echo [4/4] Verificando...
if not exist "dist\%NOMBRE%.exe" goto :error
echo.
echo ============================================================
echo  LISTO: %CD%\dist\%NOMBRE%.exe
echo ============================================================
start "" explorer "%CD%\dist"
pause
exit /b 0

:sinpython
echo.
echo NO SE ENCONTRO PYTHON. Instalalo desde https://www.python.org/downloads/
echo y marca la casilla "Add python.exe to PATH" al instalar. Luego repite.
pause
exit /b 1

:error
echo.
echo *** FALLO LA CONSTRUCCION. Copia los mensajes de arriba y envialos. ***
pause
exit /b 1
