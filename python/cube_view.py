from __future__ import annotations

from vtkmodules.vtkFiltersSources import vtkCubeSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
)
import vtkmodules.vtkRenderingOpenGL2  # noqa: F401


def main() -> int:
    source = vtkCubeSource()
    source.SetXLength(1.0)
    source.SetYLength(1.0)
    source.SetZLength(1.0)

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0.2, 0.6, 0.9)

    renderer = vtkRenderer()
    renderer.AddActor(actor)
    renderer.SetBackground(0.1, 0.12, 0.16)
    renderer.ResetCamera()

    window = vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(960, 720)
    window.SetWindowName("VTK Cube Example")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)
    interactor.SetInteractorStyle(vtkInteractorStyleTrackballCamera())

    window.Render()
    interactor.Initialize()
    interactor.Start()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
