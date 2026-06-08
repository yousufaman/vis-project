"""Side-by-side comparison of our marching cubes vs VTK's built-in."""

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


def main():
    colors = vtkNamedColors()

    # set up the implicit function to sample
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)

    sample1 = vtkSampleFunction()
    sample1.SetImplicitFunction(fn)
    sample1.SetSampleDimensions(60, 60, 60)
    sample1.SetModelBounds(-2, 2, -2, 2, -2, 2)

    sample2 = vtkSampleFunction()
    sample2.SetImplicitFunction(fn)
    sample2.SetSampleDimensions(60, 60, 60)
    sample2.SetModelBounds(-2, 2, -2, 2, -2, 2)

    iso = 2.0

    # --- left side: our implementation ---
    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(sample1.GetOutputPort())
    mc.SetIsovalue(iso)

    smooth_left = vtkPolyDataNormals()
    smooth_left.SetInputConnection(mc.GetOutputPort())
    smooth_left.SetFeatureAngle(60.0)

    mapper_l = vtkPolyDataMapper()
    mapper_l.SetInputConnection(smooth_left.GetOutputPort())
    mapper_l.ScalarVisibilityOff()

    actor_l = vtkActor()
    actor_l.SetMapper(mapper_l)
    actor_l.GetProperty().SetColor(colors.GetColor3d("PeachPuff"))
    actor_l.GetProperty().SetSpecular(0.4)
    actor_l.GetProperty().SetSpecularPower(40)

    # --- right side: vtk contour filter ---
    cf = vtkContourFilter()
    cf.SetInputConnection(sample2.GetOutputPort())
    cf.SetValue(0, iso)

    smooth_right = vtkPolyDataNormals()
    smooth_right.SetInputConnection(cf.GetOutputPort())
    smooth_right.SetFeatureAngle(60.0)

    mapper_r = vtkPolyDataMapper()
    mapper_r.SetInputConnection(smooth_right.GetOutputPort())
    mapper_r.ScalarVisibilityOff()

    actor_r = vtkActor()
    actor_r.SetMapper(mapper_r)
    actor_r.GetProperty().SetColor(colors.GetColor3d("CornflowerBlue"))
    actor_r.GetProperty().SetSpecular(0.3)
    actor_r.GetProperty().SetSpecularPower(30)

    # labels
    lbl_left = vtkTextActor()
    lbl_left.SetInput("vtkVISMarchingCubes (ours)")
    lbl_left.GetTextProperty().SetFontSize(20)
    lbl_left.GetTextProperty().SetColor(1, 1, 1)
    lbl_left.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    lbl_left.SetPosition(0.05, 0.05)

    lbl_right = vtkTextActor()
    lbl_right.SetInput("vtkContourFilter (VTK)")
    lbl_right.GetTextProperty().SetFontSize(20)
    lbl_right.GetTextProperty().SetColor(1, 1, 1)
    lbl_right.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
    lbl_right.SetPosition(0.05, 0.05)

    # renderers
    ren_left = vtkRenderer()
    ren_right = vtkRenderer()
    ren_left.SetViewport(0.0, 0.0, 0.5, 1.0)
    ren_right.SetViewport(0.5, 0.0, 1.0, 1.0)

    ren_left.AddActor(actor_l)
    ren_left.AddActor(lbl_left)
    ren_left.SetBackground(colors.GetColor3d("DarkSlateGray"))

    ren_right.AddActor(actor_r)
    ren_right.AddActor(lbl_right)
    ren_right.SetBackground(0.15, 0.15, 0.25)

    for r in (ren_left, ren_right):
        r.ResetCamera()
        r.GetActiveCamera().Elevation(20)
        r.GetActiveCamera().Azimuth(30)

    window = vtkRenderWindow()
    window.AddRenderer(ren_left)
    window.AddRenderer(ren_right)
    window.SetSize(1400, 700)
    window.SetWindowName("Marching Cubes Comparison")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()

    mc.Update()
    cf.Update()
    print(f"Our MC:  {mc.GetOutput().GetNumberOfPoints()} pts, {mc.GetOutput().GetNumberOfCells()} tris")
    print(f"VTK CF:  {cf.GetOutput().GetNumberOfPoints()} pts, {cf.GetOutput().GetNumberOfCells()} tris")

    interactor.Start()


if __name__ == "__main__":
    main()
