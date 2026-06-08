"""Task 3: visual + timing comparison of baseline vs span space acceleration."""

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


def build_pipeline(source, isovalue, use_span):
    """Build MC pipeline with or without span space."""
    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(source.GetOutputPort())
    mc.SetIsovalue(isovalue)
    mc.MergePointsOn()
    mc.ComputeNormalsOn()
    if use_span:
        mc.UseSpanSpaceOn()
    else:
        mc.UseSpanSpaceOff()

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(mc.GetOutputPort())
    mapper.ScalarVisibilityOff()

    actor = vtkActor()
    actor.SetMapper(mapper)
    return mc, actor


def main():
    colors = vtkNamedColors()
    ISO = 2.0

    # create two separate sample volumes
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)

    def make_vol():
        s = vtkSampleFunction()
        s.SetImplicitFunction(fn)
        s.SetSampleDimensions(60, 60, 60)
        s.SetModelBounds(-2, 2, -2, 2, -2, 2)
        return s

    mc_base, actor_base = build_pipeline(make_vol(), ISO, use_span=False)
    mc_span, actor_span = build_pipeline(make_vol(), ISO, use_span=True)

    actor_base.GetProperty().SetColor(colors.GetColor3d("PeachPuff"))
    actor_base.GetProperty().SetSpecular(0.3)
    actor_base.GetProperty().SetSpecularPower(30)

    actor_span.GetProperty().SetColor(colors.GetColor3d("LightBlue"))
    actor_span.GetProperty().SetSpecular(0.3)
    actor_span.GetProperty().SetSpecularPower(30)

    # viewports
    ren_l = vtkRenderer()
    ren_r = vtkRenderer()
    ren_l.SetViewport(0, 0, 0.5, 1)
    ren_r.SetViewport(0.5, 0, 1, 1)

    ren_l.AddActor(actor_base)
    ren_l.SetBackground(0.12, 0.14, 0.18)

    ren_r.AddActor(actor_span)
    ren_r.SetBackground(0.14, 0.12, 0.22)

    # quick label helper
    for ren, txt in [(ren_l, "Baseline"), (ren_r, "Span Space")]:
        lbl = vtkTextActor()
        lbl.SetInput(txt)
        lbl.GetTextProperty().SetFontSize(20)
        lbl.GetTextProperty().SetColor(1, 1, 1)
        lbl.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        lbl.SetPosition(0.05, 0.05)
        ren.AddActor(lbl)

    for r in (ren_l, ren_r):
        r.ResetCamera()
        r.GetActiveCamera().Elevation(20)
        r.GetActiveCamera().Azimuth(30)

    win = vtkRenderWindow()
    win.AddRenderer(ren_l)
    win.AddRenderer(ren_r)
    win.SetSize(1400, 700)
    win.SetWindowName("Task 3: Span Space Acceleration")

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(win)

    # warm up both pipelines first
    print("Warming up...")
    mc_base.Update()
    mc_span.Update()

    # now time with a different isovalue
    test_iso = 1.0
    print(f"\nTiming at isovalue {test_iso}:")

    mc_base.SetIsovalue(test_iso)
    t0 = time.time()
    mc_base.Update()
    dt_base = time.time() - t0

    mc_span.SetIsovalue(test_iso)
    t0 = time.time()
    mc_span.Update()
    dt_span = time.time() - t0

    out_b = mc_base.GetOutput()
    out_s = mc_span.GetOutput()
    print(f"  Baseline:   {dt_base*1000:.1f} ms  ({out_b.GetNumberOfPoints()} pts, {out_b.GetNumberOfCells()} tris)")
    print(f"  Span Space: {dt_span*1000:.1f} ms  ({out_s.GetNumberOfPoints()} pts, {out_s.GetNumberOfCells()} tris)")

    win.Render()
    iren.Start()


if __name__ == "__main__":
    main()
