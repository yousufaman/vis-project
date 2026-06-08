# build VTK

$vtkdir = Join-Path $env:USERPROFILE "\"

[Environment]::SetEnvironmentVariable(
  "VTK_DIR",
  "$env:USERPROFILE\vtk",
  "User"
)

$vtksrc = Join-Path $env:TEMP "vtk-source"
$vtkbld = Join-Path $env:TEMP "vtk-build"

git clone ^
    --branch v9.6.1 ^
    --recursive ^
    --depth 1 ^
    https://gitlab.kitware.com/vtk/vtk.git ^
    "$vtksrc"

cmake -G Ninja -B "$vtkbld" -S "$vtksrc" ^
    -DCMAKE_INSTALL_PREFIX="$env:VTK_DIR" ^
    -DCMAKE_BUILD_TYPE=Release ^
    -DBUILD_SHARED_LIBS=ON ^
    -DVTK_ENABLE_WRAPPING=ON ^
    -DVTK_WRAP_PYTHON=ON ^
    -DVTK_BUILD_TESTING=OFF ^
    -DVTK_BUILD_EXAMPLES=OFF ^
    -DVTK_FORBID_DOWNLOADS=ON ^
    -DVTK_USE_EXTERNAL=OFF ^
    -DVTK_MODULE_ENABLE_VTK_CommonCore=YES ^
    -DVTK_MODULE_ENABLE_VTK_CommonDataModel=YES ^
    -DVTK_MODULE_ENABLE_VTK_FiltersCore=YES ^
    -DVTK_MODULE_ENABLE_VTK_FiltersGeneral=YES ^
    -DVTK_MODULE_ENABLE_VTK_FiltersSources=YES ^
    -DVTK_MODULE_ENABLE_VTK_WrappingPythonCore=YES ^
    -DVTK_MODULE_ENABLE_VTK_Python=YES

cmake --build build
cmake --install build