import sys
import time
import threading
from collections import deque

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QImage, QPixmap
import pyqtgraph as pg
import cv2
import numpy as np

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_, BmsState_
from unitree_sdk2py.go2.video.video_client import VideoClient

# ====================== Global Data ======================
NUM_MOTORS = 27
robot_data = {
    "roll": 0, "pitch": 0, "yaw": 0,
    "battery_voltage": 0, "battery_current": 0, "battery_temp": 0, "battery_cycles": 0,
    "joint_q": [0]*NUM_MOTORS,
    "joint_dq": [0]*NUM_MOTORS
}

# Circular buffer for plotting IMU
history_len = 200
imu_history = {
    "roll": deque([0]*history_len, maxlen=history_len),
    "pitch": deque([0]*history_len, maxlen=history_len),
    "yaw": deque([0]*history_len, maxlen=history_len),
}

# Camera frame global
camera_frame = None
camera_lock = threading.Lock()

# ====================== DDS Callbacks ======================
def lowstate_callback(msg: LowState_):
    robot_data["roll"] = msg.imu_state.rpy[0]
    robot_data["pitch"] = msg.imu_state.rpy[1]
    robot_data["yaw"] = msg.imu_state.rpy[2]
    for i, m in enumerate(msg.motor_state):
        if i < NUM_MOTORS:
            robot_data["joint_q"][i] = m.q
            robot_data["joint_dq"][i] = m.dq
    imu_history["roll"].append(robot_data["roll"])
    imu_history["pitch"].append(robot_data["pitch"])
    imu_history["yaw"].append(robot_data["yaw"])

def bms_callback(msg: BmsState_):
    robot_data["battery_voltage"] = msg.voltage
    robot_data["battery_current"] = msg.current
    robot_data["battery_temp"] = msg.temperature
    robot_data["battery_cycles"] = msg.cycle_count

# ====================== Camera Thread ======================
def camera_thread():
    global camera_frame
    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    code, data = client.GetImageSample()
    while code == 0:
        code, data = client.GetImageSample()
        if code == 0:
            image_data = np.frombuffer(bytes(data), dtype=np.uint8)
            frame = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            with camera_lock:
                camera_frame = frame
        time.sleep(0.03)  # ~30 FPS

# ====================== GUI Dashboard ======================
class H1Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("H1-2 Robot Dashboard")
        self.resize(1400, 900)
        main_layout = QVBoxLayout()

        # ---------- Your Name ----------
        self.name_label = QLabel("Dashboard by: Raviteja Tirumalapudi")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        main_layout.addWidget(self.name_label)

        # ---------- Top Info: IMU labels + Battery ----------
        top_layout = QHBoxLayout()
        imu_layout = QHBoxLayout()
        self.roll_label = QLabel("Roll: 0.0")
        self.pitch_label = QLabel("Pitch: 0.0")
        self.yaw_label = QLabel("Yaw: 0.0")
        imu_layout.addWidget(self.roll_label)
        imu_layout.addWidget(self.pitch_label)
        imu_layout.addWidget(self.yaw_label)
        top_layout.addLayout(imu_layout)

        self.battery_label = QLabel("Battery: V:0 I:0 T:0 Cycles:0")
        top_layout.addWidget(self.battery_label)
        main_layout.addLayout(top_layout)

        # ---------- Joint Table ----------
        self.joint_table = QTableWidget()
        self.joint_table.setColumnCount(2)
        self.joint_table.setHorizontalHeaderLabels(["q", "dq"])
        self.joint_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.joint_table)

        # ---------- IMU Graph and Camera Side by Side ----------
        middle_layout = QHBoxLayout()

        # IMU Plot GroupBox
        imu_group = QGroupBox("IMU Graph")
        imu_layout_widget = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.addLegend()
        self.roll_curve = self.plot_widget.plot(list(imu_history["roll"]), pen='r', name="Roll")
        self.pitch_curve = self.plot_widget.plot(list(imu_history["pitch"]), pen='g', name="Pitch")
        self.yaw_curve = self.plot_widget.plot(list(imu_history["yaw"]), pen='b', name="Yaw")
        imu_layout_widget.addWidget(self.plot_widget)
        imu_group.setLayout(imu_layout_widget)
        middle_layout.addWidget(imu_group, 1)

        # Camera GroupBox
        cam_group = QGroupBox("Front Camera")
        cam_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cam_layout.addWidget(self.camera_label)
        cam_group.setLayout(cam_layout)
        middle_layout.addWidget(cam_group, 1)

        main_layout.addLayout(middle_layout)
        self.setLayout(main_layout)

        # Timer to refresh GUI
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(50)  # 20 Hz

    def update_dashboard(self):
        # Update labels
        self.roll_label.setText(f"Roll: {robot_data['roll']:.3f}")
        self.pitch_label.setText(f"Pitch: {robot_data['pitch']:.3f}")
        self.yaw_label.setText(f"Yaw: {robot_data['yaw']:.3f}")
        self.battery_label.setText(
            f"Battery V:{robot_data['battery_voltage']} "
            f"I:{robot_data['battery_current']} "
            f"T:{robot_data['battery_temp']} "
            f"Cycles:{robot_data['battery_cycles']}"
        )

        # Update joint table
        num_motors = len(robot_data["joint_q"])
        self.joint_table.setRowCount(num_motors)
        for i in range(num_motors):
            self.joint_table.setItem(i, 0, QTableWidgetItem(f"{robot_data['joint_q'][i]:.3f}"))
            self.joint_table.setItem(i, 1, QTableWidgetItem(f"{robot_data['joint_dq'][i]:.3f}"))

        # Update IMU plot
        self.roll_curve.setData(list(imu_history["roll"]))
        self.pitch_curve.setData(list(imu_history["pitch"]))
        self.yaw_curve.setData(list(imu_history["yaw"]))

        # Update camera feed
        if camera_frame is not None:
            with camera_lock:
                img = camera_frame.copy()
            h, w, ch = img.shape
            qt_img = QImage(img.data, w, h, ch*w, QImage.Format.Format_RGB888)
            self.camera_label.setPixmap(QPixmap.fromImage(qt_img).scaled(
                640, 480, Qt.AspectRatioMode.KeepAspectRatio
            ))

    # Graceful exit when window is closed
    def closeEvent(self, event):
        print("Dashboard closed by user.")
        QApplication.quit()

# ====================== DDS Initialization ======================
def init_dds(interface="wlp0s20f3"):
    if len(sys.argv) > 1:
        ChannelFactoryInitialize(0, sys.argv[1])
    else:
        ChannelFactoryInitialize(0)
    low_sub = ChannelSubscriber("rt/lowstate", LowState_)
    low_sub.Init(lowstate_callback, 10)
    bms_sub = ChannelSubscriber("rt/bms_state", BmsState_)
    bms_sub.Init(bms_callback, 10)
    return low_sub, bms_sub

# ====================== Main ======================
if __name__ == "__main__":
    # Initialize DDS
    low_sub, bms_sub = init_dds()

    # Start camera thread
    cam_thread = threading.Thread(target=camera_thread, daemon=True)
    cam_thread.start()

    # Start GUI
    app = QApplication(sys.argv)
    dashboard = H1Dashboard()
    dashboard.show()
    sys.exit(app.exec())

    # Clean up DDS (optional)
    low_sub.DeInit()
    bms_sub.DeInit()
