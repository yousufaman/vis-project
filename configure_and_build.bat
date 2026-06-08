@echo off
title VIS Project — Configure + Build

call "C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat"
if %ERRORLEVEL% NEQ 0 (echo [ERROR] vcvars64 failed & pause & exit /b 1)

set PROJECT_DIR=C:\Users\pc\Downloads\VTK Project
set BUILD_DIR=%PROJECT_DIR%\build
set VTK_DIR=C:\VTK-build\lib\cmake\vtk-9.6
set PYTHON_EXE=C:\Users\pc\AppData\Local\Python\pythoncore-3.14-64\python.exe

echo.
echo === Step 1: CMake Configure ===
cmake -S "%PROJECT_DIR%" ^
      -B "%BUILD_DIR%" ^
      -G "NMake Makefiles" ^
      -DCMAKE_BUILD_TYPE=Release ^
      -DVTK_DIR="%VTK_DIR%" ^
      -DPython3_EXECUTABLE="%PYTHON_EXE%"

if %ERRORLEVEL% NEQ 0 (echo [ERROR] Configure failed & pause & exit /b 1)

echo.
echo === Step 2: Build ===
cmake --build "%BUILD_DIR%" --config Release

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Build successful!
) else (
    echo.
    echo [ERROR] Build failed. Check errors above.
)
pause
