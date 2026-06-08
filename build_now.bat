@echo off
call "C:\Program Files\Microsoft Visual Studio\18\Insiders\VC\Auxiliary\Build\vcvars64.bat"
cmake --build "C:\Users\pc\Downloads\VTK Project\build" --config Release
echo EXIT_CODE=%ERRORLEVEL%
