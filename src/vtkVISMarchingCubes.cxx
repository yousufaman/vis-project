#include "vtkVISMarchingCubes.h"
#include "mc_tables.h"
#include "mc33_tables.h"

#include <vtkSMPTools.h>
#include <vtkSMPThreadLocalObject.h>
#include <vtkAppendPolyData.h>
#include <vtkCleanPolyData.h>
#include <vtkMergePoints.h>


#include <vtkCellArray.h>
#include <vtkDataArray.h>
#include <vtkFloatArray.h>
#include <vtkImageData.h>
#include <algorithm>
#include <limits>
#include <vtkInformation.h>
#include <vtkInformationVector.h>
#include <vtkObjectFactory.h>
#include <vtkPointData.h>
#include <vtkPoints.h>
#include <vtkPolyData.h>
#include <vtkSmartPointer.h>

vtkStandardNewMacro(vtkVISMarchingCubes);

vtkVISMarchingCubes::vtkVISMarchingCubes()
{
  this->SetNumberOfInputPorts(1);
  this->SetNumberOfOutputPorts(1);
}

void vtkVISMarchingCubes::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os, indent);
  os << indent << "Isovalue: " << this->Isovalue << "\n";
  os << indent << "ComputeNormals: " << (this->ComputeNormals ? "On" : "Off") << "\n";
  os << indent << "MergePoints: " << (this->MergePoints ? "On" : "Off") << "\n";
  os << indent << "UseSpanSpace: " << (this->UseSpanSpace ? "On" : "Off") << "\n";
  os << indent << "ComputeTopologicallyCorrect: " << (this->ComputeTopologicallyCorrect ? "On" : "Off") << "\n";
  os << indent << "UseParallel: " << (this->UseParallel ? "On" : "Off") << "\n";
}

int vtkVISMarchingCubes::FillInputPortInformation(int, vtkInformation* info)
{
  info->Set(vtkAlgorithm::INPUT_REQUIRED_DATA_TYPE(), "vtkImageData");
  return 1;
}

// lerp the intersection point along an edge
static void interpolate(
  const double v0[3], const double v1[3],
  double s0, double s1, double iso, double out[3])
{
  double denom = s1 - s0;
  double t = (std::abs(denom) < 1e-10) ? 0.5 : (iso - s0) / denom;
  out[0] = v0[0] + t * (v1[0] - v0[0]);
  out[1] = v0[1] + t * (v1[1] - v0[1]);
  out[2] = v0[2] + t * (v1[2] - v0[2]);
}

// central-difference gradient for normal estimation
static void gradient(vtkDataArray* sc, const int dims[3],
  const double sp[3], int i, int j, int k, double g[3])
{
  auto idx = [&](int x, int y, int z) {
    return static_cast<vtkIdType>(x + dims[0] * (y + dims[1] * z));
  };
  int ix0 = std::max(i - 1, 0),      ix1 = std::min(i + 1, dims[0] - 1);
  int iy0 = std::max(j - 1, 0),      iy1 = std::min(j + 1, dims[1] - 1);
  int iz0 = std::max(k - 1, 0),      iz1 = std::min(k + 1, dims[2] - 1);
  g[0] = (sc->GetTuple1(idx(ix1,j,k)) - sc->GetTuple1(idx(ix0,j,k)))
         / ((ix1 - ix0) * sp[0] + 1e-30);
  g[1] = (sc->GetTuple1(idx(i,iy1,k)) - sc->GetTuple1(idx(i,iy0,k)))
         / ((iy1 - iy0) * sp[1] + 1e-30);
  g[2] = (sc->GetTuple1(idx(i,j,iz1)) - sc->GetTuple1(idx(i,j,iz0)))
         / ((iz1 - iz0) * sp[2] + 1e-30);
}


struct ParallelMCWorker {
  vtkImageData* Input;
  vtkPolyData* Output;
  double Isovalue;
  bool ComputeNormals;
  int dims[3];
  double origin[3];
  double spacing[3];
  vtkDataArray* scalars;

  struct ThreadLocalData {
    vtkSmartPointer<vtkPoints> Points;
    vtkSmartPointer<vtkCellArray> Polys;
    vtkSmartPointer<vtkFloatArray> Normals;
  };
  vtkSMPThreadLocal<ThreadLocalData> TLData;

  void Initialize() {
    auto& data = this->TLData.Local();
    data.Points = vtkSmartPointer<vtkPoints>::New();
    data.Polys = vtkSmartPointer<vtkCellArray>::New();
    data.Normals = vtkSmartPointer<vtkFloatArray>::New();
    data.Normals->SetName("Normals");
    data.Normals->SetNumberOfComponents(3);
  }

  void operator()(vtkIdType begin, vtkIdType end) {
    auto& data = this->TLData.Local();
    static const int vOff[8][3] = {
      {0,0,0},{1,0,0},{1,1,0},{0,1,0},
      {0,0,1},{1,0,1},{1,1,1},{0,1,1}
    };
    static const int edgeVerts[12][2] = {
      {0,1},{1,2},{2,3},{3,0},
      {4,5},{5,6},{6,7},{7,4},
      {0,4},{1,5},{2,6},{3,7}
    };

    for (vtkIdType cellIdx = begin; cellIdx < end; ++cellIdx) {
      int i = cellIdx % (dims[0] - 1);
      int j = (cellIdx / (dims[0] - 1)) % (dims[1] - 1);
      int k = cellIdx / ((dims[0] - 1) * (dims[1] - 1));

      double s[8];
      double p[8][3];
      double g[8][3];
      int cubeIndex = 0;
      for (int v = 0; v < 8; ++v) {
        int ci = i + vOff[v][0];
        int cj = j + vOff[v][1];
        int ck = k + vOff[v][2];
        p[v][0] = origin[0] + ci * spacing[0];
        p[v][1] = origin[1] + cj * spacing[1];
        p[v][2] = origin[2] + ck * spacing[2];
        vtkIdType ptId = ci + dims[0] * (cj + dims[1] * ck);
        s[v] = scalars->GetTuple1(ptId);
        if (s[v] >= Isovalue) cubeIndex |= (1 << v);
        if (ComputeNormals) gradient(scalars, dims, spacing, ci, cj, ck, g[v]);
      }

      if (edgeTable[cubeIndex] == 0) continue;

      double ep[12][3];
      double en[12][3];
      for (int e = 0; e < 12; ++e) {
        if (!(edgeTable[cubeIndex] & (1 << e))) continue;
        int a = edgeVerts[e][0], b = edgeVerts[e][1];
        interpolate(p[a], p[b], s[a], s[b], Isovalue, ep[e]);
        if (ComputeNormals) {
          double denom = s[b] - s[a];
          double t = (std::abs(denom) < 1e-10) ? 0.5 : (Isovalue - s[a]) / denom;
          for (int d = 0; d < 3; ++d) en[e][d] = g[a][d] + t * (g[b][d] - g[a][d]);
        }
      }

      for (int t = 0; triTable[cubeIndex][t] != -1; t += 3) {
        vtkIdType tri[3];
        for (int v = 0; v < 3; ++v) {
          int e = triTable[cubeIndex][t + v];
          tri[v] = data.Points->InsertNextPoint(ep[e]);
          if (ComputeNormals) {
            double nx = en[e][0], ny = en[e][1], nz = en[e][2];
            double len = std::sqrt(nx*nx + ny*ny + nz*nz);
            if (len > 1e-10) { nx /= len; ny /= len; nz /= len; }
            data.Normals->InsertNextTuple3(nx, ny, nz);
          }
        }
        data.Polys->InsertNextCell(3, tri);
      }
    }
  }

  void Reduce() {
    vtkNew<vtkAppendPolyData> append;
    for (auto it = this->TLData.begin(); it != this->TLData.end(); ++it) {
      if (it->Points->GetNumberOfPoints() > 0) {
        vtkNew<vtkPolyData> pd;
        pd->SetPoints(it->Points);
        pd->SetPolys(it->Polys);
        if (ComputeNormals) pd->GetPointData()->SetNormals(it->Normals);
        append->AddInputData(pd);
      }
    }
    append->Update();
    
    // Use vtkCleanPolyData to emulate MergePoints
    vtkNew<vtkCleanPolyData> cleaner;
    cleaner->SetInputData(append->GetOutput());
    cleaner->Update();
    
    this->Output->ShallowCopy(cleaner->GetOutput());
  }
};

int vtkVISMarchingCubes::RequestData(
  vtkInformation*,
  vtkInformationVector** inputVector,
  vtkInformationVector* outputVector)
{
  auto* input  = vtkImageData::GetData(inputVector[0], 0);
  auto* output = vtkPolyData::GetData(outputVector, 0);

  if (!input || !output)
  {
    vtkErrorMacro("Expected valid vtkImageData input and vtkPolyData output.");
    return 0;
  }

  vtkDataArray* scalars = input->GetPointData()->GetScalars();
  if (!scalars)
  {
    vtkErrorMacro("Input vtkImageData has no point scalars.");
    return 0;
  }

  int dims[3];
  double origin[3], spacing[3];
  input->GetDimensions(dims);
  input->GetOrigin(origin);
  input->GetSpacing(spacing);

  // vertex offsets for the 8 corners of a cube
  static const int vOff[8][3] = {
    {0,0,0},{1,0,0},{1,1,0},{0,1,0},
    {0,0,1},{1,0,1},{1,1,1},{0,1,1}
  };
  // edge-to-vertex mapping
  static const int edgeVerts[12][2] = {
    {0,1},{1,2},{2,3},{3,0},
    {4,5},{5,6},{6,7},{7,4},
    {0,4},{1,5},{2,6},{3,7}
  };

  auto points    = vtkSmartPointer<vtkPoints>::New();
  auto polys     = vtkSmartPointer<vtkCellArray>::New();
  
  vtkSmartPointer<vtkFloatArray> normals;
  if (this->ComputeNormals)
  {
    normals = vtkSmartPointer<vtkFloatArray>::New();
    normals->SetName("Normals");
    normals->SetNumberOfComponents(3);
  }

  vtkSmartPointer<vtkMergePoints> locator;
  if (this->MergePoints)
  {
    locator = vtkSmartPointer<vtkMergePoints>::New();
    locator->InitPointInsertion(points, input->GetBounds());
  }

  const double iso = this->Isovalue;

  if (this->UseParallel && !this->UseSpanSpace && !this->ComputeTopologicallyCorrect)
  {
    ParallelMCWorker worker;
    worker.Input = input;
    worker.Output = output;
    worker.Isovalue = iso;
    worker.ComputeNormals = this->ComputeNormals;
    worker.dims[0] = dims[0]; worker.dims[1] = dims[1]; worker.dims[2] = dims[2];
    worker.origin[0] = origin[0]; worker.origin[1] = origin[1]; worker.origin[2] = origin[2];
    worker.spacing[0] = spacing[0]; worker.spacing[1] = spacing[1]; worker.spacing[2] = spacing[2];
    worker.scalars = scalars;
    
    vtkIdType numCells = static_cast<vtkIdType>(dims[0] - 1) * (dims[1] - 1) * (dims[2] - 1);
    vtkSMPTools::For(0, numCells, worker);
    return 1;
  }

  auto processCell = [&](int i, int j, int k) {
    // gather corner scalars + positions
    double s[8];
    double p[8][3];
    double g[8][3];
    int cubeIndex = 0;
    for (int v = 0; v < 8; ++v)
    {
      int ci = i + vOff[v][0];
      int cj = j + vOff[v][1];
      int ck = k + vOff[v][2];
      p[v][0] = origin[0] + ci * spacing[0];
      p[v][1] = origin[1] + cj * spacing[1];
      p[v][2] = origin[2] + ck * spacing[2];
      vtkIdType ptId = ci + dims[0] * (cj + dims[1] * ck);
      s[v] = scalars->GetTuple1(ptId);
      if (s[v] >= iso) cubeIndex |= (1 << v);
      gradient(scalars, dims, spacing, ci, cj, ck, g[v]);
    }

    if (edgeTable[cubeIndex] == 0) return; // no intersection

    // find intersection points on cut edges
    double ep[12][3];
    double en[12][3];
    for (int e = 0; e < 12; ++e)
    {
      if (!(edgeTable[cubeIndex] & (1 << e))) continue;
      int a = edgeVerts[e][0], b = edgeVerts[e][1];
      interpolate(p[a], p[b], s[a], s[b], iso, ep[e]);
      double denom = s[b] - s[a];
      double t = (std::abs(denom) < 1e-10) ? 0.5 : (iso - s[a]) / denom;
      for (int d = 0; d < 3; ++d)
        en[e][d] = g[a][d] + t * (g[b][d] - g[a][d]);
    }

    // emit triangles
    for (int t = 0; triTable[cubeIndex][t] != -1; t += 3)
    {
      vtkIdType tri[3];
      for (int v = 0; v < 3; ++v)
      {
        int e = triTable[cubeIndex][t + v];
        
        if (this->MergePoints)
        {
          if (locator->InsertUniquePoint(ep[e], tri[v]))
          {
            if (this->ComputeNormals)
            {
              double nx = en[e][0], ny = en[e][1], nz = en[e][2];
              double len = std::sqrt(nx*nx + ny*ny + nz*nz);
              if (len > 1e-10) { nx /= len; ny /= len; nz /= len; }
              normals->InsertNextTuple3(nx, ny, nz);
            }
          }
        }
        else
        {
          tri[v] = points->InsertNextPoint(ep[e]);
          if (this->ComputeNormals)
          {
            double nx = en[e][0], ny = en[e][1], nz = en[e][2];
            double len = std::sqrt(nx*nx + ny*ny + nz*nz);
            if (len > 1e-10) { nx /= len; ny /= len; nz /= len; }
            normals->InsertNextTuple3(nx, ny, nz);
          }
        }
      }
      polys->InsertNextCell(3, tri);
    }
  };

  if (this->UseParallel && !this->UseSpanSpace && !this->ComputeTopologicallyCorrect)
  {
    ParallelMCWorker worker;
    worker.Input = input;
    worker.Output = output;
    worker.Isovalue = this->Isovalue;
    worker.ComputeNormals = this->ComputeNormals;
    worker.dims[0] = dims[0]; worker.dims[1] = dims[1]; worker.dims[2] = dims[2];
    worker.origin[0] = origin[0]; worker.origin[1] = origin[1]; worker.origin[2] = origin[2];
    worker.spacing[0] = spacing[0]; worker.spacing[1] = spacing[1]; worker.spacing[2] = spacing[2];
    worker.scalars = scalars;
    
    vtkIdType numCells = static_cast<vtkIdType>(dims[0] - 1) * (dims[1] - 1) * (dims[2] - 1);
    vtkSMPTools::For(0, numCells, worker);
    return 1;
  }

  if (this->UseSpanSpace)
  {
    if (this->SpanSpaceTime < input->GetMTime())
    {
      this->SpanSpace.clear();
      for (int k = 0; k < dims[2] - 1; ++k)
      for (int j = 0; j < dims[1] - 1; ++j)
      for (int i = 0; i < dims[0] - 1; ++i)
      {
        double min_s = std::numeric_limits<double>::max();
        double max_s = std::numeric_limits<double>::lowest();
        for (int v = 0; v < 8; ++v)
        {
          int ci = i + vOff[v][0];
          int cj = j + vOff[v][1];
          int ck = k + vOff[v][2];
          vtkIdType ptId = ci + dims[0] * (cj + dims[1] * ck);
          double val = scalars->GetTuple1(ptId);
          if (val < min_s) min_s = val;
          if (val > max_s) max_s = val;
        }
        this->SpanSpace.push_back({min_s, max_s, i, j, k});
      }
      std::sort(this->SpanSpace.begin(), this->SpanSpace.end(), [](const CellSpan& a, const CellSpan& b) {
        return a.min_val < b.min_val;
      });
      this->SpanSpaceTime = input->GetMTime();
    }

    auto upper = std::upper_bound(this->SpanSpace.begin(), this->SpanSpace.end(), iso, [](double val, const CellSpan& c) {
      return val < c.min_val;
    });

    for (auto it = this->SpanSpace.begin(); it != upper; ++it)
    {
      if (iso <= it->max_val)
      {
        processCell(it->i, it->j, it->k);
      }
    }
  }
  else
  {
    for (int k = 0; k < dims[2] - 1; ++k)
    for (int j = 0; j < dims[1] - 1; ++j)
    for (int i = 0; i < dims[0] - 1; ++i)
    {
      processCell(i, j, k);
    }
  }

  output->SetPoints(points);
  output->SetPolys(polys);
  if (this->ComputeNormals)
  {
    output->GetPointData()->SetNormals(normals);
  }
  return 1;
}
