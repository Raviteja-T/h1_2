# Project Roadmap – Unitree H1-2 with LLM & VLM Integration

The goal of this project is to enable the Unitree H1-2 humanoid robot to communicate naturally with humans using Large Language Models (LLMs) and Vision-Language Models (VLMs), and to perform collaborative tasks such as picking up objects and handing them over safely to humans.

# Timeline (7–8 Months)

## Short-Term Goals (Months 1–3) – Foundation

- ✅ Confirm hardware configuration (PC modules, IPs, sensors).
- ✅ Establish SSH & ROS 2 communication with robot core and hands.
- ✅ Access and test onboard camera and hands control.
- Enable LiDAR and other sensors in ROS 2.
- Configure router/dual-IP solution for parallel access.
- Build dashboard for easy monitoring of robot sensors.
- Create URDF/Xacro model of H1-2 for simulation.
- Set up ROS 2 simulation environment (Gazebo/Isaac Sim).
- Implement basic teleop for joint-level and base movement.
- Document setup, connectivity, and workflows.


## Long-Term Goals (Months 4–8) – Integration & Autonomy

- Implement motion planning for arm and base in ROS 2.
- Develop grasping pipeline for simple objects.
- Integrate LLM for natural language command understanding.
- Integrate VLM for visual perception (object recognition/classification).
- Connect VLM outputs to ROS 2 perception and control stack.
- Enable human-robot interaction: “Pick up X and give it to me.”
- Deploy integrated LLM+VLM system on real H1-2.
- Optimize motion planning for safe and efficient handover.
- Conduct real-world trials with object pickup and human transfer.
- Prepare final workflow documentation, performance results, and demo presentation.


## End Goal
**A humanoid robot assistant that**
  - Understands natural language commands.
  - Recognizes objects visually.
  - Picks up objects safely.
  - Hands them over to humans in collaborative tasks.

## H1-2 Robot Dashboard

### Prerequisites
- Install and build **Unitree SDK2 (Python version)**. You can find it here: [unitreerobotics/unitree_sdk2_python](https://github.com/unitreerobotics/unitree_sdk2_python)  
- Ensure Python ≥ 3.8 and required dependencies (e.g. numpy, opencv-python, cyclonedds) are installed. 

### Run the Dashboard
```bash
python3 /dashboard/main.py

## Notes

- Sample files can be found in the old_records folder.
- Detected objects are saved in detected_objects.txt for future reference.
- LiDAR integration is currently in progress.
- Hand gripper functionality is under development.

## Author
**Tirumalapudi Raviteja**  
- Email: t.raviteja@gmail.com