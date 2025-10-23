cmake_minimum_required(VERSION 3.8)
project(unitree_h1_2_description)

# Required dependencies
find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

# Install Python script
install(PROGRAMS
  scripts/lowstate_to_jointstate_full.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME lowstate_to_jointstate_full
)

# Install mesh files
install(DIRECTORY meshes/
  DESTINATION share/${PROJECT_NAME}/meshes
)

# Install URDF and XML files
install(DIRECTORY urdf/
  DESTINATION share/${PROJECT_NAME}/urdf
)

# Install launch files
install(DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch
)

# Package declaration
ament_package()

