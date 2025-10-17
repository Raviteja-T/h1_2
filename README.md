# ROS2 Workspace: Livox MID360 & Realsense Segmentation

This repository contains ROS2 packages for working with:

1. **Livox MID360 LiDAR** - ROS2 driver and point cloud visualization.
2. **Realsense Camera** - Object detection and segmentation using Intel Realsense.

---

## Workspace Structure

```
ros2_ws/
├─ src/
│  ├─ livox_ros_driver2/        # Livox MID360 ROS2 driver
│  ├─ realsense_segmentation/   # Realsense detection and segmentation
│  └─ other_packages/           # Any other packages
├─ build/
├─ install/
└─ log/
```

---

## Prerequisites

* Ubuntu 22.04
* ROS2 Humble
* Intel Realsense SDK2
* Livox SDK2
* Python 3.10+
* CMake 3.10+
* Dependencies installed for both packages (refer to each package `README` if needed)

---

## Installation

Clone this workspace:

```bash
git clone <your-repo-url> ros2_ws
cd ros2_ws
vcs import src < ros2.repos   # optional if using vcs
colcon build
source install/setup.bash
```

---

## Usage

### 1. Livox MID360 LiDAR

Launch the driver and visualize in RViz:

```bash
ros2 launch livox_ros_driver2 msg_MID360_launch.py
```

Make sure your LiDAR is connected and network configured correctly.

### 2. Realsense Detection & Segmentation

Launch the detection node:

```bash
ros2 launch realsense_segmentation realsense_detection.launch.py
```

This will start camera streaming and detection/segmentation pipelines.

---

## Notes

* Keep your `wlp0s20f3` (or network interface) IP properly configured for LiDAR communication.
* Avoid pushing `build/`, `install/`, and `log/` directories to GitHub. Use `.gitignore`.

---

## Branch Naming Suggestion

* `main` or `master`: stable code
* `develop`: development branch
* Feature branches: `feature/livox-integration`, `feature/realsense-segmentation`

---

## Author

**Raviteja Tirumalapudi**
Email: [t.raviteja@gmail.com](mailto:t.raviteja@gmail.com)
