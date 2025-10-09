import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2

class UnitreeFrontCameraNode(Node):
    def __init__(self):
        super().__init__('unitree_front_camera_node')

        # ✅ Network interface connected to the robot
        self.interface_name = 'wlp0s20f3'  # <-- change to your host interface

        # Front camera GStreamer UDP pipeline
        self.front_gst_pipeline = (
            f"udpsrc address=230.1.1.1 port=1720 multicast-iface={self.interface_name} ! "
            "application/x-rtp, media=video, encoding-name=H264 ! "
            "rtph264depay ! h264parse ! avdec_h264 ! "
            "videoconvert ! video/x-raw,width=1280,height=720,format=BGR ! appsink drop=1"
        )

        # Publisher
        self.front_pub = self.create_publisher(Image, 'camera/front/image_raw', 10)
        self.bridge = CvBridge()

        # OpenCV VideoCapture
        self.front_cap = cv2.VideoCapture(self.front_gst_pipeline, cv2.CAP_GSTREAMER)

        if not self.front_cap.isOpened():
            self.get_logger().error("Failed to open front camera GStreamer UDP stream.")
        else:
            self.get_logger().info("Front camera streaming started.")

        # Timer for publishing at ~20 Hz
        self.timer = self.create_timer(0.05, self.timer_callback)

    def timer_callback(self):
        ret, frame = self.front_cap.read()
        if ret:
            msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            self.front_pub.publish(msg)
            self.get_logger().info("Published front camera frame")
        else:
            self.get_logger().warn("No frame received from front camera.")

def main(args=None):
    rclpy.init(args=args)
    node = UnitreeFrontCameraNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
