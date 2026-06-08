#ifndef vtkVISMarchingCubes_h
#define vtkVISMarchingCubes_h

#include "vtkVISFiltersModule.h"

#include <vtkPolyDataAlgorithm.h>
#include <vector>

// Marching Cubes filter for extracting isosurfaces from vtkImageData.
// Based on Lorensen & Cline (1987). Supports optional gradient normals,
// point merging, and span space acceleration.
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
