"""Single isosurface demo using our marching cubes filter."""

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
    vtkRenderWindowInteractor,
)
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401
import vtkmodules.vtkInteractionStyle  # noqa: F401


def main():
    colors = vtkNamedColors()

    # sample a superquadric on a grid
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)

    sample = vtkSampleFunction()
    sample.SetImplicitFunction(fn)
    sample.SetSampleDimensions(60, 60, 60)
    sample.SetModelBounds(-2, 2, -2, 2, -2, 2)

    # run our filter
    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(sample.GetOutputPort())
    mc.SetIsovalue(2.0)

    smooth = vtkPolyDataNormals()
    smooth.SetInputConnection(mc.GetOutputPort())
    smooth.SetFeatureAngle(60.0)

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(smooth.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("PeachPuff"))
    actor.GetProperty().SetSpecular(0.4)
    actor.GetProperty().SetSpecularPower(40)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d("DarkSlateGray"))
    renderer.ResetCamera()
    renderer.GetActiveCamera().Elevation(20)
    renderer.GetActiveCamera().Azimuth(30)

    window = vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(800, 600)
    window.SetWindowName("vtkVISMarchingCubes - Single Isosurface")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    window.Render()
    interactor.Start()


if __name__ == "__main__":
    main()
