import sys
import cv2
import numpy as np
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient
from ultralytics import YOLO  # YOLOv8 for object detection

class RaviBotDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("H1-2 Dashboard Control Panel")
        self.setGeometry(100, 100, 1000, 750)

        # === Logo ===
        logo_label = QLabel()
        logo_pixmap = QPixmap("/home/toor/dashboard/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(184, 86))
        logo_label.setFixedSize(184, 86)

        # === Status & Camera View ===
        self.status_label = QLabel("Camera not connected")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; color: #888; margin-top: 20px;")

        self.camera_label = QLabel("Camera feed will appear here")
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setFixedSize(800, 600)
        self.camera_label.setStyleSheet("border: 1px solid #ccc;")

        # === Buttons ===
        self.connect_btn = QPushButton("Connect Camera")
        self.capture_btn = QPushButton("Capture Image")
        self.record_btn = QPushButton("Start Recording")
        self.detect_btn = QPushButton("Object Detection")
        self.quit_btn = QPushButton("Quit")

        self.capture_btn.setEnabled(False)
        self.record_btn.setEnabled(False)
        self.detect_btn.setEnabled(False)

        self.connect_btn.clicked.connect(self.connect_camera)
        self.capture_btn.clicked.connect(self.capture_image)
        self.record_btn.clicked.connect(self.start_recording)
        self.detect_btn.clicked.connect(self.toggle_detection)
        self.quit_btn.clicked.connect(self.close)

        # === Layout ===
        top_bar = QHBoxLayout()
        top_bar.addWidget(logo_label)
        top_bar.addStretch()

        button_bar = QHBoxLayout()
        button_bar.addStretch()
        button_bar.addWidget(self.capture_btn)
        button_bar.addWidget(self.record_btn)
        button_bar.addWidget(self.detect_btn)
        button_bar.addWidget(self.quit_btn)
        button_bar.addStretch()

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_bar)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)
        main_layout.addSpacing(20)
        main_layout.addWidget(self.connect_btn, alignment=Qt.AlignCenter)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_bar)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # === Camera & Detection Setup ===
        self.client = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.last_frame = None
        self.frame_to_record = None

        self.recording = False
        self.video_writer = None
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.record_frame)

        self.yolo_model = YOLO("yolov8n.pt")
        self.detecting = False

    def connect_camera(self):
        try:
            ChannelFactoryInitialize(0)
            self.client = VideoClient()
            self.client.SetTimeout(3.0)
            self.client.Init()

            self.status_label.setText("Camera connected")
            self.status_label.setStyleSheet("font-size: 16px; color: green; margin-top: 20px;")
            self.capture_btn.setEnabled(True)
            self.record_btn.setEnabled(True)
            self.detect_btn.setEnabled(True)

            self.timer.start(30)
        except Exception as e:
            self.status_label.setText(f"Failed to connect: {e}")
            self.status_label.setStyleSheet("font-size: 16px; color: red; margin-top: 20px;")

    def update_camera_frame(self):
        if self.client:
            code, data = self.client.GetImageSample()
            if code == 0:
                image_data = np.frombuffer(bytes(data), dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                if image is not None:
                    self.last_frame = image

                    if self.detecting:
                        results = self.yolo_model(image)
                        annotated = results[0].plot()
                        boxes = results[0].boxes
                        names = results[0].names
                        self.save_detected_objects(boxes, names)
                        display_image = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)
                        self.frame_to_record = annotated
                    else:
                        display_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                        self.frame_to_record = image

                    h, w, ch = display_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(display_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    self.camera_label.setPixmap(QPixmap.fromImage(qt_image))
            else:
                self.status_label.setText(f"Camera error: {code}")
                self.status_label.setStyleSheet("font-size: 16px; color: red; margin-top: 20px;")

    def capture_image(self):
        if self.last_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captured_{timestamp}.jpg"
            cv2.imwrite(filename, self.last_frame)
            self.status_label.setText(f"Image saved: {filename}")
            self.status_label.setStyleSheet("font-size: 16px; color: purple; margin-top: 20px;")
        else:
            self.status_label.setText("No frame available to save")
            self.status_label.setStyleSheet("font-size: 16px; color: red; margin-top: 20px;")

    def start_recording(self):
        if not self.recording and self.frame_to_record is not None:
            height, width = self.frame_to_record.shape[:2]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
            self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            self.recording = True
            self.record_timer.start(50)
            self.status_label.setText(f"Recording started: {filename}")
            self.status_label.setStyleSheet("font-size: 16px; color: orange; margin-top: 20px;")
        elif self.recording:
            self.record_timer.stop()
            self.video_writer.release()
            self.video_writer = None
            self.recording = False
            self.status_label.setText("Recording stopped.")
            self.status_label.setStyleSheet("font-size: 16px; color: gray; margin-top: 20px;")

    def record_frame(self):
        if self.recording and self.frame_to_record is not None:
            self.video_writer.write(self.frame_to_record)

    def toggle_detection(self):
        self.detecting = not self.detecting
        if self.detecting:
            self.status_label.setText("Object detection ON")
            self.status_label.setStyleSheet("font-size: 16px; color: blue; margin-top: 20px;")
        else:
            self.status_label.setText("Object detection OFF")
            self.status_label.setStyleSheet("font-size: 16px; color: gray; margin-top: 20px;")

    def save_detected_objects(self, boxes, names, filename="detected_objects.txt"):
        detected_classes = set()
        for box in boxes:
            cls_id = int(box.cls[0].item())
            detected_classes.add(names[cls_id])
        with open(filename, "w") as f:
            for obj_name in sorted(detected_classes):
                f.write(f"{obj_name}\n")

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Escape, Qt.Key_Q]:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RaviBotDashboard()
    window.show()
    sys.exit(app.exec_())
