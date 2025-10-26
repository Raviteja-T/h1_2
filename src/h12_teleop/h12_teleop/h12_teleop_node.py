# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Joy
from std_msgs.msg import Float64MultiArray
import math

class H12TeleopNode(Node):
    def __init__(self):
        super().__init__('h12_teleop_node')
        
        # Parameters
        self.declare_parameter('linear_scale', 0.5)
        self.declare_parameter('angular_scale', 1.0)
        self.declare_parameter('arm_scale', 0.3)
        
        # Publishers
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/h1/joint_commands', 10)
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber for joystick
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        
        # H1_2 joint positions (27 motors)
        self.joint_positions = [0.0] * 27
        self.set_standing_position()
        
        self.get_logger().info('H12 Teleoperation Node Started')
        self.get_logger().info('Controls:')
        self.get_logger().info('  Left Stick: Move body')
        self.get_logger().info('  Right Stick: Control arms')
        self.get_logger().info('  A/B: Change modes')
        self.get_logger().info('  X/Y: Special actions')
    
    def set_standing_position(self):
        """Set default standing position for H1_2"""
        # Legs - standing position
        self.joint_positions[1] = -0.3   # Left hip pitch
        self.joint_positions[3] = 0.6    # Left knee  
        self.joint_positions[4] = -0.3   # Left ankle pitch
        self.joint_positions[7] = -0.3   # Right hip pitch
        self.joint_positions[9] = 0.6    # Right knee
        self.joint_positions[10] = -0.3  # Right ankle pitch
        
        # Arms - neutral position
        self.joint_positions[12] = 0.0   # Right shoulder pitch
        self.joint_positions[15] = 0.0   # Right elbow
        self.joint_positions[18] = 0.0   # Left shoulder pitch
        self.joint_positions[21] = 0.0   # Left elbow
    
    def joy_callback(self, msg):
        """Handle joystick input"""
        try:
            # Get scaling parameters
            linear_scale = self.get_parameter('linear_scale').value
            angular_scale = self.get_parameter('angular_scale').value
            arm_scale = self.get_parameter('arm_scale').value
            
            # Left stick - body movement
            left_x = msg.axes[0]  # Usually axis 0
            left_y = msg.axes[1]  # Usually axis 1
            
            # Right stick - arm control
            right_x = msg.axes[2]  # Usually axis 2
            right_y = msg.axes[3]  # Usually axis 3
            
            # Buttons
            a_button = msg.buttons[0]  # Usually button 0
            b_button = msg.buttons[1]  # Usually button 1
            x_button = msg.buttons[2]  # Usually button 2
            y_button = msg.buttons[3]  # Usually button 3
            
            # Create Twist message for body movement
            twist_msg = Twist()
            twist_msg.linear.x = left_y * linear_scale
            twist_msg.linear.y = left_x * linear_scale
            twist_msg.angular.z = right_x * angular_scale
            
            self.twist_pub.publish(twist_msg)
            
            # Control arms with right stick
            self.joint_positions[12] = right_y * arm_scale  # Right shoulder
            self.joint_positions[15] = -right_y * arm_scale * 0.7  # Right elbow
            self.joint_positions[18] = -right_y * arm_scale * 0.3  # Left shoulder
            
            # Special actions with buttons
            if a_button:  # Wave right arm
                self.joint_positions[12] = math.sin(self.get_clock().now().nanoseconds / 1e9 * 2) * 0.5
                self.joint_positions[15] = -math.sin(self.get_clock().now().nanoseconds / 1e9 * 2) * 0.3
            
            if b_button:  # Reset to standing
                self.set_standing_position()
            
            if x_button:  # Raise arms
                self.joint_positions[12] = -0.5
                self.joint_positions[18] = -0.5
            
            if y_button:  # Lower arms
                self.joint_positions[12] = 0.5
                self.joint_positions[18] = 0.5
            
            # Publish joint commands
            joint_msg = Float64MultiArray()
            joint_msg.data = self.joint_positions
            self.cmd_pub.publish(joint_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error in joy callback: {e}')
    
    def publish_standing(self):
        """Publish standing position periodically"""
        joint_msg = Float64MultiArray()
        joint_msg.data = self.joint_positions
        self.cmd_pub.publish(joint_msg)

def main():
    rclpy.init()
    node = H12TeleopNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()