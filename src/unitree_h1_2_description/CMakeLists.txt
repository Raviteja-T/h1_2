cmake_minimum_required(VERSION 3.8)
project(unitree_h1_2_description)

find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

# Install meshes and URDF files
install(
  DIRECTORY meshes/
  DESTINATION share/${PROJECT_NAME}/meshes
)

install(
  FILES
    h1_2.urdf
    h1_2.xml
    h1_2_handless.urdf
    h1_2_handless.xml
  DESTINATION share/${PROJECT_NAME}
)

# Install launch files
install(
  DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
