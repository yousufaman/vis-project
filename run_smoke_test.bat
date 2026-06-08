@echo off
title VIS Project — Smoke Test

set "PROJECT_DIR=%~dp0"
set "BUILD_DIR=%PROJECT_DIR%build"
set "VTK_BIN=C:\VTK-build\bin"
set "VTK_PYTHON=C:\VTK-build\lib\site-packages"

:: Add VTK DLLs and our own DLL to PATH so vtkVISFilters.pyd can find them
set "PATH=%VTK_BIN%;%BUILD_DIR%\bin;%PATH%"

:: PYTHONPATH: VTK modules first, then our module's vtkmodules folder
set "PYTHONPATH=%VTK_PYTHON%;%BUILD_DIR%\python\vtkmodules;%PYTHONPATH%"

echo ============================================
echo  Running: Smoke Test (vtkVISMarchingCubes)
echo ============================================
echo.
echo PATH prepended: %VTK_BIN%
echo PYTHONPATH: %PYTHONPATH%
echo.

python "%PROJECT_DIR%python\smoke_marching_cubes.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [PASS] All tests passed!
) else (
    echo.
    echo [FAIL] Test failed. See message above.
)

pause
