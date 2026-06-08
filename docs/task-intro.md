# Introduction

## VTK and the Pipeline Model

The Visualization Toolkit (VTK) is an open-source software system for 3D computer graphics, image processing, and scientific visualization. It provides a large library of algorithms covering isosurface extraction, volume rendering, flow visualization, surface processing, and much more. VTK is implemented in C++ and exposes Python bindings, which means you can write algorithm-level code in C++ for performance and assemble visualization pipelines in Python for flexibility. All implementation projects in this course follow this hybrid workflow.

Before starting any of the implementation tasks, it is worth spending time understanding how VTK structures computation. The central concept in VTK is the **data-flow pipeline**: a directed graph of objects that produce, transform, and consume data. The pipeline is lazy — no computation happens until you explicitly request an update, and VTK tracks which parts of the pipeline are outdated and only recomputes what is necessary.

### Why this matters for the project

In the later assignments, you will not just call built-in VTK filters. You will implement your own C++ filters and then use them from Python exactly like native VTK components. That means the basic workflow in this introduction is already the workflow you will use throughout the project:

- create or load data with a source
- connect filters through output ports
- map the resulting data for rendering
- inspect the result in Python
- change parameters and rerun the pipeline

The goal of this document is not to teach all of VTK. It is to give you enough understanding of the core mechanisms that later tasks can focus on visualization ideas rather than on pipeline confusion.

### Suggested Reading

Before working through the examples below, check out the following references that can be helpful throughout the project:

1. Kitware. [The VTK User's Guide](https://vtk.org/vtk-users-guide/).  
   Chapter 4 covers the pipeline model. Chapter 5 introduces the key data structures.

2. Will Schroeder, Ken Martin, and Bill Lorensen. [The Visualization Toolkit: An Object-Oriented Approach to 3D Graphics](https://vtk.org/vtk-textbook/).  
   Chapters 3 and 4 explain the architecture and the rendering model respectively.

3. VTK Getting Started: [https://docs.vtk.org/en/latest/getting_started/index.html](https://docs.vtk.org/en/latest/getting_started/index.html)

5. VTK Python API notes: [https://docs.vtk.org/en/latest/api/python.html](https://docs.vtk.org/en/latest/api/python.html)
6. VTK example `ColoredSphere`: [https://examples.vtk.org/site/Python/Rendering/ColoredSphere/](https://examples.vtk.org/site/Python/Rendering/ColoredSphere/)
7. VTK example `SampleFunction`: [https://examples.vtk.org/site/Python/ImplicitFunctions/SampleFunction/](https://examples.vtk.org/site/Python/ImplicitFunctions/SampleFunction/)

As you read, focus on the following questions:

- What is the difference between a source, a filter, and a sink in the VTK pipeline?
- When does VTK actually execute computation, and what triggers it?
- How does VTK decide which parts of the pipeline need to be re-executed after a parameter changes?
- What is the role of the mapper, and why is it separate from the filter?

---

### The VTK Data-Flow Pipeline

Every VTK pipeline is built from three types of objects.

**Sources** are objects at the head of the pipeline that produce data without requiring any upstream input. They represent either data generators — such as a sphere or a structured grid sampled from an analytic function — or data readers that load a dataset from disk. Examples include `vtkSphereSource`, `vtkConeSource`, `vtkXMLImageDataReader`, and `vtkSampleFunction`. A source fully specifies the data that flows into the rest of the pipeline.

**Filters** are the computational heart of a VTK pipeline. A filter takes one or more upstream datasets as input, applies an algorithm, and produces a new dataset as output. The upstream connection is made by calling `SetInputConnection` with the output port of the previous object. VTK includes hundreds of filters covering geometry processing, scalar computation, surface extraction, resampling, and more. The filters you implement in these projects (`vtkVISMarchingCubes` and others) are designed to plug into this model as first-class pipeline components.

![VTK Pipeline](https://www.cs.uic.edu/~jbell/CS526/Tutorial/VTK_Pipeline.jpg)

**Sinks** (Mapper + Actor + Renderer) consume data, either by rendering it or by writing it to disk. For rendering, the most common sink is the **mapper**, which converts a `vtkDataSet` into rendering primitives. The mapper is connected to an **actor**, which holds both the mapper and the visual properties of the object (color, opacity, representation mode). Actors live inside a **renderer**, which manages a collection of actors, a camera, and lighting. The renderer is owned by a **render window**, which handles display.

Two method calls appear everywhere in pipeline code:

- `GetOutputPort()` exposes a pipeline output so another object can connect to it.
- `SetInputConnection(...)` connects one stage of the pipeline to the next.

When you see code like this

```python
mapper.SetInputConnection(filter.GetOutputPort())
```

you should read it as: "take the output of this upstream pipeline object and make it the input of the next stage."

This chain is explicit and composable. Any filter whose output type is compatible with the next filter's expected input can be inserted or removed from the chain without touching the rest of the pipeline.


---

### Examples

The following four examples build progressively from the smallest working rendering pipeline to a pattern close to the actual course workflow. Work through them in order.

#### Example 1: The Smallest Useful Rendering Pipeline

This first example shows the smallest rendering pipeline that is still representative of normal VTK usage. The purpose is to see the basic rendering chain clearly: source, mapper, actor, renderer, render window.

```python
import vtk

sphere = vtk.vtkSphereSource()
sphere.SetRadius(1.0)
sphere.SetThetaResolution(32)
sphere.SetPhiResolution(32)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(sphere.GetOutputPort())

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.9, 0.5, 0.2)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.1, 0.15)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(800, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

window.Render()
interactor.Start()
```

What to notice:

- `vtkSphereSource` is a **source**. It generates geometry for us.
- `vtkPolyDataMapper` is downstream of the source and connects through `SetInputConnection(sphere.GetOutputPort())`.
- `vtkActor` does not compute geometry. It stores how geometry should be shown.
- `window.Render()` triggers the actual computation needed for display.
- Even this simple script already uses the same pattern you will reuse later with more complex filters.

#### Example 2: Inserting a Filter

The next example adds a real filter into the pipeline. This matters because most project work is not about sources or rendering setup, but about inserting algorithms between them.

```python
import vtk

sphere = vtk.vtkSphereSource()
sphere.SetRadius(1.0)
sphere.SetThetaResolution(48)
sphere.SetPhiResolution(48)

elevation = vtk.vtkElevationFilter()
elevation.SetInputConnection(sphere.GetOutputPort())
elevation.SetLowPoint(0.0, 0.0, -1.0)
elevation.SetHighPoint(0.0, 0.0, 1.0)

mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(elevation.GetOutputPort())
mapper.SetScalarRange(-1.0, 1.0)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.15, 0.18, 0.2)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(800, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

window.Render()
interactor.Start()
```

What to notice:

- `vtkElevationFilter` is a genuine **filter** between source and mapper.
- The pipeline pattern did not change. You only inserted a new stage.
- The filter adds scalar values to the geometry, and the mapper uses those values for coloring.
- This is the key idea behind composability in VTK: if input and output types match, filters can be chained naturally.

#### Example 3: From Sampled Volume to Isosurface

This example is the most relevant one for later scalar-field tasks. It creates a sampled volumetric field and then extracts an isosurface from it. This is structurally very close to the pipelines you will build later with `vtkContourFilter` and with your own custom isosurface filters.

```python
import vtk

implicit_function = vtk.vtkSuperquadric()
implicit_function.SetPhiRoundness(2.5)
implicit_function.SetThetaRoundness(0.5)

sample = vtk.vtkSampleFunction()
sample.SetImplicitFunction(implicit_function)
sample.SetSampleDimensions(50, 50, 50)
sample.SetModelBounds(-2.0, 2.0, -2.0, 2.0, -2.0, 2.0)

contour = vtk.vtkContourFilter()
contour.SetInputConnection(sample.GetOutputPort())
contour.SetValue(0, 2.0)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(contour.GetOutputPort())
mapper.ScalarVisibilityOff()

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(0.9, 0.9, 0.95)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.08, 0.08, 0.12)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)
window.SetSize(800, 600)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

window.Render()
interactor.Start()
```

What to notice:

- `vtkSampleFunction` is a **source** that produces sampled volume data rather than polygonal geometry.
- `vtkContourFilter` is a **filter** that extracts an isosurface from scalar data.
- The input is conceptually volumetric; the output is polygonal, which is why the downstream mapper is `vtkPolyDataMapper`.
- This is very close to the course workflow for Marching Cubes: scalar field in, surface out.

#### Example 4: Understanding Updates and Dataflow

VTK uses **demand-driven execution**. Creating the pipeline does not immediately run the algorithm. Computation happens when some downstream object requests data, typically through `Render()` or explicitly through `Update()`.

This example uses `Update()` so you can observe the effect directly in Python without focusing on the rendering window.

```python
import vtk

sphere = vtk.vtkSphereSource()
sphere.SetRadius(1.0)
sphere.SetThetaResolution(8)
sphere.SetPhiResolution(8)

normals = vtk.vtkPolyDataNormals()
normals.SetInputConnection(sphere.GetOutputPort())

normals.Update()
output_1 = normals.GetOutput()
print("First point count:", output_1.GetNumberOfPoints())

sphere.SetThetaResolution(32)
sphere.SetPhiResolution(32)

normals.Update()
output_2 = normals.GetOutput()
print("Second point count:", output_2.GetNumberOfPoints())
```

What to notice:

- `Update()` is an explicit request for current output data.
- After the source parameters change, the downstream filter sees that its input is outdated and recomputes when `Update()` is called again.
- The pipeline connection matters: because `normals` is connected to `sphere` through `SetInputConnection(...)`, VTK knows which upstream object must be asked for fresh data.
- `Render()` works similarly in a rendering pipeline. A mapper requests data, which triggers upstream execution as needed.

Conceptually, you can think of VTK objects as carrying a "modified time." When you call a setter such as `SetThetaResolution(...)`, VTK marks the object as changed. The next downstream request then updates only the affected part of the pipeline. This is why VTK pipelines are reusable and interactive instead of being one-shot scripts.

---

### Data Representations

You do not need to memorize the full VTK data model now, but you should know the most important data types for the later assignments.

- `vtkImageData`: a regular rectilinear grid with uniform spacing, used for volumetric scalar fields such as medical images or simulation output. This is the most common input type for isosurface extraction.
- `vtkPolyData`: a collection of points with associated cells (vertices, lines, polygons, triangle strips). This is the standard output format for surface-extracting filters such as Marching Cubes.
- `vtkUnstructuredGrid`: an irregular mesh where cells can be of mixed types, used for unstructured simulation data.

Understanding these data types is essential because filters declare which types they accept as input and produce as output. A filter that expects `vtkImageData` will not work if given `vtkPolyData`. VTK documents these constraints in its class reference.

For the isosurface tasks in particular, a useful mental model is:

- start with `vtkImageData` or some other scalar volume representation
- apply a contouring or isosurface filter
- obtain `vtkPolyData`
- render that result with a polydata mapper

### Looking Inside the Interface

After installation, one of the most useful habits is simply inspecting classes from Python. The VTK wrappers expose the same class and method names you will see in C++ documentation, so the Python shell is a practical way to learn the interface.

```python
import vtk

help(vtk.vtkSphereSource)
```

When you inspect the output, pay attention to the following:

- the superclass, for example `vtkSphereSource` is shown as a `vtkPolyDataAlgorithm`
- the object description, which usually states what kind of data it creates
- setter/getter conventions such as `SetRadius`, `GetRadius`, `SetThetaResolution`, `GetThetaResolution`
- whether the class is a source, filter, mapper, or rendering object

You can also inspect data objects directly:

```python
import vtk

sphere = vtk.vtkSphereSource()
sphere.Update()

output = sphere.GetOutput()
print(type(output))
print(output.GetClassName())
print(output.GetNumberOfPoints())
```

This is often the quickest way to answer practical questions such as:

- What does this class output?
- Is the output `vtkPolyData` or `vtkImageData`?
- Which parameters can I configure?
- What methods are inherited from the superclass?

When you later read VTK examples or write your own filters, this habit saves time.

### Implementing Your Own Filter

All implementation projects in this course ask you to implement algorithms inside VTK filter classes. A filter is a C++ class that inherits from an appropriate base class — typically `vtkPolyDataAlgorithm` for filters that produce surface geometry — and overrides the `RequestData` method where the algorithm runs. The method receives the input dataset and fills the output dataset before returning.

Filters expose their parameters through explicit setter and getter methods following VTK's naming conventions (`SetIsovalue`, `GetIsovalue`). This makes the filter scriptable from Python exactly like any built-in VTK class. Once compiled, your C++ filter is imported from Python like any other module, and used in the same way as the built-in VTK filters shown above.

```python
import vtk
import vtkVISFilters  # your compiled module

reader = vtk.vtkXMLImageDataReader()
reader.SetFileName("data/volume.vti")

my_filter = vtkVISFilters.vtkVISMarchingCubes()
my_filter.SetInputConnection(reader.GetOutputPort())
my_filter.SetIsovalue(128.0)

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(my_filter.GetOutputPort())
# ... rest of the pipeline
```

Your filter behaves identically to a built-in VTK filter from the pipeline's perspective. This is the key design goal: every algorithm you write should be indistinguishable from a native VTK component when used from Python.

#### C++ Example 1: Filter Class Structure

The following shows the minimal structure of a VTK filter in C++. The header declares the class and its parameters; the implementation file overrides `RequestData`, which is where the algorithm runs.

**`vtkVISExampleFilter.h`**
```cpp
#pragma once

#include <vtkPolyDataAlgorithm.h>

class vtkVISExampleFilter : public vtkPolyDataAlgorithm
{
public:
    static vtkVISExampleFilter* New();
    vtkTypeMacro(vtkVISExampleFilter, vtkPolyDataAlgorithm);

    vtkSetMacro(Isovalue, double);
    vtkGetMacro(Isovalue, double);

protected:
    vtkVISExampleFilter();
    ~vtkVISExampleFilter() override = default;

    int RequestData(vtkInformation*, vtkInformationVector**, vtkInformationVector*) override;

    // Declare the expected input type
    int FillInputPortInformation(int port, vtkInformation* info) override;

private:
    double Isovalue = 0.0;
};
```

**`vtkVISExampleFilter.cxx`**
```cpp
#include "vtkVISExampleFilter.h"

#include <vtkImageData.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkObjectFactory.h>
#include <vtkPolyData.h>

vtkStandardNewMacro(vtkVISExampleFilter);

vtkVISExampleFilter::vtkVISExampleFilter()
{
    this->SetNumberOfInputPorts(1);
    this->SetNumberOfOutputPorts(1);
}

int vtkVISExampleFilter::FillInputPortInformation(int, vtkInformation* info)
{
    info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkImageData");
    return 1;
}

int vtkVISExampleFilter::RequestData(
    vtkInformation*,
    vtkInformationVector** inputVector,
    vtkInformationVector* outputVector)
{
    // Retrieve input and output objects from the pipeline
    vtkImageData* input = vtkImageData::GetData(inputVector[0]);
    vtkPolyData* output = vtkPolyData::GetData(outputVector);

    if (!input || !output)
        return 0;

    // --- Algorithm implementation goes here ---

    return 1;
}
```

What to notice:

- `vtkStandardNewMacro` registers the class with VTK's object factory, which is required for Python wrapping and `::New()`.
- `vtkSetMacro` / `vtkGetMacro` generate the setter and getter methods automatically, following VTK naming conventions.
- `FillInputPortInformation` declares that this filter expects `vtkImageData` as input. VTK will enforce this constraint at pipeline execution time.
- `RequestData` is called by the pipeline when downstream objects request data. Input and output are retrieved from the information vectors, not passed as arguments directly.
- The output object (`vtkPolyData`) already exists when `RequestData` is called. The method populates it rather than creating a new one.

#### C++ Example 2: Reading Input Data and Writing Output Geometry

This example shows the next step: accessing scalar values from the input `vtkImageData` and inserting points and cells into the output `vtkPolyData`. This is the standard pattern for any filter that extracts geometry from a scalar field.

```cpp
int vtkVISExampleFilter::RequestData(
    vtkInformation*,
    vtkInformationVector** inputVector,
    vtkInformationVector* outputVector)
{
    vtkImageData* input = vtkImageData::GetData(inputVector[0]);
    vtkPolyData*  output = vtkPolyData::GetData(outputVector);

    if (!input || !output)
        return 0;

    // Query the grid dimensions and spacing
    int dims[3];
    input->GetDimensions(dims);    // number of points along each axis

    double spacing[3];
    input->GetSpacing(spacing);    // physical distance between points

    double origin[3];
    input->GetOrigin(origin);      // world-space coordinates of point (0,0,0)

    // Access the scalar array attached to grid points
    vtkDataArray* scalars = input->GetPointData()->GetScalars();
    if (!scalars)
        return 0;

    // Prepare output geometry containers
    vtkNew<vtkPoints>    points;
    vtkNew<vtkCellArray> triangles;

    // Example: insert a single triangle for illustration
    // In a real filter, you would loop over cells and generate geometry
    vtkIdType id0 = points->InsertNextPoint(0.0, 0.0, 0.0);
    vtkIdType id1 = points->InsertNextPoint(1.0, 0.0, 0.0);
    vtkIdType id2 = points->InsertNextPoint(0.5, 1.0, 0.0);

    vtkIdType tri[3] = {id0, id1, id2};
    triangles->InsertNextCell(3, tri);

    // Attach geometry to the output
    output->SetPoints(points);
    output->SetPolys(triangles);

    return 1;
}
```

What to notice:

- `GetDimensions`, `GetSpacing`, and `GetOrigin` are the standard calls for querying the geometry of a `vtkImageData` grid. You will use these in every scalar-field filter.
- `GetPointData()->GetScalars()` retrieves the primary scalar array. If the dataset has multiple arrays, use `GetArray("name")` instead.
- `vtkNew<T>` is the preferred RAII wrapper for allocating VTK objects in C++. It handles reference counting automatically.
- Points are inserted one at a time with `InsertNextPoint`, returning an integer id. Cells are defined by listing the ids of their vertices.
- The output `vtkPolyData` object is populated in-place. Do not create a new `vtkPolyData` and assign it; write into the object that the pipeline already provides.
- For a real isosurface filter, the triangle-insertion step would be inside a loop over all grid cells, with the isovalue determining which edges are intersected.

### Including Your C++ Filters in CMake and Testing from Python

This repository is already configured to build VTK modules and wrap them for Python. To add a new C++ filter class, you only need to register it in the module CMake file and then add a Python test script under CTest.

#### 1) Register the filter class in `src/CMakeLists.txt`

Add your class name to `CLASSES` and the implementation file to `SOURCES`.

```cmake
vtk_module_add_module(VISFilters
    CLASSES
        vtkHelloElevationFilter
        vtkVISMarchingCubes            # add your new filter class here
    SOURCES
        vtkHelloElevationFilter.cxx
        vtkVISMarchingCubes.cxx        # add your new source file here
)
```

If your filter needs additional VTK components, extend the module link list in the same file:

```cmake
vtk_module_link(VISFilters
    PUBLIC
        VTK::CommonCore
        VTK::CommonDataModel
        VTK::FiltersCore
        VTK::FiltersGeneral
        # VTK::ImagingCore              # example: add only if needed
)
```

#### 2) Keep module metadata in sync

The root build uses `vtk_module_scan(...)` over `src/vtk.module`, then `vtk_module_build(...)` and `vtk_module_wrap_python(...)` in the top-level `CMakeLists.txt`. In practice, this means:

- Keep the module name and dependencies in `src/vtk.module` accurate.
- Ensure your new filter headers/sources are listed in `src/CMakeLists.txt`.
- Reconfigure/rebuild so Python wrappers are regenerated.

After rebuilding, your class is available in Python through the wrapped module (for example, `from vtkVISFilters import *`).

#### 3) Write a Python smoke test script

Create a small script that imports your wrapped class, runs `Update()`, and asserts basic output properties. Example:

```python
from vtkVISFilters import vtkVISMarchingCubes
from vtkmodules.vtkFiltersSources import vtkSphereSource


def main() -> int:
        source = vtkSphereSource()
        source.SetThetaResolution(24)
        source.SetPhiResolution(24)

        filt = vtkVISMarchingCubes()
        filt.SetInputConnection(source.GetOutputPort())
        filt.Update()

        output = filt.GetOutput()
        assert output is not None
        assert output.GetNumberOfPoints() >= 0
        return 0


if __name__ == "__main__":
        raise SystemExit(main())
```

You can place this in `tests/` (for example, `tests/python_smoke_marching_cubes.py`).

#### 4) Register the script as a CTest test

Add an `add_test(...)` entry in `tests/CMakeLists.txt`, and set `PYTHONPATH` so Python can find the generated wrapped module in the build tree:

```cmake
add_test(
    NAME python.marching_cubes_smoke
    COMMAND "${Python_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/python_smoke_marching_cubes.py"
)

set_tests_properties(
    python.marching_cubes_smoke
    PROPERTIES
        ENVIRONMENT "PYTHONPATH=${CMAKE_BINARY_DIR}/python/vtkmodules"
)
```

Run tests with CTest from the build directory:

```bash
ctest --output-on-failure
```

This gives you a fast validation loop: compile C++ filter, load it in Python, run a pipeline update, and catch wrapper/interface regressions early.

### Side-by-Side Comparisons

Several tasks ask you to set up comparison pipelines that show two algorithm results side-by-side. In VTK, this is achieved by using two renderers inside the same render window, each with its own viewport. The viewport defines the portion of the window that the renderer occupies, specified as a normalized rectangle `[xmin, ymin, xmax, ymax]`.

```python
renderer_left = vtk.vtkRenderer()
renderer_left.SetViewport(0.0, 0.0, 0.5, 1.0)

renderer_right = vtk.vtkRenderer()
renderer_right.SetViewport(0.5, 0.0, 1.0, 1.0)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer_left)
window.AddRenderer(renderer_right)
window.SetSize(1400, 700)
```

You can alternatively place two actors in the same renderer and use `actor.SetPosition(...)` to offset them horizontally. Both approaches are valid and the choice depends on how much you want the cameras to be independent.

---

### What You Should Understand Before Moving On

Before starting the topic-specific tasks, you should be comfortable with the following points:

- You can identify the role of a source, filter, mapper, actor, renderer, and render window in a simple script.
- You can read a short VTK pipeline from left to right and explain what data is flowing through it.
- You understand why `GetOutputPort()` and `SetInputConnection(...)` appear everywhere.
- You understand that VTK usually computes results only when data is requested, for example through `Render()` or `Update()`.
- You know the difference between `vtkImageData` and `vtkPolyData` and when each appears in a pipeline.
- You know that later course work will follow the same structure, except that some filters will be your own C++ implementations rather than built-in VTK classes.

If these points feel clear, you are ready to move on to the project tasks.

---

### Summary

VTK's pipeline model separates data production, data transformation, and rendering into distinct composable stages. Sources generate data, filters transform it, and mappers and actors render it. Computation is deferred until explicitly requested, and VTK tracks dependencies so that only outdated parts of the pipeline re-execute when something changes.

In these projects, you will implement algorithms as VTK filters in C++ and drive them from Python pipelines. The emphasis throughout is on fitting your algorithms naturally into this model — exposing clean interfaces, maintaining compatibility between tasks, and using the pipeline infrastructure to set up meaningful comparisons.

---
