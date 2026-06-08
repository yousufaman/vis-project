configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/pipeline_demo.py"
  "${CMAKE_CURRENT_BINARY_DIR}/pipeline_demo.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/cube_view.py"
  "${CMAKE_CURRENT_BINARY_DIR}/cube_view.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/smoke_marching_cubes.py"
  "${CMAKE_CURRENT_BINARY_DIR}/smoke_marching_cubes.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/task1_demo_single.py"
  "${CMAKE_CURRENT_BINARY_DIR}/task1_demo_single.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/task1_demo_comparison.py"
  "${CMAKE_CURRENT_BINARY_DIR}/task1_demo_comparison.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/task2_demo_normals.py"
  "${CMAKE_CURRENT_BINARY_DIR}/task2_demo_normals.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/task3_demo_spanspace.py"
  "${CMAKE_CURRENT_BINARY_DIR}/task3_demo_spanspace.py"
  COPYONLY
)

configure_file(
  "${CMAKE_CURRENT_SOURCE_DIR}/task4_evaluation_sweep.py"
  "${CMAKE_CURRENT_BINARY_DIR}/task4_evaluation_sweep.py"
  COPYONLY
)

install(
  FILES
    "${CMAKE_CURRENT_SOURCE_DIR}/pipeline_demo.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/cube_view.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/smoke_marching_cubes.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/task1_demo_single.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/task1_demo_comparison.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/task2_demo_normals.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/task3_demo_spanspace.py"
    "${CMAKE_CURRENT_SOURCE_DIR}/task4_evaluation_sweep.py"
  DESTINATION "${CMAKE_INSTALL_DATADIR}/VISVTKFilters/python"
)
