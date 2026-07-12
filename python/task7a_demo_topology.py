import os
if os.name == 'nt' and hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(r"C:\VTK-build\bin")
    os.add_dll_directory(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "build", "bin")))

import vtk
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkCommonDataModel import vtkQuadric
from vtkmodules.vtkFiltersCore import vtkContourFilter, vtkPolyDataNormals
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor
from vtkVISFilters import vtkVISMarchingCubes
import math

def create_saddle():
    quadric = vtkQuadric()
    quadric.SetCoefficients(1, 1, -1, 0, 0, 0, 0, 0, 0, 0) # x^2 + y^2 - z^2
    
    sample = vtkSampleFunction()
    sample.SetSampleDimensions(15, 15, 15)
    sample.SetImplicitFunction(quadric)
    sample.SetModelBounds(-1, 1, -1, 1, -1, 1)
    sample.Update()
    return sample.GetOutput()

def get_actor(polydata, color, offset=0.0):
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)
    actor.SetPosition(offset, 0, 0)
    
    edges = vtkActor()
    edges.SetMapper(mapper)
    edges.GetProperty().SetRepresentationToWireframe()
    edges.GetProperty().SetColor(0,0,0)
    edges.GetProperty().SetLineWidth(1.5)
    edges.SetPosition(offset, 0, 0)
    
    return [actor, edges]

def main():
    img = create_saddle()
    colors = vtkNamedColors()
    
    # 1. Classical MC (Ours)
    mc1 = vtkVISMarchingCubes()
    mc1.SetInputData(img)
    mc1.SetIsovalue(0.1)
    mc1.Update()
    
    # 2. Topologically Correct (Ours) - enabled topological checks
    mc2 = vtkVISMarchingCubes()
    mc2.SetInputData(img)
    mc2.SetIsovalue(0.1)
    mc2.SetComputeTopologicallyCorrect(True)
    mc2.Update()
    
    # 3. VTK Reference
    vtk_mc = vtkContourFilter()
    vtk_mc.SetInputData(img)
    vtk_mc.SetValue(0, 0.1)
    vtk_mc.Update()
    
    ren = vtkRenderer()
    
    for a in get_actor(mc1.GetOutput(), colors.GetColor3d("Tomato"), -2.5):
        ren.AddActor(a)
    for a in get_actor(mc2.GetOutput(), colors.GetColor3d("SeaGreen"), 0.0):
        ren.AddActor(a)
    for a in get_actor(vtk_mc.GetOutput(), colors.GetColor3d("CornflowerBlue"), 2.5):
        ren.AddActor(a)
        
    ren.SetBackground(colors.GetColor3d("WhiteSmoke"))
    ren.ResetCamera()
    
    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(1200, 400)
    renWin.SetWindowName("Task 7a: Topological Ambiguity (Classical | MC33 | VTK)")
    
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    # Save screenshot
    renWin.Render()
    import vtkmodules.vtkIOImage as io
    from vtkmodules.vtkRenderingCore import vtkWindowToImageFilter
    w2if = vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()
    writer = io.vtkPNGWriter()
    writer.SetFileName("task7a_plot.png")
    writer.SetInputConnection(w2if.GetOutputPort())
    writer.Write()
    
    print("Saved task7a_plot.png")
    
    iren.Start()

if __name__ == '__main__':
    main()
