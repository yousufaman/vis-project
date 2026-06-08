"""Smoke test: import vtkVISMarchingCubes, run on a synthetic volume, check output."""
from __future__ import annotations

import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkImagingCore import vtkImageCast
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkCommonDataModel import vtkSphere


def main() -> int:
    # Build a small synthetic scalar volume from a sphere implicit function
    sphere_fn = vtkSphere()
    sphere_fn.SetRadius(0.4)

    sampler = vtkSampleFunction()
    sampler.SetImplicitFunction(sphere_fn)
    sampler.SetSampleDimensions(30, 30, 30)
    sampler.SetModelBounds(-1, 1, -1, 1, -1, 1)
    sampler.Update()

    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(sampler.GetOutputPort())
    mc.SetIsovalue(0.0)   # sphere surface is at f=0
    mc.Update()

    output = mc.GetOutput()
    npts  = output.GetNumberOfPoints()
    ncells = output.GetNumberOfCells()
    print(f"vtkVISMarchingCubes: points={npts}  triangles={ncells}")

    assert npts > 0,   f"Expected points > 0, got {npts}"
    assert ncells > 0, f"Expected triangles > 0, got {ncells}"
    # Every cell must be a triangle (3 points)
    for i in range(ncells):
        cell = output.GetCell(i)
        assert cell.GetNumberOfPoints() == 3, \
            f"Cell {i} has {cell.GetNumberOfPoints()} points (expected 3)"

    print("All assertions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
