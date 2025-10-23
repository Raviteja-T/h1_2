# Unitree H1-2 Robot Dashboard

This project provides a real-time dashboard for the Unitree H1-2 robot, displaying IMU data, joint states, battery information, and front camera feed. The dashboard is built using **PyQt6** for GUI and **pyqtgraph** for live plotting.

## Features

- Real-time IMU visualization (Roll, Pitch, Yaw)  
- Battery status display (voltage, current, temperature, cycle count)  
- Joint states table (`q` and `dq`) for all 27 motors  
- Front camera feed integrated into the dashboard  
- Graceful exit and automatic stop of data streams  

## Requirements

- Python >= 3.10  
- PyQt6  
- pyqtgraph  
- OpenCV (`opencv-python`)  
- `unitree-sdk2py` (Unitree Python SDK v2)  

You can install dependencies with:

```bash
pip install pyqt6 pyqtgraph opencv-python unitree-sdk2py
```

## Setup

1. Connect your computer to the H1-2 robot network.  
2. Set your system IP in the same subnet as the robot (e.g., `192.168.123.x`).  
3. Ensure DDS communication is working using the Unitree SDK.  

## Usage

```bash
python3 dashboard.py <network_interface>
```

Example:

```bash
python3 dashboard.py wlp0s20f3
```

- Press the **X** button to close the dashboard gracefully.  
- The dashboard updates IMU, joint, battery, and camera data in real time.  


## Author

Raviteja Tirumalapudi  

## License

This project is released under **BSD-3-Clause License**.