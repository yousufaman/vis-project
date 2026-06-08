"""Sweep isovalues and plot triangle count + runtime (baseline vs span space)."""

import os
import time
import sys

import matplotlib.pyplot as plt
import numpy as np

if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonDataModel import vtkSuperquadric
from vtkmodules.vtkImagingHybrid import vtkSampleFunction


def main():
    # generate volume data
    fn = vtkSuperquadric()
    fn.SetPhiRoundness(2.5)
    fn.SetThetaRoundness(0.5)
    source = vtkSampleFunction()
    source.SetImplicitFunction(fn)
    source.SetSampleDimensions(60, 60, 60)
    source.SetModelBounds(-2, 2, -2, 2, -2, 2)
    source.Update()

    data = source.GetOutput()
    srange = data.GetScalarRange()
    print(f"Scalar range: [{srange[0]:.2f}, {srange[1]:.2f}]")

    # sweep settings
    n_steps = 50
    margin = (srange[1] - srange[0]) * 0.05
    isovalues = np.linspace(srange[0] + margin, srange[1] - margin, n_steps)

    mc = vtkVISMarchingCubes()
    mc.SetInputConnection(source.GetOutputPort())
    mc.MergePointsOn()
    mc.ComputeNormalsOn()

    tri_counts = []
    t_baseline = []
    t_spanspace = []

    print(f"Running {n_steps} isovalues...")
    for i, iso in enumerate(isovalues):
        # baseline
        mc.UseSpanSpaceOff()
        mc.SetIsovalue(iso)
        t0 = time.perf_counter()
        mc.Update()
        dt_b = time.perf_counter() - t0

        ntri = mc.GetOutput().GetNumberOfCells()

        # span space
        mc.UseSpanSpaceOn()
        mc.SetIsovalue(iso)
        t0 = time.perf_counter()
        mc.Update()
        dt_s = time.perf_counter() - t0

        tri_counts.append(ntri)
        t_baseline.append(dt_b)
        t_spanspace.append(dt_s)

        print(f"\r  [{i+1}/{n_steps}] iso={iso:.1f}  tris={ntri}  base={dt_b:.4f}s  span={dt_s:.4f}s", end="")

    print("\nDone. Plotting...")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    ax1.plot(isovalues, tri_counts, 'purple', linewidth=2, marker='o', markersize=3)
    ax1.set_ylabel("Triangle count")
    ax1.set_title("Isosurface Evaluation")
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.plot(isovalues, t_baseline, 'r-', label="Baseline", linewidth=2, marker='s', markersize=3)
    ax2.plot(isovalues, t_spanspace, 'b-', label="Span Space", linewidth=2, marker='^', markersize=3)
    ax2.set_xlabel("Isovalue")
    ax2.set_ylabel("Time (s)")
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.6)

    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "..", "task4_evaluation_plot.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot to {os.path.abspath(out_path)}")
    plt.show()


if __name__ == "__main__":
    main()
