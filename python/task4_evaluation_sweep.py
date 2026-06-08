"""Task 4: Evaluation: Sweep Isovalues and Measure Triangle Count and Runtime."""
from __future__ import annotations

import os
import time
import subprocess
import sys

# Ensure matplotlib is installed
try:
    import matplotlib.pyplot as plt
except ImportError:
    print("Installing matplotlib...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"])
    import matplotlib.pyplot as plt
import numpy as np

if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
from vtkmodules.vtkImagingHybrid import vtkSampleFunction

def main() -> None:
    print("============================================")
    print(" Task 4: Sweeping Isovalues & Benchmarking")
    print("============================================")
    
    # 1. Dataset Setup
    # vtkRTAnalyticSource generates a good mix of peaks, valleys, and varying frequencies
    print("Generating mathematical volume data (vtkSuperquadric)...")
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)
    source = vtkSampleFunction()
    source.SetImplicitFunction(fn)
    source.SetSampleDimensions(60, 60, 60)
    source.SetModelBounds(-2, 2, -2, 2, -2, 2)
    
    # Warm up upstream pipeline
    source.Update()
    img_data = source.GetOutput()
    scalar_range = img_data.GetScalarRange()
    min_val, max_val = scalar_range
    print(f"Data generated. True scalar range: [{min_val:.2f}, {max_val:.2f}]")

    # 2. Setup Evaluation
    NUM_STEPS = 50
    # Create an array of isovalues sweeping across the scalar range
    # We shrink the range slightly to avoid empty corner cases at the absolute min/max
    margin = (max_val - min_val) * 0.05
    isovalues = np.linspace(min_val + margin, max_val - margin, NUM_STEPS)

    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(source.GetOutputPort())
    mc.MergePointsOn()
    mc.ComputeNormalsOn()

    tri_counts = []
    times_base = []
    times_span = []

    print(f"\nSweeping {NUM_STEPS} isovalues...")
    for iso in isovalues:
        # Baseline measurement
        mc.UseSpanSpaceOff()
        mc.SetIsovalue(iso)
        t0 = time.perf_counter()
        mc.Update()
        t1 = time.perf_counter()
        baseline_time = t1 - t0
        
        # Get triangle count from the baseline run
        polydata = mc.GetOutput()
        num_triangles = polydata.GetNumberOfCells()

        # Span Space measurement
        mc.UseSpanSpaceOn()
        mc.SetIsovalue(iso)
        t0 = time.perf_counter()
        mc.Update()
        t1 = time.perf_counter()
        span_time = t1 - t0

        tri_counts.append(num_triangles)
        times_base.append(baseline_time)
        times_span.append(span_time)
        
        # Progress indicator
        sys.stdout.write(f"\rEvaluating iso={iso:>6.1f} | Tris: {num_triangles:>7} | Base: {baseline_time:.4f}s | Span: {span_time:.4f}s")
        sys.stdout.flush()

    print("\n\nEvaluation complete! Generating plot...")

    # 3. Plotting results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Top Plot: Geometric Complexity
    ax1.plot(isovalues, tri_counts, color='purple', linewidth=2, marker='o', markersize=4)
    ax1.set_ylabel("Number of Triangles")
    ax1.set_title("Task 4: Isosurface Extraction Performance")
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Bottom Plot: Runtime Comparison
    ax2.plot(isovalues, times_base, color='red', label="Baseline (No Span Space)", linewidth=2, marker='s', markersize=4)
    ax2.plot(isovalues, times_span, color='blue', label="Accelerated (Span Space)", linewidth=2, marker='^', markersize=4)
    ax2.set_xlabel("Isovalue")
    ax2.set_ylabel("Runtime (seconds)")
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plot_filename = "task4_evaluation_plot.png"
    plt.savefig(plot_filename, dpi=150)
    print(f"Plot successfully saved to: {os.path.abspath(plot_filename)}")
    
    # Optionally display the plot on screen
    plt.show()

if __name__ == "__main__":
    main()
