"""Controlled benchmark for task 5: our MC (base vs spanspace) vs vtkContourFilter."""

import os
import time
import sys

import matplotlib.pyplot as plt
import numpy as np

if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonDataModel import vtkSphere
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkFiltersCore import vtkContourFilter

def main():
    resolutions = [20, 40, 60, 80, 100]
    
    tri_counts = []
    t_base = []
    t_span = []
    t_vtk = []
    
    radius = 0.5
    isovalue = 0.0 # for a sphere implicit function, 0 is the surface
    
    for res in resolutions:
        # generate volume data
        sphere = vtkSphere()
        sphere.SetRadius(radius)
        sphere.SetCenter(0, 0, 0)
        
        source = vtkSampleFunction()
        source.SetImplicitFunction(sphere)
        source.SetSampleDimensions(res, res, res)
        # Bounds slightly larger than radius
        source.SetModelBounds(-1, 1, -1, 1, -1, 1)
        source.Update()
        
        # Our MC - Base
        mc_base = vtkVISMarchingCubes()
        mc_base.SetInputConnection(source.GetOutputPort())
        mc_base.MergePointsOn()
        mc_base.ComputeNormalsOn()
        mc_base.UseSpanSpaceOff()
        mc_base.SetIsovalue(isovalue)
        
        t0 = time.perf_counter()
        mc_base.Update()
        dt_b = time.perf_counter() - t0
        ntri_b = mc_base.GetOutput().GetNumberOfCells()
        
        # Our MC - Span Space
        mc_span = vtkVISMarchingCubes()
        mc_span.SetInputConnection(source.GetOutputPort())
        mc_span.MergePointsOn()
        mc_span.ComputeNormalsOn()
        mc_span.UseSpanSpaceOn()
        mc_span.SetIsovalue(isovalue)
        
        t0 = time.perf_counter()
        mc_span.Update()
        dt_s = time.perf_counter() - t0
        ntri_s = mc_span.GetOutput().GetNumberOfCells()
        
        # vtkContourFilter
        vtk_cf = vtkContourFilter()
        vtk_cf.SetInputConnection(source.GetOutputPort())
        vtk_cf.SetValue(0, isovalue)
        vtk_cf.ComputeNormalsOn()
        
        t0 = time.perf_counter()
        vtk_cf.Update()
        dt_v = time.perf_counter() - t0
        ntri_v = vtk_cf.GetOutput().GetNumberOfCells()
        
        print(f"Res: {res}^3")
        print(f"  Tris -> Base: {ntri_b}, Span: {ntri_s}, VTK: {ntri_v}")
        print(f"  Time -> Base: {dt_b:.4f}s, Span: {dt_s:.4f}s, VTK: {dt_v:.4f}s")
        
        if not (ntri_b == ntri_s == ntri_v):
            print(f"  WARNING: Triangle counts do not match at res {res}!")
            
        tri_counts.append(ntri_b)
        t_base.append(dt_b)
        t_span.append(dt_s)
        t_vtk.append(dt_v)

    # Plotting
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(resolutions, tri_counts, 'k-', linewidth=2, marker='o')
    ax1.set_ylabel("Triangle Count")
    ax1.set_title("Task 5: Controlled Benchmark")
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.plot(resolutions, t_base, 'r-', label="Our MC (No Span Space)", linewidth=2, marker='s')
    ax2.plot(resolutions, t_span, 'b-', label="Our MC (Span Space)", linewidth=2, marker='^')
    ax2.plot(resolutions, t_vtk, 'g-', label="vtkContourFilter", linewidth=2, marker='d')
    ax2.set_xlabel("Resolution")
    ax2.set_ylabel("Runtime (s)")
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "..", "task5_plot.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot to {os.path.abspath(out_path)}")
    # We won't block with plt.show() so the batch script can run smoothly, or maybe we will since task4 does.
    # Actually, it's better to just save, but task4 did plt.show(). I'll leave it out for CI, or I'll just put it.
    # The prompt doesn't ask for it to be interactive, just "save plot as task5_plot.png".
    plt.show()

if __name__ == "__main__":
    main()
