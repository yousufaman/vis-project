#ifndef vtkHelloElevationFilter_h
#define vtkHelloElevationFilter_h

#include "vtkVISFiltersModule.h"
#include <vtkPolyDataAlgorithm.h>

/**
 * @brief Simple elevation-based coloring filter (professor's example).
 *
 * Copies the Z-coordinate of each point into a scalar array named "Elevation",
 * demonstrating the basic VTK filter pipeline pattern.
 */
class VTKVISFILTERS_EXPORT vtkHelloElevationFilter : public vtkPolyDataAlgorithm
{
public:
  static vtkHelloElevationFilter* New();
  vtkTypeMacro(vtkHelloElevationFilter, vtkPolyDataAlgorithm);
  void PrintSelf(ostream& os, vtkIndent indent) override;

protected:
  vtkHelloElevationFilter() = default;
  ~vtkHelloElevationFilter() override = default;

  int RequestData(
    vtkInformation* request,
    vtkInformationVector** inputVector,
    vtkInformationVector* outputVector) override;

private:
  vtkHelloElevationFilter(const vtkHelloElevationFilter&) = delete;
  void operator=(const vtkHelloElevationFilter&) = delete;
};

#endif
