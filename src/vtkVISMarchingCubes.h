#ifndef vtkVISMarchingCubes_h
#define vtkVISMarchingCubes_h

#include "vtkVISFiltersModule.h"

#include <vtkPolyDataAlgorithm.h>
#include <vector>

/**
 * @brief Marching Cubes isosurface filter (VIS course implementation).
 *
 * Extracts a single isosurface from a 3D scalar field (vtkImageData) at a
 * user-specified isovalue and outputs a vtkPolyData triangle mesh.
 *
 * Algorithm: Lorensen & Cline, SIGGRAPH 1987.
 *   - Each voxel cell is classified by an 8-bit vertex mask (inside/outside).
 *   - A 256-entry edge table identifies which of the 12 edges are cut.
 *   - Edge intersection positions are computed by linear interpolation.
 *   - A triangle table maps each configuration to a triangle list.
 *   - Per-vertex normals are estimated from the central-difference gradient.
 *
 * Usage (Python):
 * @code
 *   from vtkVISFilters import vtkVISMarchingCubes
 *   mc = vtkVISMarchingCubes()
 *   mc.SetInputConnection(reader.GetOutputPort())
 *   mc.SetIsovalue(128.0)
 *   mc.Update()
 *   polydata = mc.GetOutput()
 * @endcode
 */
class VTKVISFILTERS_EXPORT vtkVISMarchingCubes : public vtkPolyDataAlgorithm
{
public:
  static vtkVISMarchingCubes* New();
  vtkTypeMacro(vtkVISMarchingCubes, vtkPolyDataAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent) override;

  ///@{ Scalar value at which the isosurface is extracted.
  vtkSetMacro(Isovalue, double);
  vtkGetMacro(Isovalue, double);
  ///@}

  ///@{ Flag to compute gradient-based normals.
  vtkSetMacro(ComputeNormals, bool);
  vtkGetMacro(ComputeNormals, bool);
  vtkBooleanMacro(ComputeNormals, bool);
  ///@}

  ///@{ Flag to merge coincident points.
  vtkSetMacro(MergePoints, bool);
  vtkGetMacro(MergePoints, bool);
  vtkBooleanMacro(MergePoints, bool);
  ///@}

  ///@{ Flag to accelerate using span space.
  vtkSetMacro(UseSpanSpace, bool);
  vtkGetMacro(UseSpanSpace, bool);
  vtkBooleanMacro(UseSpanSpace, bool);
  ///@}

protected:
  vtkVISMarchingCubes();
  ~vtkVISMarchingCubes() override = default;

  int FillInputPortInformation(int port, vtkInformation* info) override;

  int RequestData(
    vtkInformation* request,
    vtkInformationVector** inputVector,
    vtkInformationVector* outputVector) override;

private:
  vtkVISMarchingCubes(const vtkVISMarchingCubes&) = delete;
  void operator=(const vtkVISMarchingCubes&) = delete;

  double Isovalue = 0.0;
  bool ComputeNormals = true;
  bool MergePoints = true;
  bool UseSpanSpace = false;

  struct CellSpan {
    double min_val;
    double max_val;
    int i, j, k;
  };
  std::vector<CellSpan> SpanSpace;
  vtkMTimeType SpanSpaceTime = 0;
};

#endif
