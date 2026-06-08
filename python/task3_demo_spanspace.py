"""Demo 3: Side-by-side comparison — Baseline vs Span Space Accelerated."""
from __future__ import annotations

import os
import time
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
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
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(pipeline_end.GetOutputPort())
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

    sample_left  = make_sample()
    sample_right = make_sample()

    # Left: Baseline (UseSpanSpaceOff)
    mc_left = vtkVISMarchingCubes()
    mc_left.SetInputConnection(sample_left.GetOutputPort())
    mc_left.SetIsovalue(ISOVALUE)
    mc_left.MergePointsOn()
    mc_left.ComputeNormalsOn()
    mc_left.UseSpanSpaceOff()
    
    actor_left = make_actor(mc_left, colors.GetColor3d("PeachPuff"))

    # Right: Accelerated (UseSpanSpaceOn)
    mc_right = vtkVISMarchingCubes()
    mc_right.SetInputConnection(sample_right.GetOutputPort())
    mc_right.SetIsovalue(ISOVALUE)
    mc_right.MergePointsOn()
    mc_right.ComputeNormalsOn()
    mc_right.UseSpanSpaceOn()
    
    actor_right = make_actor(mc_right, colors.GetColor3d("LightSkyBlue"))

    # Renderers with split viewports
    ren_left  = vtkRenderer()
    ren_right = vtkRenderer()
    ren_left.SetViewport(0.0, 0.0, 0.5, 1.0)
    ren_right.SetViewport(0.5, 0.0, 1.0, 1.0)

    ren_left.AddActor(actor_left)
    ren_left.AddActor(make_label("Baseline (UseSpanSpace=Off)"))
    ren_left.SetBackground(colors.GetColor3d("DarkSlateGray"))

    ren_right.AddActor(actor_right)
    ren_right.AddActor(make_label("Accelerated (UseSpanSpace=On)"))
    ren_right.SetBackground(colors.GetColor3d("DarkSlateBlue"))

    for ren in (ren_left, ren_right):
        ren.ResetCamera()
        ren.GetActiveCamera().Elevation(20)
        ren.GetActiveCamera().Azimuth(30)

    window = vtkRenderWindow()
    window.AddRenderer(ren_left)
    window.AddRenderer(ren_right)
    window.SetSize(1400, 700)
    window.SetWindowName("Task 3: Span Space Acceleration Comparison")

    interactor = vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    # First update: pre-caches the span space on the right side
    print("Pre-caching pipelines...")
    mc_left.Update()
    mc_right.Update()

    # Measure time for a new isovalue
    NEW_ISO = 1.0
    print(f"\nEvaluating extraction at new isovalue: {NEW_ISO}")
    
    mc_left.SetIsovalue(NEW_ISO)
    t0 = time.time()
    mc_left.Update()
    t_base = time.time() - t0

    mc_right.SetIsovalue(NEW_ISO)
    t0 = time.time()
    mc_right.Update()
    t_span = time.time() - t0

    print(f"Baseline:     time={t_base:.4f}s  points={mc_left.GetOutput().GetNumberOfPoints():>7}  triangles={mc_left.GetOutput().GetNumberOfCells():>7}")
    print(f"Span Space:   time={t_span:.4f}s  points={mc_right.GetOutput().GetNumberOfPoints():>7}  triangles={mc_right.GetOutput().GetNumberOfCells():>7}")

    window.Render()
    interactor.Start()


if __name__ == "__main__":
    main()
