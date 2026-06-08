"""Quick smoke test for vtkVISMarchingCubes."""

import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkCommonDataModel import vtkSphere

# simple test: extract sphere isosurface and check we get triangles
sphere_fn = vtkSphere()
sphere_fn.SetRadius(0.4)

sampler = vtkSampleFunction()
sampler.SetImplicitFunction(sphere_fn)
sampler.SetSampleDimensions(30, 30, 30)
sampler.SetModelBounds(-1, 1, -1, 1, -1, 1)
sampler.Update()

mc = vtkVISMarchingCubes()
mc.SetInputConnection(sampler.GetOutputPort())
mc.SetIsovalue(0.0)
mc.Update()

output = mc.GetOutput()
npts = output.GetNumberOfPoints()
ntri = output.GetNumberOfCells()
print(f"Points: {npts}, Triangles: {ntri}")

assert npts > 0, "no points generated"
assert ntri > 0, "no triangles generated"

# check all cells are actually triangles
for i in range(ntri):
    assert output.GetCell(i).GetNumberOfPoints() == 3

print("OK - all checks passed")
