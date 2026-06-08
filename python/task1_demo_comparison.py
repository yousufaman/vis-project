"""Demo 2: Side-by-side comparison — vtkVISMarchingCubes vs vtkContourFilter."""
from __future__ import annotations

import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
from vtkmodules.vtkFiltersCore import vtkContourFilter, vtkPolyDataNormals
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


def make_actor(pipeline_end, color):
    smooth = vtkPolyDataNormals()
    smooth.SetInputConnection(pipeline_end.GetOutputPort())
    smooth.SetFeatureAngle(60.0)
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(smooth.GetOutputPort())
    mapper.ScalarVisibilityOff()
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetSpecular(0.4)
    actor.GetProperty().SetSpecularPower(40)
    return actor


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

    # Shared volume source — used by both pipelines
    sample_left  = make_sample()
    sample_right = make_sample()

    # Left: our Marching Cubes
    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(sample_left.GetOutputPort())
    mc.SetIsovalue(ISOVALUE)
    actor_left = make_actor(mc, colors.GetColor3d("PeachPuff"))

    # Right: VTK's built-in ContourFilter
    cf = vtkContourFilter()
    cf.SetInputConnection(sample_right.GetOutputPort())
    cf.SetValue(0, ISOVALUE)
    actor_right = make_actor(cf, colors.GetColor3d("LightSkyBlue"))

    # Renderers with split viewports
    ren_left  = vtkRenderer()
    ren_right = vtkRenderer()
    ren_left.SetViewport(0.0, 0.0, 0.5, 1.0)
    ren_right.SetViewport(0.5, 0.0, 1.0, 1.0)

    ren_left.AddActor(actor_left)
    ren_left.AddActor(make_label("vtkVISMarchingCubes (ours)"))
    ren_left.SetBackground(colors.GetColor3d("DarkSlateGray"))

    ren_right.AddActor(actor_right)
    ren_right.AddActor(make_label("vtkContourFilter (VTK built-in)"))
    ren_right.SetBackground(colors.GetColor3d("DarkSlateBlue"))

    for ren in (ren_left, ren_right):
        ren.ResetCamera()
        ren.GetActiveCamera().Elevation(20)
        ren.GetActiveCamera().Azimuth(30)

    window = vtkRenderWindow()
    window.AddRenderer(ren_left)
    window.AddRenderer(ren_right)
    window.SetSize(1400, 700)
    window.SetWindowName("Marching Cubes Comparison: Ours vs VTK ContourFilter")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()

    # Print point/triangle counts for comparison
    mc.Update()
    cf.Update()
    print(f"Our MC:          points={mc.GetOutput().GetNumberOfPoints():>7}  "
          f"triangles={mc.GetOutput().GetNumberOfCells():>7}")
    print(f"vtkContourFilter: points={cf.GetOutput().GetNumberOfPoints():>7}  "
          f"triangles={cf.GetOutput().GetNumberOfCells():>7}")

    interactor.Start()


if __name__ == "__main__":
    main()
