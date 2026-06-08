"""Demo: Side-by-side comparison — Gradient-based Normals vs vtkPolyDataNormals."""
from __future__ import annotations

import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
from vtkmodules.vtkFiltersCore import vtkPolyDataNormals
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkRenderingCore import (
    vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow,
    vtkRenderWindowInteractor, vtkTextActor,
)
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
import vtkmodules.vtkInteractionStyle  # noqa: F401

ISOVALUE = 2.0
DIMS = 60


def make_sample():
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)
    sample = vtkSampleFunction()
    sample.SetImplicitFunction(fn)
    sample.SetSampleDimensions(DIMS, DIMS, DIMS)
    sample.SetModelBounds(-2, 2, -2, 2, -2, 2)
    return sample


def make_label(text):
    label = vtkTextActor()
    label.SetInput(text)
    label.GetTextProperty().SetFontSize(20)
    label.GetTextProperty().SetColor(1, 1, 1)
    label.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    label.SetPosition(0.05, 0.05)
    return label


def main() -> None:
    colors = vtkNamedColors()

    sample_left  = make_sample()
    sample_right = make_sample()

    # Left: our Marching Cubes WITH gradient-based normals enabled (ComputeNormalsOn)
    mc_left = vtkVISMarchingCubes()
    mc_left.SetInputConnection(sample_left.GetOutputPort())
    mc_left.SetIsovalue(ISOVALUE)
    mc_left.MergePointsOn()
    mc_left.ComputeNormalsOn()

    mapper_left = vtkPolyDataMapper()
    mapper_left.SetInputConnection(mc_left.GetOutputPort())
    mapper_left.ScalarVisibilityOff()
    
    actor_left = vtkActor()
    actor_left.SetMapper(mapper_left)
    actor_left.GetProperty().SetColor(colors.GetColor3d("PeachPuff"))
    actor_left.GetProperty().SetSpecular(0.4)
    actor_left.GetProperty().SetSpecularPower(40)

    # Right: our Marching Cubes WITHOUT gradient normals + vtkPolyDataNormals
    mc_right = vtkVISMarchingCubes()
    mc_right.SetInputConnection(sample_right.GetOutputPort())
    mc_right.SetIsovalue(ISOVALUE)
    mc_right.MergePointsOn()
    mc_right.ComputeNormalsOff()

    cf = vtkPolyDataNormals()
    cf.SetInputConnection(mc_right.GetOutputPort())
    cf.SetFeatureAngle(60.0)

    mapper_right = vtkPolyDataMapper()
    mapper_right.SetInputConnection(cf.GetOutputPort())
    mapper_right.ScalarVisibilityOff()

    actor_right = vtkActor()
    actor_right.SetMapper(mapper_right)
    actor_right.GetProperty().SetColor(colors.GetColor3d("LightSkyBlue"))
    actor_right.GetProperty().SetSpecular(0.4)
    actor_right.GetProperty().SetSpecularPower(40)

    # Renderers with split viewports
    ren_left  = vtkRenderer()
    ren_right = vtkRenderer()
    ren_left.SetViewport(0.0, 0.0, 0.5, 1.0)
    ren_right.SetViewport(0.5, 0.0, 1.0, 1.0)

    ren_left.AddActor(actor_left)
    ren_left.AddActor(make_label("Gradient-Based Normals (ComputeNormals=On)"))
    ren_left.SetBackground(colors.GetColor3d("DarkSlateGray"))

    ren_right.AddActor(actor_right)
    ren_right.AddActor(make_label("vtkPolyDataNormals (ComputeNormals=Off)"))
    ren_right.SetBackground(colors.GetColor3d("DarkSlateBlue"))

    for ren in (ren_left, ren_right):
        ren.ResetCamera()
        ren.GetActiveCamera().Elevation(20)
        ren.GetActiveCamera().Azimuth(30)

    window = vtkRenderWindow()
    window.AddRenderer(ren_left)
    window.AddRenderer(ren_right)
    window.SetSize(1400, 700)
    window.SetWindowName("Normals Comparison: Gradient vs vtkPolyDataNormals")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()

    # Print point/triangle counts for comparison
    mc_left.Update()
    mc_right.Update()
    cf.Update()
    print(f"Gradient Normals: points={mc_left.GetOutput().GetNumberOfPoints():>7}  "
          f"triangles={mc_left.GetOutput().GetNumberOfCells():>7}")
    print(f"vtkPolyDataNormals: points={cf.GetOutput().GetNumberOfPoints():>7}  "
          f"triangles={cf.GetOutput().GetNumberOfCells():>7}")

    interactor.Start()


if __name__ == "__main__":
    main()
