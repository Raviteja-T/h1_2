import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import numpy as np
import cv2
import sys

from rclpy.utilities import remove_ros_args
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient


class H1CameraNode(Node):
    def __init__(self):
        super().__init__('h1_camera_node')
        self.publisher = self.create_publisher(Image, '/unitree_h1/image_raw', 10)
        self.bridge = CvBridge()

        # ✅ Safely parse CLI args to avoid ROS flags
        ros_args = remove_ros_args(sys.argv)
        if len(ros_args) > 1:
            device_arg = ros_args[1]
            print(f"Using device argument: {device_arg}")
            ChannelFactoryInitialize(0, device_arg)
        else:
            print("Using default device")
            ChannelFactoryInitialize(0)

        self.get_logger().info("Initializing Unitree SDK...")
        self.client = VideoClient()
        self.client.SetTimeout(3.0)
        self.client.Init()
        self.get_logger().info("VideoClient initialized.")

        # ✅ Timer keeps node alive and streams frames
        self.timer = self.create_timer(0.05, self.capture_frame)

    def capture_frame(self):
        try:
            code, data = self.client.GetImageSample()
            if code != 0:
                self.get_logger().warn(f"GetImageSample failed with code: {code}")
                return

            img_array = np.frombuffer(bytes(data), dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if img is not None:
                ros_img = self.bridge.cv2_to_imgmsg(img, encoding='bgr8')
                self.publisher.publish(ros_img)
                self.get_logger().debug("Published frame to /unitree_h1/image_raw")
        except Exception as e:
            self.get_logger().error(f"Exception in capture_frame: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = H1CameraNode()
    node.get_logger().info("Spinning node...")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
