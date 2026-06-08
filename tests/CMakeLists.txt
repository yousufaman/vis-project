add_test(
  NAME python.pipeline_demo
  COMMAND "${Python_EXECUTABLE}" "${CMAKE_BINARY_DIR}/python/pipeline_demo.py"
)

set_tests_properties(
  python.pipeline_demo
  PROPERTIES
    ENVIRONMENT "PYTHONPATH=${CMAKE_BINARY_DIR}/python/vtkmodules"
)

add_test(
  NAME python.marching_cubes_smoke
  COMMAND "${Python_EXECUTABLE}" "${CMAKE_BINARY_DIR}/python/smoke_marching_cubes.py"
)

set_tests_properties(
  python.marching_cubes_smoke
  PROPERTIES
    ENVIRONMENT "PYTHONPATH=${CMAKE_BINARY_DIR}/python/vtkmodules"
)
