# Unitree Front Camera ROS 2 Node

This ROS 2 package streams the **front camera** from a Unitree robot and publishes it as a ROS 2 `sensor_msgs/Image` topic (`/camera/image_raw`). It is fully ROS 2 compliant and allows other nodes to subscribe for further processing.

---

## Install Dependencies

```bash
sudo apt update
sudo apt install ros-<ros2-distro>-cv-bridge python3-opencv
```

---

## Build Workspace

```bash
cd ~/ros2_ws
colcon build
source install/setup.bash
```

---

## Usage

### Run the Camera Node

```bash
ros2 run unitree_camera_node camera_publisher
```

By default, it streams the **front camera** at **20 Hz**.

### View Live Feed

```bash
ros2 run rqt_image_view rqt_image_view
```

- Select topic: `/camera/image_raw`

---

## Configuration

### Stream URL

Set your RTSP URL inside `camera_publisher.py`:

```python
self.stream_url = 'rtsp://192.168.123.161:8551/front_video'
```

### Publishing Rate

Adjust the timer interval:

```python
self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz
```

### Logging

Reduce logging frequency for smoother performance:

```python
self.get_logger().debug("Published frame")
```

---

## Extending for Back Camera

- Duplicate the node and change the RTSP URL and topic name:

```python
self.stream_url = 'rtsp://192.168.123.161:8552/back_video'
self.publisher_ = self.create_publisher(Image, 'camera/back/image_raw', 10)
```

- Subscribe to `/camera/back/image_raw` separately.

---

## Notes

- Ensure a **network connection** to the Unitree robot.
- RTSP/FFmpeg must be installed as OpenCV uses it to grab frames.
- For **low latency streaming**, consider using **GStreamer pipelines** in the future.

---

## License

MIT License. See [LICENSE](LICENSE) for details.