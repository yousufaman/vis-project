import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

import vtk
import time
import matplotlib.pyplot as plt
import vtkVISFilters as vis

def benchmark(res):
    # generate a large sphere dataset
    sphere = vtk.vtkSphere()
    sphere.SetRadius(0.8)
    sphere.SetCenter(0,0,0)
    
    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(sphere)
    sample.SetModelBounds(-1, 1, -1, 1, -1, 1)
    sample.SetSampleDimensions(res, res, res)
    sample.Update()
    
    img = sample.GetOutput()
    
    # Serial
    mc_serial = vis.vtkVISMarchingCubes()
    mc_serial.SetInputData(img)
    mc_serial.SetIsovalue(0.0)
    mc_serial.SetUseParallel(False)
    
    t0 = time.time()
    mc_serial.Update()
    t_serial = time.time() - t0
    
    # Parallel
    mc_parallel = vis.vtkVISMarchingCubes()
    mc_parallel.SetInputData(img)
    mc_parallel.SetIsovalue(0.0)
    mc_parallel.SetUseParallel(True)
    
    t0 = time.time()
    mc_parallel.Update()
    t_parallel = time.time() - t0
    
    return t_serial, t_parallel

resolutions = [50, 100, 150, 200]
t_serials = []
t_parallels = []
speedups = []

print("Running Scalability Benchmark (Task 7b)")
for r in resolutions:
    print(f"Resolution {r}x{r}x{r}...")
    ts, tp = benchmark(r)
    t_serials.append(ts)
    t_parallels.append(tp)
    speedups.append(ts / tp if tp > 0 else 1.0)
    print(f"  Serial: {ts:.3f}s | Parallel: {tp:.3f}s | Speedup: {ts/tp:.2f}x")

plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.plot(resolutions, t_serials, 'o-', label='Serial')
plt.plot(resolutions, t_parallels, 's-', label='Parallel')
plt.xlabel('Resolution')
plt.ylabel('Runtime (s)')
plt.title('Runtime Comparison')
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(resolutions, speedups, '^-', color='green')
plt.xlabel('Resolution')
plt.ylabel('Speedup (T_serial / T_parallel)')
plt.title('Parallel Speedup')
plt.grid(True)

plt.tight_layout()
plt.savefig('task7b_plot.png')
print("Saved plot to task7b_plot.png")
