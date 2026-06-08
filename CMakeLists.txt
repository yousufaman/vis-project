cmake_minimum_required(VERSION 3.25)

project(VISVTKFilters VERSION 0.1.0 LANGUAGES CXX)

include(GNUInstallDirs)
include(CTest)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Python wrapping requires shared libraries
set(BUILD_SHARED_LIBS ON)

# locate Python libraries
find_package(Python 
  REQUIRED 
  COMPONENTS 
    Interpreter 
    Development.Module
)

# locate VTK library
find_package(
  VTK REQUIRED
  COMPONENTS
    CommonCore
    CommonDataModel
    FiltersCore
    FiltersGeneral
    FiltersSources
    WrappingPythonCore
)

set(vis_module_file "${CMAKE_CURRENT_SOURCE_DIR}/src/vtk.module")

vtk_module_scan(
  MODULE_FILES "${vis_module_file}"
  PROVIDES_MODULES vis_vtk_modules
  WANT_BY_DEFAULT ON
)

vtk_module_build(
  MODULES ${vis_vtk_modules}
  PACKAGE "${PROJECT_NAME}"
  ENABLE_WRAPPING ON
  INSTALL_EXPORT VISVTKFiltersTargets
  VERSION "${PROJECT_VERSION}"
)

if(VTK_WRAP_PYTHON)
  vtk_module_wrap_python(
    MODULES ${vis_vtk_modules}
    PYTHON_PACKAGE "vtkmodules"
    MODULE_DESTINATION "python"
    INSTALL_HEADERS OFF
    INSTALL_EXPORT VISVTKFiltersPythonTargets
  )
endif()

add_subdirectory(python)

if(BUILD_TESTING)
  add_subdirectory(tests)
endif()
