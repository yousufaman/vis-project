@echo off
title VIS Project — Task 7b: Scalability Study

set "PROJECT_DIR=%~dp0"
set "BUILD_DIR=%PROJECT_DIR%build"
set "VTK_BIN=C:\VTK-build\bin"
set "VTK_PYTHON=C:\VTK-build\lib\site-packages"

:: Add VTK DLLs and our own DLL to PATH so vtkVISFilters.pyd can find them
set "PATH=%VTK_BIN%;%BUILD_DIR%\bin;%PATH%"

:: PYTHONPATH: VTK modules first, then our module's vtkmodules folder
set "PYTHONPATH=%VTK_PYTHON%;%BUILD_DIR%\python\vtkmodules;%PYTHONPATH%"

python "%PROJECT_DIR%python\task7b_scalability_study.py"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Demo failed. See message above.
    pause
)
