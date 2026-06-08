"""Comparing gradient-based normals vs vtkPolyDataNormals post-processing."""

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

ISO = 2.0


def setup_sample():
    """Create a superquadric sample volume."""
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)
    s = vtkSampleFunction()
    s.SetImplicitFunction(fn)
    s.SetSampleDimensions(60, 60, 60)
    s.SetModelBounds(-2, 2, -2, 2, -2, 2)
    return s


def add_label(renderer, text):
    t = vtkTextActor()
    t.SetInput(text)
    t.GetTextProperty().SetFontSize(18)
    t.GetTextProperty().SetColor(1, 1, 1)
    t.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    t.SetPosition(0.04, 0.04)
    renderer.AddActor(t)


def main():
    colors = vtkNamedColors()

    # Left: gradient normals from our filter directly
    mc1 = vtkVISMarchingCubes()
    mc1.SetInputConnection(setup_sample().GetOutputPort())
    mc1.SetIsovalue(ISO)
    mc1.MergePointsOn()
    mc1.ComputeNormalsOn()

    m1 = vtkPolyDataMapper()
    m1.SetInputConnection(mc1.GetOutputPort())
    m1.ScalarVisibilityOff()

    a1 = vtkActor()
    a1.SetMapper(m1)
    a1.GetProperty().SetColor(colors.GetColor3d("PeachPuff"))
    a1.GetProperty().SetSpecular(0.4)
    a1.GetProperty().SetSpecularPower(40)

    # Right: no gradient normals, then run vtkPolyDataNormals on output
    mc2 = vtkVISMarchingCubes()
    mc2.SetInputConnection(setup_sample().GetOutputPort())
    mc2.SetIsovalue(ISO)
    mc2.MergePointsOn()
    mc2.ComputeNormalsOff()

    pdn = vtkPolyDataNormals()
    pdn.SetInputConnection(mc2.GetOutputPort())
    pdn.SetFeatureAngle(60.0)

    m2 = vtkPolyDataMapper()
    m2.SetInputConnection(pdn.GetOutputPort())
    m2.ScalarVisibilityOff()

    a2 = vtkActor()
    a2.SetMapper(m2)
    a2.GetProperty().SetColor(colors.GetColor3d("LightSkyBlue"))
    a2.GetProperty().SetSpecular(0.4)
    a2.GetProperty().SetSpecularPower(40)

    # set up side-by-side renderers
    ren1 = vtkRenderer()
    ren2 = vtkRenderer()
    ren1.SetViewport(0, 0, 0.5, 1)
    ren2.SetViewport(0.5, 0, 1, 1)

    ren1.AddActor(a1)
    ren1.SetBackground(0.12, 0.15, 0.18)
    add_label(ren1, "Gradient Normals (ComputeNormals=On)")

    ren2.AddActor(a2)
    ren2.SetBackground(0.14, 0.12, 0.2)
    add_label(ren2, "vtkPolyDataNormals (post-process)")

    for r in [ren1, ren2]:
        r.ResetCamera()
        cam = r.GetActiveCamera()
        cam.Elevation(20)
        cam.Azimuth(30)

    win = vtkRenderWindow()
    win.AddRenderer(ren1)
    win.AddRenderer(ren2)
    win.SetSize(1400, 700)
    win.SetWindowName("Normals Comparison")

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(win)
    win.Render()

    mc1.Update()
    mc2.Update()
    pdn.Update()
    print(f"Gradient normals: {mc1.GetOutput().GetNumberOfPoints()} pts, {mc1.GetOutput().GetNumberOfCells()} tris")
    print(f"PolyDataNormals:  {pdn.GetOutput().GetNumberOfPoints()} pts, {pdn.GetOutput().GetNumberOfCells()} tris")

    iren.Start()


if __name__ == "__main__":
    main()
