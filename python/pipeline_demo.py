from __future__ import annotations

from vtkVISFilters import *
from vtkmodules.vtkCommonCore import vtkVersion
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkFiltersSources import vtkSphereSource


def build_pipeline():
    source = vtkSphereSource()
    source.SetThetaResolution(32)
    source.SetPhiResolution(32)

    elevation = vtkHelloElevationFilter()
    elevation.SetInputConnection(source.GetOutputPort())
    elevation.SetLowPoint(0.0, 0.0, -0.5)
    elevation.SetHighPoint(0.0, 0.0, 0.5)

    normals = vtkPolyDataNormals()
    normals.SetInputConnection(elevation.GetOutputPort())
    normals.SplittingOff()

    return source, elevation, normals


def main() -> int:
    _, _, pipeline = build_pipeline()
    pipeline.Update()

    output = pipeline.GetOutput()
    scalars = output.GetPointData().GetScalars()
    scalar_range = scalars.GetRange() if scalars is not None else (None, None)

    print(f"VTK {vtkVersion.GetVTKVersion()}")
    print(f"points={output.GetNumberOfPoints()}")
    print(f"polys={output.GetNumberOfPolys()}")
    print(f"scalar_name={scalars.GetName() if scalars is not None else 'None'}")
    print(f"scalar_range={scalar_range}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
