# Unitree H1-2 Description Package

This ROS 2 package contains the **URDF model**, meshes, and launch files for the **Unitree H1-2 humanoid robot**. It allows visualization of the robot in **RViz** and supports joint state publishing.

---

## Package Structure

```
unitree_h1_2_description/
├── CMakeLists.txt
├── package.xml
├── launch/
│   └── display.launch.py
├── meshes/
│   ├── pelvis.STL
│   ├── torso_link.STL
│   └── ... (other robot part meshes)
├── include/unitree_h1_2_description/
├── src/
├── h1_2.urdf
├── h1_2_handless.urdf
├── README.md
└── h1_2.png
```

- **URDF files:** `h1_2.urdf` contains the full humanoid robot model.  
- **Meshes:** STL files for each robot link used for visualization and collision.  
- **Launch:** `display.launch.py` to load the URDF in RViz with `robot_state_publisher` and `joint_state_publisher_gui`.

---

## Features

- Full **URDF model** of Unitree H1-2 humanoid robot.  
- All links and joints correctly defined for RViz visualization.  
- Supports **joint_state_publisher GUI** for interactive joint control.  
- Handles **floating base** configuration.  

---

## Dependencies

- ROS 2 Humble  
- `robot_state_publisher`  
- `joint_state_publisher_gui`  
- `rviz2`

Install dependencies:

```bash
sudo apt update
sudo apt install ros-humble-robot-state-publisher ros-humble-joint-state-publisher-gui ros-humble-rviz2
```

---

## Launching in RViz

From your workspace:

```bash
cd ~/h1_2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch unitree_h1_2_description display.launch.py
```

- This will open RViz with the robot model loaded.  
- Use the **Joint State Publisher GUI** to move joints interactively.

---

## Notes

- Make sure all **mesh files** are present in the `meshes/` folder.  
- All `<material>` elements in the URDF have a **name attribute** for RViz compatibility.  
- The robot origin is aligned with the `world` link via a fixed joint (`world_to_pelvis`).  

---

## Author

**Raviteja Tirumalapudi**  
