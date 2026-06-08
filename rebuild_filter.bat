@echo off
title VIS Project — Rebuild C++ Filter

set "PROJECT_DIR=%~dp0"

echo ============================================
echo  Rebuilding vtkVISMarchingCubes C++ filter
echo  (only recompiles what changed — fast!)
echo ============================================
echo.

:: Initialize the MSVC compiler environment
call "C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat" > nul 2>&1

cmake --build "%PROJECT_DIR%build" --config Release

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Build successful! You can now run the demos.
) else (
    echo.
    echo [ERROR] Build failed. Check the errors above.
)

pause
