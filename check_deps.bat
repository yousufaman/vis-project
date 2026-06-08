@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat" > nul 2>&1
echo === DLL dependencies of vtkVISFilters.pyd ===
dumpbin /dependents "C:\Users\pc\Downloads\VTK Project\build\python\vtkmodules\vtkVISFilters.pyd"
pause
