#include "vtkHelloElevationFilter.h"

#include <vtkFloatArray.h>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkObjectFactory.h>
#include <vtkPointData.h>
#include <vtkPoints.h>
#include <vtkPolyData.h>

vtkStandardNewMacro(vtkHelloElevationFilter);

void vtkHelloElevationFilter::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
}

int vtkHelloElevationFilter::RequestData(
  vtkInformation*,
  vtkInformationVector** inputVector,
  vtkInformationVector* outputVector)
{
  auto* input  = vtkPolyData::GetData(inputVector[0], 0);
  auto* output = vtkPolyData::GetData(outputVector, 0);

  if (!input || !output)
    return 0;

  // Pass geometry through
  output->ShallowCopy(input);

  vtkPoints* pts = input->GetPoints();
  if (!pts)
    return 1;

  vtkIdType npts = pts->GetNumberOfPoints();

  auto elevation = vtkSmartPointer<vtkFloatArray>::New();
  elevation->SetName("Elevation");
  elevation->SetNumberOfTuples(npts);

  for (vtkIdType i = 0; i < npts; ++i)
  {
    double p[3];
    pts->GetPoint(i, p);
    elevation->SetValue(i, static_cast<float>(p[2]));
  }

  output->GetPointData()->AddArray(elevation);
  output->GetPointData()->SetActiveScalars("Elevation");
  return 1;
}
