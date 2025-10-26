# 🤖 Unitree H1_2 Humanoid Robot Teleoperation System

[![ROS2](https://img.shields.io/badge/ROS2-Humble-brightgreen.svg)](https://docs.ros.org/en/humble/)
[![MuJoCo](https://img.shields.io/badge/Simulator-MuJoCo-blue.svg)](https://mujoco.org/)
[![Unitree](https://img.shields.io/badge/Robot-Unitree_H1__2-orange.svg)](https://www.unitree.com/h1/)
[![Python](https://img.shields.io/badge/Python-3.8+-yellow.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete ROS2-based teleoperation system for Unitree H1_2 humanoid robot using MuJoCo simulation. Real-time keyboard control of 27 joints with full body movement, arm control, and bipedal walking gait capabilities.

**Author:** Raviteja Tirumalapudi
**Email:** t.raviteja@gmail.com  

## ✨ Features

- 🎮 **Real-time keyboard control** of all 27 H1_2 joints
- 🤖 **Full body movement** (leaning, rotating, balancing)
- 🦾 **Precise arm control** (individual and coordinated movements)
- 🚶‍♂️ **Bipedal walking gait** with forward/backward motion, strafing, and turning
- 🔄 **Multiple control modes** with real-time switching
- 📡 **ROS2-DDS bridge** for seamless simulator communication
- 🎯 **Elastic band support** for safe humanoid handling
- 📊 **System monitoring** with status reporting
- 🎪 **Arm waving animation** for demonstration
- 🚀 **Easy setup** with clear execution steps

## 🚀 Quick Start

### Prerequisites

- **Ubuntu** 20.04 or 22.04
- **ROS2** Humble ([installation guide](https://docs.ros.org/en/humble/Installation.html))
- **Python** 3.8+
- **MuJoCo** 3.3.6
- **Unitree SDK2** and **Unitree MuJoCo** simulator

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Raviteja-T/h1_2.git
cd unitree_ros2_ws
```
2. **Build the ROS2 package:**
```bash
colcon build --packages-select h12_teleop
source install/setup.bash
```

### 🎯 Teleoperation Setup

#### Step-by-Step Execution

**Terminal 1: Start Simulator**
```bash
cd ~/.mujoco/unitree_mujoco/simulate/build
./unitree_mujoco
```
Wait for the simulator window to open with H1_2 robot

**Terminal 2: Start ROS2 Bridge**
```bash
cd ~/unitree_ros2_ws
source install/setup.bash
ros2 run h12_teleop unitree_bridge_node
```
You should see: `Unitree Bridge Node Started`

**Terminal 3: Start Keyboard Control**
```bash
cd ~/unitree_ros2_ws
source install/setup.bash
ros2 run h12_teleop keyboard_teleop_node
```
You will see the control instructions printed.

### Configuration

**C++ Simulator Config (`~/.mujoco/unitree_mujoco/simulate/config.yaml`):**
```yaml
robot: "h1_2"
robot_scene: "scene.xml"
domain_id: 1
interface: "lo"
use_joystick: 0
enable_elastic_band: 1
```

## 🎮 Control Instructions

Once the system is running, use these keys in the Keyboard Control terminal:

### Body Movement Mode (Default)
| Key | Action | Description |
|-----|---------|-------------|
| W | Lean Forward | Bend forward at hips |
| S | Lean Backward | Bend backward at hips |
| A | Lean Left | Shift weight to left |
| D | Lean Right | Shift weight to right |
| Q | Rotate Left | Twist torso counterclockwise |
| E | Rotate Right | Twist torso clockwise |
| X | Stop Movement | Return to neutral position |

### Arm Control Mode (Press M to switch)
| Key | Action | Description |
|-----|---------|-------------|
| I | Right Arm Up | Raise right shoulder |
| K | Right Arm Down | Lower right shoulder |
| J | Left Arm Up | Raise left shoulder |
| L | Left Arm Down | Lower left shoulder |
| U | Both Arms Up | Raise both arms |
| O | Both Arms Down | Lower both arms |

### Walking Gait Mode (Press M again to switch)
| Key | Action | Description |
|-----|---------|-------------|
| G | Toggle Walking | Start/stop walking |
| W | Walk Forward | Move forward |
| S | Walk Backward | Move backward |
| A | Strafe Left | Move left |
| D | Strafe Right | Move right |
| Q | Turn Left | Rotate counterclockwise |
| E | Turn Right | Rotate clockwise |
| X | Stop Walking | Halt all movement |

### Special Functions
| Key | Action | Description |
|-----|---------|-------------|
| R | Reset | Return to standing position |
| T | Toggle Wave | Enable/disable arm waving |
| M | Switch Mode | Cycle through control modes |
| C | Status | Show current system status |

**Simulator Controls:**
```
9 - Toggle elastic band (safety feature)
7 - Lower robot to ground
8 - Lift robot up
Mouse - Rotate camera view
Scroll - Zoom in/out
```

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Keyboard      │    │   ROS2 Bridge    │    │  Unitree SDK2    │
│    Input        │───▶│   (DDS Domain 1) │───▶│    Interface     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Control Logic  │    │  Message Routing │    │  MuJoCo Simulator│
│  & Gait Control │    │   & Translation  │    │   H1_2 Robot     │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## 📁 Project Structure

```
unitree_ros2_ws/src/h12_teleop/
├── h12_teleop/
│   ├── keyboard_teleop_node.py  # Main control node
│   ├── unitree_bridge_node.py   # ROS2-Unitree bridge
│   ├── gait_controller.py       # Bipedal walking gait
│   └── __init__.py
├── launch/
│   ├── teleop.launch.py         # Joystick launch
│   └── keyboard_teleop.launch.py
├── package.xml                  # ROS2 package config
├── setup.py                     # Python setup
└── README.md
```

## 🤖 Walking Gait Implementation

The system includes a sophisticated bipedal gait controller:

**Gait Features:**
- State Machine: Double support, left/right swing phases  
- Smooth Trajectories: Cycloid motion for natural foot movement  
- Balance Control: COM shifting and ankle strategy  
- Adaptive Parameters: Adjustable step length, height, and timing  

**Gait States:**
- Double Support: Both feet on ground  
- Left Swing: Left leg moving forward  
- Right Swing: Right leg moving forward  
- Transition: Phase switching  

## 🔍 Verification

**To verify the system is working correctly:**

Check ROS2 Communication:
```bash
ros2 node list
ros2 topic list
```

Monitor Message Flow:
```bash
ros2 topic hz /h1/joint_commands
```

Test Sequence:
1. Press `R` - Robot resets to standing position  
2. Press `I` - Right arm moves upward  
3. Press `M` then `G` then `W` - Start walking forward  
4. Press `X` - Stop walking  

## 🛠️ Troubleshooting

| Issue | Solution |
|--------|-----------|
| Simulator not starting | Check MuJoCo installation and Unitree mujoco build |
| Bridge connection failed | Verify `domain_id=1` in `config.yaml` |
| No robot movement | Check if joint commands are published (`ros2 topic echo /h1/joint_commands`) |
| Keyboard not responding | Ensure terminal has focus for input |
| Robot falls over | Use elastic band (`press 9`) or reset (`press R`) |
| Import errors | Rebuild package: `colcon build --packages-select h12_teleop` |


## 📄 License

This project is licensed under the **MIT License** - see the LICENSE file for details.

## 🙏 Acknowledgments

- Unitree Robotics for the H1_2 robot model and simulator  
- MuJoCo Team for the physics engine  
- ROS2 Community for the robotics framework  
- Contributors who help improve this project  

## 📞 Support

**Email:** t.raviteja@gmail.com  
**GitHub Issues:** Create New Issue  

<div align="center">
Built with ❤️ by Ravi Teja  
⭐ If this project helped you, please give it a star!
</div>