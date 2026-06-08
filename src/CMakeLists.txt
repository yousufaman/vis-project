vtk_module_add_module(VISFilters
  CLASSES
    vtkHelloElevationFilter
    vtkVISMarchingCubes
  SOURCES
    vtkHelloElevationFilter.cxx
    vtkVISMarchingCubes.cxx
)

vtk_module_link(VISFilters
  PUBLIC
    VTK::CommonCore
    VTK::CommonDataModel
    VTK::FiltersCore
    VTK::FiltersGeneral
    VTK::ImagingCore
)
