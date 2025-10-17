#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from ultralytics import YOLO

class SegmentationNode(Node):
    def __init__(self):
        super().__init__('segmentation_node')
        self.get_logger().info('Initializing YOLOv8 segmentation node...')

        # Subscribe to RealSense color image
        self.subscription = self.create_subscription(
            Image, '/camera/camera/color/image_raw', self.listener_callback, 10)
        self.subscription  # prevent unused variable warning

        # Publisher for segmented image
        self.publisher = self.create_publisher(Image, '/segmentation/output', 10)

        # Bridge for ROS ↔ OpenCV
        self.bridge = CvBridge()

        # Load YOLOv8 segmentation model
        self.model = YOLO('yolov8n-seg.pt')  # lightweight model
        self.get_logger().info('YOLOv8n-seg model loaded successfully.')

    def listener_callback(self, data):
        """Callback when an image is received."""
        try:
            # Convert ROS image to OpenCV
            frame = self.bridge.imgmsg_to_cv2(data, desired_encoding='bgr8')

            # Run YOLO segmentation
            results = self.model(frame)
            annotated_frame = results[0].plot()

            # Display the result in an OpenCV window
            cv2.imshow('YOLOv8 Segmentation', annotated_frame)
            cv2.waitKey(1)

            # Publish annotated image back to ROS
            seg_image = self.bridge.cv2_to_imgmsg(annotated_frame, encoding='bgr8')
            self.publisher.publish(seg_image)

        except Exception as e:
            self.get_logger().error(f'Error processing frame: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = SegmentationNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down segmentation node.')
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
