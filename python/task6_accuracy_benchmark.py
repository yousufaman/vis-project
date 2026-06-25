"""Accuracy benchmark for task 6: evaluate surface area and volume of MC output."""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkCommonDataModel import vtkSphere
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.util.numpy_support import vtk_to_numpy

def main():
    resolutions = list(range(10, 151, 10)) # 10 to 150
    
    radius = 1.0
    exact_area = 4.0 * np.pi * (radius ** 2)
    exact_vol = (4.0 / 3.0) * np.pi * (radius ** 3)
    
    err_area = []
    err_vol = []
    
    for res in resolutions:
        # generate volume data
        sphere = vtkSphere()
        sphere.SetRadius(radius)
        sphere.SetCenter(0, 0, 0)
        
        source = vtkSampleFunction()
        source.SetImplicitFunction(sphere)
        source.SetSampleDimensions(res, res, res)
        # Model bounds should strictly contain the sphere
        source.SetModelBounds(-1.5, 1.5, -1.5, 1.5, -1.5, 1.5)
        source.Update()
        
        # Our MC
        mc = vtkVISMarchingCubes()
        mc.SetInputConnection(source.GetOutputPort())
        mc.MergePointsOn()
        mc.SetIsovalue(0.0)
        mc.Update()
        
        polydata = mc.GetOutput()
        
        if polydata.GetNumberOfCells() == 0:
            print(f"Res: {res} -> No triangles extracted!")
            err_area.append(1.0)
            err_vol.append(1.0)
            continue
            
        pts_array = polydata.GetPoints().GetData()
        points = vtk_to_numpy(pts_array)
        
        polys_array = polydata.GetPolys().GetData()
        polys = vtk_to_numpy(polys_array)
        
        # polys format: [3, i0, i1, i2, 3, i0, i1, i2, ...]
        indices = polys.reshape(-1, 4)[:, 1:]
        
        A = points[indices[:, 0]]
        B = points[indices[:, 1]]
        C = points[indices[:, 2]]
        
        # Triangle area: 0.5 * ||(B-A) x (C-A)||
        cross_prod = np.cross(B - A, C - A)
        areas = 0.5 * np.linalg.norm(cross_prod, axis=1)
        calc_area = np.sum(areas)
        
        # Tetrahedron volume from origin: 1/6 * A dot (B x C)
        # Note: Depending on normal direction, this could be negative, so we use abs() for the sum.
        # Actually, sum signed volumes first, then take abs.
        signed_vols = np.sum(A * np.cross(B, C), axis=1) / 6.0
        calc_vol = abs(np.sum(signed_vols))
        
        # Relative errors
        rel_err_a = abs(calc_area - exact_area) / exact_area
        rel_err_v = abs(calc_vol - exact_vol) / exact_vol
        
        err_area.append(rel_err_a)
        err_vol.append(rel_err_v)
        
        print(f"Res: {res:3d} | Area: {calc_area:.4f} (err: {rel_err_a:.2%}) | Vol: {calc_vol:.4f} (err: {rel_err_v:.2%})")

    # Plotting
    plt.figure(figsize=(9, 6))
    
    plt.plot(resolutions, err_area, 'o-', color='darkorange', linewidth=2, label="Surface Area Error")
    plt.plot(resolutions, err_vol, 's-', color='teal', linewidth=2, label="Volume Error")
    
    plt.title("Task 6: Isosurface Accuracy vs Resolution (Sphere R=1.0)")
    plt.xlabel("Resolution")
    plt.ylabel("Relative Error")
    plt.yscale('log') # Log scale is usually best for showing convergence
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.legend()
    
    plt.tight_layout()
    out_path = os.path.join(os.path.dirname(__file__), "..", "task6_plot.png")
    plt.savefig(out_path, dpi=150)
    print(f"Saved plot to {os.path.abspath(out_path)}")
    plt.show()

if __name__ == "__main__":
    main()
