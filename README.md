# Unitree H1-2 Camera ROS 2 Node

### Overview
This package provides a ROS 2 Python node that streams live camera frames from the Unitree H1-2 robot using the official Unitree SDK (`unitree_sdk2py`). It wraps the SDK's `VideoClient` interface and publishes frames to `/unitree_h1/image_raw` as `sensor_msgs/Image`.

The node is designed for integration with ROS 2 perception, SLAM, and visualization pipelines.

### Features
- Uses Unitree SDK (`unitree_sdk2py`) for direct camera access
- Publishes frames to `/unitree_h1/image_raw` at ~20 FPS
- Compatible with `rqt_image_view`, `rosbag`, and image processing nodes
- Handles SDK initialization and CLI argument parsing robustly
- Includes exception handling for stable runtime

### Environment Setup
Before running the node, make sure to source the following in your terminal:

```bash
# Source Cyclone DDS configuration (if using a custom config)
export CYCLONEDDS_URI=file:///home/toor/cyclonedds_config.xml

# Source your ROS 2 distribution
source /opt/ros/foxy/setup.bash

# Source your workspace
source ~/h12_ws/install/setup.bash

## Package Structure
├── h1_2_camera_py
│   ├── h1_camera_node.py
│   ├── __init__.py
│   └── __pycache__
│       ├── h1_camera_node.cpython-38.pyc
│       └── __init__.cpython-38.pyc
├── package.xml
├── resource
│   └── h1_2_camera_py
├── setup.cfg
├── setup.py
└── test
    ├── test_copyright.py
    ├── test_flake8.py
    └── test_pep257.py

## Installation
cd ~/h12_ws/src
git clone [<your-repo-url>](https://github.com/Raviteja-T/h1_2/tree/develope_camera)
cd ~/h12_ws
colcon build --packages-select h1_2_camera_py
source install/setup.bash

## Usage
ros2 run h1_2_camera_py h1_camera_node

## Topic
- `/unitree_h1/image_raw` (`sensor_msgs/Image`): Published camera frames

## Debugging
To run with debug logs:

```bash
ros2 run h1_2_camera_py h1_camera_node --ros-args --log-level DEBUG

## Compatibilty
Tested on ROS 2 Foxy. Should be adaptable to other ROS 2 distros with Python 3.8+.

## Author
**Tirumalapudi Raviteja**  
- Email: t.raviteja@gmail.com