# 🦿 Unitree H1-2 Real Robot Visualization

This branch enables **real-time visualization** of the **Unitree H1-2 humanoid robot** in **RViz 2**, using live joint data streamed from the physical robot.  
It bridges the robot’s **LowState data** (via UDP/TCP) with ROS 2’s standard `/joint_states` topic, allowing synchronized motion visualization.

---

## 🌐 Overview

The node reads **joint state feedback** from the Unitree H1-2 robot—positions, velocities, and efforts—and publishes them to ROS 2 in real-time.  
This enables users to view actual robot movements inside **RViz 2**, fully synced with the hardware.

---

## 🧩 Features

- ✅ Real-time ROS 2 visualization of H1-2 joint movements  
- ✅ Conversion from LowState → JointState messages  
- ✅ Compatible with **ROS 2 Humble**  
- ✅ URDF-based visualization in RViz  
- ✅ Configurable network interface (e.g., `wlp0s20f3`)  

---

## ⚙️ Node Information

- **Package:** `unitree_h1_2_description`  
- **Node:** `unitree_joint_state_publisher`  
- **Published Topic:** `/joint_states`

### Parameters

| Name             | Description                          | Default       |
|------------------|--------------------------------------|---------------|
| `interface_name` | Network interface connected to robot | `wlp0s20f3`   |
| `publish_rate`   | Joint state update frequency (Hz)    | `50`          |

---

## 🚀 Usage

### 1️⃣ Build the workspace
```bash
cd ~/ros2_ws
colcon build --packages-select unitree_h1_2_description
source install/setup.bash
```

### 2️⃣ Run the joint state publisher node
```bash
ros2 run unitree_h1_2_description joint_state_publisher --ros-args -p interface_name:=wlp0s20f3
```

### 3️⃣ Launch RViz for visualization
```bash
ros2 launch unitree_h1_2_description rviz_h1_visualization.launch.py
```

---

## 🎥 Demo

The following video demonstrates live visualization of the Unitree H1-2 robot:  
`/home/ravi/h1_2/h1-2 movement.webm`

---

## 📝 Notes

- Ensure both your system and the robot are on the same subnet (e.g., `192.168.123.x`)  
- If you encounter `No transform from [world] to [torso_link]`, verify the URDF hierarchy  
- This branch focuses solely on visualization; motion planning and control integration will be added in future updates

---

## 👤 Author

**Tirumalapudi Raviteja**  