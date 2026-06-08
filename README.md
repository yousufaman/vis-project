# Scivis Project Scaffold

This repository supports the design of self-guided implementation projects for the Visualization & HCI course.

The long-term goal is to explore modern visualization techniques through a workflow built around `VTK`, `C++`, and `Python`. 

As part of the project students implement filters and core algorithms in C++, expose them through VTK's wrapping system, and assemble demonstration or comparison pipelines in Python.

At the moment, the repository contains a minimal working scaffold for that stack: an example external VTK module, a wrapped Python entry point, and a test that verifies the Python pipeline can import and run the generated module.

The project tasks are described here:

- [Introduction](docs/task-intro.md)
- [Task 1](docs/task1.md)
- [Task 2](docs/task2.md)
- ...


## Repository Organization

The importants aspects of the repository reside in 

- `src/`: C++ source for the VTK module. This contains the filter implementation, module metadata, and build rules.
- `src/vtkHelloElevationFilter.{h,cxx}`: sample custom VTK filter (in C++) used to prove out the wrapping pipeline.

- `python/`: Python-side demo code and scripts.

- `python/pipeline_demo.py`: sample pipeline that imports the wrapped module and runs the example filter.

- `tests/`: CTest-based integration test that runs the Python demo against the build-tree wrapper output.

## Build Overview

The project expects:

- CMake 3.25 or newer
- a C++20 compiler
- Python with development headers for extension-module builds
- a VTK installation with Python wrapping support available to CMake

If VTK is not installed in a standard location, point CMake at it with `VTK_DIR` or `CMAKE_PREFIX_PATH`.

## Installing Prerequisites

### macOS

Install Apple's developer tools first. Installing the full Xcode app is fine; if you only need the toolchain, install the Command Line Tools:

```bash
xcode-select --install
```

If you have multiple Xcode installations, make sure the active developer directory is set correctly:

```bash
sudo xcode-select --switch /Applications/Xcode.app
```

Then install the project dependencies with Homebrew:

```bash
brew install cmake ninja python@3.14 vtk
```

If CMake does not find VTK automatically, configure with:

```bash
cmake -S . -B build -DCMAKE_PREFIX_PATH="$(brew --prefix vtk)"
```

If you prefer to point CMake at the package directly, use the installed VTK CMake directory, for example:

```bash
cmake -S . -B build -DVTK_DIR="$(brew --prefix vtk)/lib/cmake/vtk-9.5"
```

### Linux

On Debian or Ubuntu, install a C++ toolchain, CMake, Python development headers, and the VTK development package:

```bash
sudo apt update
sudo apt install build-essential cmake ninja-build python3 python3-dev libvtk9-dev
```

If your distribution installs VTK in a non-default CMake location, point CMake at it explicitly:

```bash
cmake -S . -B build -DVTK_DIR=/usr/lib/x86_64-linux-gnu/cmake/vtk-9.1
```

Package names and VTK install paths vary by distribution, so on non-Debian systems you may need the equivalent development packages for Python and VTK.

## Build Instructions

Configure:

```bash
cmake -S . -B build
```

Build:

```bash
cmake --build build
```

Run the test suite:

```bash
ctest --test-dir build --output-on-failure
```

Run the demo script directly:

```bash
PYTHONPATH="$PWD/build/python/vtkmodules" python build/python/pipeline_demo.py
```

## Intended Direction

As the repository grows, it is intended to hold one Markdown brief per visualization topic. Those topic files should describe short, implementation-focused projects that ask students to build a baseline technique, extend it with meaningful augmentations, and compare or evaluate research-inspired variants within the VTK/C++ plus Python pipeline workflow described above.
