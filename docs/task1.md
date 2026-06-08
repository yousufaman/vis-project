# Task 1: Scalar-Field Visualization with Isosurfaces

## Introduction: Isosurfaces and Marching Cubes

Many scientific datasets are defined as scalar fields: for every point in a 2D or 3D domain, the dataset stores a single value such as temperature, pressure, density, concentration, or intensity. An **isosurface** is the set of all points in a 3D scalar field that share the same scalar value. If we choose an isovalue `c`, the isosurface is the geometric locus of points where `f(x,y,z) = c`. In practice, isosurfaces are one of the most important techniques in visualization because they transform a volumetric dataset into an explicit geometric surface that can be rendered, shaded, measured, and compared.

Isosurfaces are especially useful when the chosen value corresponds to a meaningful physical boundary. For example, in medical imaging an isosurface might approximate bone or skin, in simulation data it might mark a pressure front, and in chemistry it might represent a level set of electron density. Choosing a good isovalue is therefore part of the interpretation task: different isovalues often reveal different structures in the same dataset.

The most influential algorithm for extracting isosurfaces from regular grids is **Marching Cubes**, introduced by Lorensen and Cline in 1987. The central idea is simple: the algorithm processes the volume cell by cell, where each cell is a cube formed by eight neighboring sample points. For a given isovalue, each vertex of the cube is classified as either above or below the threshold. This binary labeling determines how the isosurface intersects the cube. Rather than solving each case from scratch, Marching Cubes uses a lookup table that maps each vertex-sign configuration to a set of triangles. By "marching" through all cells and generating the corresponding local triangles, the algorithm constructs a polygonal approximation of the full isosurface.

Two technical ingredients are particularly important. First, intersection points along cell edges are not placed arbitrarily; they are usually found by linear interpolation between the scalar values at the two edge endpoints. This gives a more accurate geometric approximation than simply snapping intersections to grid locations. Second, surface normals can be derived from the gradient of the scalar field, which often produces much better shading than normals computed only from triangle connectivity. These details matter because they strongly affect surface quality, visual smoothness, and numerical fidelity.

Marching Cubes is a foundational algorithm in visualization because it combines a clean geometric idea with a number of deeper design questions: ambiguity handling, topology, interpolation accuracy, point sharing, memory use, acceleration structures, and parallel execution. It is also a very good implementation project because the basic method is accessible, while many meaningful extensions lead naturally into more advanced visualization research and systems issues.

### Suggested Reading

Students should read at least the original paper and one broader visualization reference before implementing the project.

1. William E. Lorensen and Harvey E. Cline. [Marching Cubes: A High Resolution 3D Surface Construction Algorithm](https://doi.org/10.1145/37402.37422). Proceedings of SIGGRAPH 1987.  
   This is the original Marching Cubes paper and the most important starting point for the project.

3. Kitware. [The VTK User's Guide](https://vtk.org/vtk-users-guide/) and the VTK textbook [The Visualization Toolkit: An Object-Oriented Approach to 3D Graphics](https://vtk.org/vtk-textbook/).  
   These are especially relevant for understanding how isosurface extraction fits into the VTK pipeline model and how existing VTK filters are structured.

4. Thomas Lewiner, Hélio Lopes, Antônio Wilson Vieira, and Geovan Tavares. [Efficient Implementation of Marching Cubes' Cases with Topological Guarantees](https://www.ks.uiuc.edu/Research/vmd/projects/ece498/surf/lewiner.pdf). Journal of Graphics Tools, 2003.  
   Recommended as a follow-up reading if you want to understand case handling, ambiguities, and improved implementations beyond the original algorithm.

As you read, focus on the following questions:

- What exactly is being approximated by the extracted triangle mesh?
- How does the cube-wise case table encode the local topology of the surface?
- Why do interpolation and normal computation matter for quality?
- What limitations of the original Marching Cubes algorithm motivate later extensions?

---

## Task 1: Implement Marching Cubes as a VTK Filter

Implement a VTK filter (`vtkVISMarchingCubes`) that extracts a single isosurface from a 3D scalar field on a regular grid and outputs a `vtkPolyData` triangle mesh. For this first task, focus on turning the algorithm described in the Marching Cubes paper into a clean, reusable VTK component. The paper should remain your primary source for the algorithm itself; the emphasis here is on implementing the algorithm properly inside the VTK data-flow model.

By the end of this task, you should have a reusable VTK filter that can be called from Python, inserted into a standard VTK pipeline, and used as the foundation for later extensions, comparisons, and performance studies.

Set up two demonstration pipelines:
- one that just shows the result from your algorithm for a specific isovalue
- one that shows your results side-by-side with VTK's isosurface implementation (`vtkContourFilter`)

How do you explain the differences that can be observed between your and VTK's implementation?

### Hints

- Start of with copying the example filter from the project repository into a new filter `vtkVISMarchingCubes`).

- Expose the isovalue through VTK setter/getter conventions so the filter is easy to script from Python.

- Keep the algorithmic core separated from VTK-specific boilerplate as much as possible. This makes it easier to test, reason about, and later optimize.

- `vtkImageData` is a very reasonable input restriction for the first version. It keeps the data model close to the assumptions in the literature and simplifies integration. You can generalize later.

- Compare your filter against the existing VTK contouring filter early, not because the outputs must match triangle-for-triangle, but because it helps you validate data flow, output type, and basic geometric plausibility.

- You can use an actor's `SetPosition` method to achieve side-by-side views.

## Task 2: Add Point Merging and Gradient Normals

The MC algorithm produces triangles separately from each other, however, the triangle corners originate a repeated since they originate from the same edges. Extend your `vtkVISMarchingCubes` filter so that it produces a surface representation with shared vertices and gradient-based normals. The goal of this task is to move from a minimal baseline implementation toward a more realistic isosurface extraction filter and to study how these design choices affect both mesh structure and visual quality.

Make sure your implementation works by using the demonstration pipeline from Task1. Set up a third comparison pipeline to compare gradient-based normals side-by-side against a generic surface normal algorithm (`vtkSurfaceNormal` filter).

### Hints

- Treat this as an extension of the existing filter, not as a separate implementation. The interface and output should remain compatible with the pipeline structure you established in Task 1.

- Think carefully about where point merging belongs architecturally. It should improve the structure of the output mesh without making the filter interface harder to use in Python.

- Make the new behavior configurable through the filter API so you can switch features on and off during comparison.

- Choose test datasets where shading differences are easy to see. Smooth implicit surfaces are often more informative here than highly noisy volumes.

- When comparing against generic surface-normal computation, focus not only on visual quality but also on what information each method uses. That conceptual difference is more important than whether one image simply "looks better." Which one represents the data better?

## Task 3: Accelerate the Algorithm with Span Spacing

In this task, extend your `vtkVISMarchingCubes` filter with a span-space-based acceleration strategy following the paper of [Livnat et al.](https://doi.org/10.1109/2945.489388). The goal is to move beyond a purely cell-by-cell extraction approach and to study how preprocessing can reduce the amount of work required for a given isovalue query.

Your implementation should remain compatible with the demonstration pipelines from the previous tasks. In addition, set up a comparison that lets you switch between the baseline implementation and the span-space-enhanced version for the same dataset and isovalue. A full benchmark is not needed, this is the object of the next task.

Set up a comparison pipeline that allows you to visually inspect that the result of your algorithm is unchanged whether acceleration is enabled or not.

### Hints

- Again, treat span space as an extension of your existing filter design, not as a separate algorithm with a separate user-facing interface.

- Expose the accelerated mode in a way that makes it easy to compare against the non-accelerated baseline from Python, i.e. by a parameter that can enable it selectively.

- Keep the filter interface stable. Later tasks will build on this implementation, so the acceleration should fit naturally into the architecture you already established.

## Task 4: Evaluation: Sweep Isovalues and Measure Triangle Count and Runtime

Set up a Python/VTK evaluation pipeline that, for a given dataset, steps through a range of isovalues from the minimum scalar value to the maximum scalar value and records two quantities for each extraction: the number of generated triangles and the runtime of the extraction. The goal of this task is to move from isolated visual inspection to a more systematic view of how the behavior of the algorithm depends on the chosen isovalue – especially the runtime, so the advantages of span spacing can become better understood.

Use this pipeline with your current implementation of `vtkVISMarchingCubes`. The result should not just be a script that runs the filter repeatedly, but a small experimental setup that helps you observe trends across the scalar range of the dataset.

By the end of this task, you should be able to produce a plot or table that relates isovalue, triangle count, and runtime, and use it to discuss where extraction is cheap or expensive and how geometric complexity and runtime appear to be related. Create plots that allow you to understand this data visually (using e.g. matplotlib).

### Hints

- Keep this as a Python-side evaluation pipeline rather than embedding measurement logic into the filter itself. You can measure the triangle count of the output polydata and do Python-side timing of your filter's `Update` method. Should you use CPU time or wall time?

- Make sure that all upstream filters – e.g. data loading – are "warm" in the sense that their computations are cached before you measure the series.

- Make sure the range of sampled isovalues is derived from the actual scalar range of the input dataset rather than chosen arbitrarily.

- Expect the relationship between isovalue and runtime to be dataset-dependent. The point of the task is not only to collect numbers, but to interpret why peaks and valleys occur. Test over several datasets.

- Keep the measurement setup reusable. Later tasks will likely compare multiple algorithmic variants on the same dataset, so it is useful if the evaluation pipeline can be adapted rather than rewritten.

## Task 5: Evaluation: Design a Controlled Benchmark Dataset

Design a synthetic benchmark dataset for which the number of triangles generated at a chosen isovalue is known in advance or can be predicted analytically with high confidence. You should be able to control the resolution of the data. 

Use this dataset to study the runtime behavior of your span-space implementation and to compare it against both your non-accelerated implementation and VTK's built-in Marching Cubes implementation.

The goal of this task is to move from exploratory measurement to controlled benchmarking. Rather than only observing whatever behavior happens to appear in a given real dataset, you should now construct a dataset whose structure helps you reason about the expected output complexity and about why one implementation may outperform another.

By the end of this task, you should have a benchmark setup that combines a synthetic dataset, a known or well-justified expected triangle count for a selected isovalue, and a comparative runtime study across at least three variants:
- your baseline `vtkVISMarchingCubes`
- your span-space-enhanced implementation
- VTK's built-in isosurface extraction filter

Use the results to determine not only which variant is faster, but also under what conditions the span-space approach appears to help and how well the measured runtime aligns with your expectations from the constructed dataset.

### Hints

- Keep the benchmark synthetic and simple enough that you can reason about it, but large enough that runtime differences are measurable. Some complexity is needed; e.g., planar isosurfaces are not insightful.

- An easy way to construct the synthetic data is to sample an analytic formula at the vertices of a given grid. Consider using `vtkSampleFunction`.

- Reuse the benchmark harness from Task 4.

- Use the known triangle count as a validation tool as well as a benchmarking tool. If an implementation produces an unexpected number of triangles, that is already an important result.

- When comparing against VTK's built-in filter, be explicit about which implementation you use as the reference and whether differences in output structure, point merging, or normal handling could influence runtime or output size.

## Task 6: Evaluation: Design a Geometric Accuracy Benchmark

Design a synthetic benchmark dataset whose isosurface has known geometric properties, in particular surface area and enclosed volume. Use this dataset to evaluate how accurately Marching Cubes reproduces these properties. The main goal is again evaluation; not in runtime, but regarding geometric fidelity. Furthermore, study the effect of resolution: As you increase the resolution of the synthetic data, the propeties of isosurfaces should converge to the properties of the analytical isosurface.

Extend your previous benchmarking implementation to measure these properties over a range of isovalues and/or resolutions. From the resulting data, create sensible plots and interpret the results.

### Hints

- Choose functions whose (analytical) isosurfaces have known properties or can be derived easily, e.g., spheres. The benchmark is most useful when you can know what the correct answer should be before running the extraction.

- As in Task 5, an analytic scalar field sampled onto a regular grid is a natural way to build the dataset. What matters here is not only simplicity, but also the availability of meaningful ground truth.

- Think carefully about what it means to compare a triangulated approximation to a smooth analytical surface. Surface area and enclosed volume are only two views of the error, not the whole story. In which cases could this evaluation "hide" systematic errors in your algorithm?

## Task 7a:

Extend your `vtkVISMarchingCubes` filter to handle topological ambiguities in a topologically correct way, following the approach described by Lewiner et al. The goal of this task is to move beyond geometric extraction and runtime considerations and to study how case handling affects the topology of the reconstructed surface.

Use this extension to compare three variants:
- your classical Marching Cubes implementation
- your topologically-correct variant following Lewiner
- VTK's built-in implementation

The point of the task is not only to observe whether the meshes look different, but to understand when topological correctness matters and how ambiguous configurations affect the extracted surface. In particular, revisit the validation setups from Tasks 5 and 6 and discuss whether they are affected by this change. Are triangle-count-based runtime benchmarks still meaningful in the same way? Do geometric measures such as area, volume, or Hausdorff distance become more informative, less informative, or simply different once topology is handled differently?

By the end of this task, you should have a topologically-aware variant of your filter together with a comparison study that highlights when ambiguity resolution changes the result and what this means for the evaluations you designed earlier.

### Hints

- Treat topological correctness as another extension of the same filter family rather than as an unrelated implementation. It should remain possible to compare classical and topologically-correct behavior within a common interface.

- Choose test data that is likely to trigger ambiguous cases. Without such data, the topological extension may appear to have no effect.

- Compare not only rendered images, but also structural properties of the extracted mesh. The important question is whether the topology of the result changes, not only whether the shading looks different.

- Revisit Tasks 5 and 6 explicitly. If ambiguity resolution changes the number of generated triangles or the geometry of the output surface, then earlier validation and benchmarking conclusions may need to be qualified.

- When discussing VTK's implementation, be precise about what aspect you are comparing: output geometry, topology, triangle count, or behavior on ambiguous cases.

## Task 7b: Parallelize and Study Scalability

Parallelize both your original `vtkVISMarchingCubes` implementation and your span-space-enhanced implementation using `VTKSMPTools`. The goal of this task is to turn your filter from a correct serial implementation into a parallel VTK component and to study how well the resulting implementation scales with the number of available cores.

This task should again have an evaluation component. After parallelizing the code, perform a small scalability study in which you vary the number of threads or cores and measure the resulting runtime. The purpose is not only to obtain speedups, but to understand which parts of the algorithm parallelize well and where bottlenecks remain.

### Hints

- Treat parallelism as another extension of the same filter rather than as a separate code path with a different interface.

- Think carefully about which parts of the computation are embarrassingly parallel and which parts require coordination, especially when writing output data structures.

- Use different parallelization strategies for the "normal" MC algorithm and for the span-space-accelerated algorithm. In the former case, paralellize over the full cell range. For span spaces, first produce a candidate list of cells (serially), then parallelize over the candidates.

- Collecting triangles in a single dataset concurrently is difficult or requires locking. Rather, emit triangles into a per-thread polydata (with the help of `vtkSMPThreadLocalObject`) and merge these into one polydata object (`vtkAppendPolyData` filter).

- Keep correctness checks in place while parallelizing. A parallel implementation is only useful if it still produces the same output as the serial version.

- Use a small but meaningful range of thread counts for the scalability study, for example from one thread up to the number of physical or logical cores available on the machine. Create suitable plots and interpret the results.

- Reuse the measurement harness from the previous tasks rather than building a separate benchmarking framework just for parallel experiments.

- When interpreting the results, focus not only on raw speedup but also on why scaling may flatten out. Which parts of your algorithm are not parallel? It may be helpful to consider [Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law). 

- If you're tempted to parallelize other parts of your MC filter (e.g. point merging), we won't keep you from doing that.
