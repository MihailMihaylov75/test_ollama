@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================================
REM Creates/updates .venv in REPO ROOT, activates it, installs requirements.txt.
REM Place this file under: <repo>\scripts\init-venv.bat
REM ============================================================================

REM --- Move to repo root (parent of this script's folder)
pushd "%~dp0\.." >nul

set "VENV_DIR=.venv"
set "REQ_FILE=requirements.txt"
set "REBUILD=0"

REM --- Optional: rebuild flag (keep or remove if you want zero options)
if /I "%~1"=="--rebuild" set "REBUILD=1"

REM --- Find python (robust)
set "PY_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do (
  set "PY_EXE=%%P"
  goto :python_found
)
:python_found

if "%PY_EXE%"=="" (
  echo [ERROR] Python not found in PATH. Install Python or add it to PATH.
  goto :fail
)

REM --- Sanity check
"%PY_EXE%" -c "import sys" >nul 2>&1 || (
  echo [ERROR] Python is present but cannot run.
  goto :fail
)

REM --- Ensure requirements exist in repo root
if not exist "%REQ_FILE%" (
  echo [ERROR] "%REQ_FILE%" not found in repo root: %CD%
  goto :fail
)

REM --- Rebuild if requested
if "%REBUILD%"=="1" (
  echo [1/6] Removing existing %VENV_DIR%...
  if exist "%VENV_DIR%" rmdir /s /q "%VENV_DIR%"
)

REM --- Create venv if missing
if not exist "%VENV_DIR%\Scripts\python.exe" (
  echo [2/6] Creating venv in "%CD%\%VENV_DIR%"...
  "%PY_EXE%" -m venv "%VENV_DIR%" || ( echo [ERROR] venv create failed & goto :fail )
) else (
  echo [2/6] Venv already exists: "%CD%\%VENV_DIR%"
)

REM --- Activate venv in current shell
echo [3/6] Activating venv...
call "%VENV_DIR%\Scripts\activate.bat" || ( echo [ERROR] activate failed & goto :fail )

REM --- Make pip less noisy
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

echo [4/6] Upgrading pip/setuptools/wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo [WARN] Tooling upgrade failed. Trying ensurepip repair...
  python -m ensurepip --upgrade
  python -m pip install --upgrade pip setuptools wheel || echo [WARN] Still failing; continuing...
)

echo [5/6] Installing dependencies from "%REQ_FILE%"...
python -m pip install -r "%REQ_FILE%" || ( echo [ERROR] Requirements install failed & goto :fail )

echo [6/6] Sanity check (pip check)...
python -m pip check || echo [WARN] pip check reported issues (continuing).

echo.
echo [OK] Virtualenv ready and ACTIVE: %CD%\%VENV_DIR%
python --version
python -m pip --version
echo.

popd >nul
endlocal & exit /b 0

:fail
echo.
echo [FAIL] init-venv failed.
popd >nul
endlocal & exit /b 1