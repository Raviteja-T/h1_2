# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

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
        self.declare_parameter('hand_scale', 0.5)
        
        # Publishers
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/h1/joint_commands', 10)
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Subscriber for joystick
        self.joy_sub = self.create_subscription(Joy, '/joy', self.joy_callback, 10)
        
        # H1_2 joint positions (27 motors)
        self.joint_positions = [0.0] * 27
        self.set_standing_position()
        
        # Arm control state
        self.left_hand_open = False
        self.right_hand_open = False
        self.hug_mode = False
        self.arms_wide_open = False
        self.arms_crossed = False
        self.victory_pose = False
        self.muscle_pose = False
        
        self.get_logger().info('H12 Teleoperation Node Started')
        self.get_logger().info('Controls:')
        self.get_logger().info('  Left Stick: Move body')
        self.get_logger().info('  Right Stick: Control arms')
        self.get_logger().info('  A/B/X/Y: Special poses')
        self.get_logger().info('  L1/R1: Open/Close hands')
        self.get_logger().info('  L2/R2: Arm poses')
    
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
        
        # Hands - closed position
        self.set_hands_closed()
    
    def set_hands_closed(self):
        """Close both hands (gripping position)"""
        # Left hand fingers (closed/gripping)
        self.joint_positions[17] = 0.0   # Left wrist roll (closed)
        self.joint_positions[18] = 0.0   # Left wrist pitch 
        self.joint_positions[19] = 0.0   # Left wrist yaw
        
        # Right hand fingers (closed/gripping)
        self.joint_positions[24] = 0.0   # Right wrist roll (closed)
        self.joint_positions[25] = 0.0   # Right wrist pitch
        self.joint_positions[26] = 0.0   # Right wrist yaw
        
        self.left_hand_open = False
        self.right_hand_open = False
    
    def set_hands_open(self):
        """Open both hands wide"""
        # Left hand fingers (open wide)
        self.joint_positions[17] = 1.0   # Left wrist roll (open)
        self.joint_positions[18] = 0.5   # Left wrist pitch (spread)
        self.joint_positions[19] = 0.5   # Left wrist yaw (spread)
        
        # Right hand fingers (open wide)
        self.joint_positions[24] = -1.0  # Right wrist roll (open)
        self.joint_positions[25] = -0.5  # Right wrist pitch (spread)
        self.joint_positions[26] = -0.5  # Right wrist yaw (spread)
        
        self.left_hand_open = True
        self.right_hand_open = True
    
    def set_arms_wide_open(self):
        """Open arms wide fully (T-pose)"""
        # Reset other poses
        self.reset_arm_poses()
        
        # Left arm - fully extended sideways
        self.joint_positions[18] = 1.57   # Left shoulder pitch (90 degrees out)
        self.joint_positions[21] = 0.0    # Left elbow straight
        self.joint_positions[14] = 0.0    # Left shoulder roll
        
        # Right arm - fully extended sideways
        self.joint_positions[12] = -1.57  # Right shoulder pitch (-90 degrees out)
        self.joint_positions[15] = 0.0    # Right elbow straight
        self.joint_positions[21] = 0.0    # Right shoulder roll
        
        # Open hands
        self.set_hands_open()
        
        self.arms_wide_open = True
        self.get_logger().info('Arms WIDE OPEN (T-pose)')
    
    def set_arms_crossed(self):
        """Cross arms in front (defensive/thinking pose)"""
        # Reset other poses
        self.reset_arm_poses()
        
        # Left arm across right
        self.joint_positions[18] = -0.8   # Left shoulder pitch forward
        self.joint_positions[21] = -1.2   # Left elbow bent
        self.joint_positions[14] = 0.5    # Left shoulder roll across
        
        # Right arm across left
        self.joint_positions[12] = -0.8   # Right shoulder pitch forward
        self.joint_positions[15] = -1.2   # Right elbow bent
        self.joint_positions[21] = -0.5   # Right shoulder roll across
        
        self.arms_crossed = True
        self.get_logger().info('Arms CROSSED')
    
    def set_victory_pose(self):
        """Victory pose with arms raised in V shape"""
        # Reset other poses
        self.reset_arm_poses()
        
        # Both arms up in V shape
        self.joint_positions[18] = -1.2   # Left shoulder pitch up
        self.joint_positions[21] = -0.5   # Left elbow slightly bent
        self.joint_positions[14] = 0.3    # Left shoulder roll out
        
        self.joint_positions[12] = -1.2   # Right shoulder pitch up
        self.joint_positions[15] = -0.5   # Right elbow slightly bent
        self.joint_positions[21] = -0.3   # Right shoulder roll out
        
        # Open hands
        self.set_hands_open()
        
        self.victory_pose = True
        self.get_logger().info('VICTORY pose!')
    
    def set_muscle_pose(self):
        """Bodybuilder pose with flexed arms"""
        # Reset other poses
        self.reset_arm_poses()
        
        # Left arm flexed
        self.joint_positions[18] = -0.5   # Left shoulder pitch forward
        self.joint_positions[21] = -2.0   # Left elbow fully bent
        self.joint_positions[14] = 0.2    # Left shoulder roll
        
        # Right arm flexed
        self.joint_positions[12] = -0.5   # Right shoulder pitch forward
        self.joint_positions[15] = -2.0   # Right elbow fully bent
        self.joint_positions[21] = -0.2   # Right shoulder roll
        
        # Closed hands (fists)
        self.set_hands_closed()
        
        self.muscle_pose = True
        self.get_logger().info('MUSCLE pose!')
    
    def set_hug_position(self):
        """Set hands in hugging position to hold objects"""
        # Reset other poses
        self.reset_arm_poses()
        
        # Bring arms forward and hands in grasping position
        self.joint_positions[12] = -0.8   # Right shoulder pitch (forward)
        self.joint_positions[15] = -1.2   # Right elbow (bent)
        self.joint_positions[18] = -0.8   # Left shoulder pitch (forward)
        self.joint_positions[21] = -1.2   # Left elbow (bent)
        
        # Hands in gentle grip position
        self.joint_positions[17] = 0.3    # Left wrist roll (slightly open)
        self.joint_positions[24] = -0.3   # Right wrist roll (slightly open)
        
        self.hug_mode = True
        self.get_logger().info('Hug mode ACTIVATED - ready to hold objects!')
    
    def reset_arm_poses(self):
        """Reset all arm pose flags"""
        self.arms_wide_open = False
        self.arms_crossed = False
        self.victory_pose = False
        self.muscle_pose = False
        self.hug_mode = False
    
    def calculate_hand_distance(self):
        """Calculate distance between hands in millimeters"""
        # Simplified calculation based on arm positions
        
        # Calculate hand positions based on joint angles
        left_hand_pos = self.calculate_forward_kinematics_left()
        right_hand_pos = self.calculate_forward_kinematics_right()
        
        # Calculate distance
        distance = math.sqrt(
            (left_hand_pos[0] - right_hand_pos[0])**2 +
            (left_hand_pos[1] - right_hand_pos[1])**2 +
            (left_hand_pos[2] - right_hand_pos[2])**2
        )
        
        return distance * 1000  # Convert to millimeters
    
    def calculate_forward_kinematics_left(self):
        """Simplified forward kinematics for left hand"""
        shoulder_pitch = self.joint_positions[18] or 0.0
        shoulder_roll = self.joint_positions[14] or 0.0
        elbow = self.joint_positions[21] or 0.0
        
        # Approximate arm lengths (meters)
        upper_arm_length = 0.3
        lower_arm_length = 0.3
        
        x = upper_arm_length * math.sin(shoulder_pitch) + lower_arm_length * math.sin(shoulder_pitch + elbow)
        y = 0.2 + upper_arm_length * math.sin(shoulder_roll) + lower_arm_length * math.sin(shoulder_roll)  # Left side offset
        z = upper_arm_length * math.cos(shoulder_pitch) + lower_arm_length * math.cos(shoulder_pitch + elbow)
        
        return [x, y, z]
    
    def calculate_forward_kinematics_right(self):
        """Simplified forward kinematics for right hand"""
        shoulder_pitch = self.joint_positions[12] or 0.0
        shoulder_roll = self.joint_positions[21] or 0.0
        elbow = self.joint_positions[15] or 0.0
        
        # Approximate arm lengths (meters)
        upper_arm_length = 0.3
        lower_arm_length = 0.3
        
        x = upper_arm_length * math.sin(shoulder_pitch) + lower_arm_length * math.sin(shoulder_pitch + elbow)
        y = -0.2 - upper_arm_length * math.sin(shoulder_roll) - lower_arm_length * math.sin(shoulder_roll)  # Right side offset
        z = upper_arm_length * math.cos(shoulder_pitch) + lower_arm_length * math.cos(shoulder_pitch + elbow)
        
        return [x, y, z]
    
    def joy_callback(self, msg):
        """Handle joystick input"""
        try:
            # Get scaling parameters
            linear_scale = self.get_parameter('linear_scale').value
            angular_scale = self.get_parameter('angular_scale').value
            arm_scale = self.get_parameter('arm_scale').value
            hand_scale = self.get_parameter('hand_scale').value
            
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
            
            # Shoulder buttons for hand control
            l1_button = msg.buttons[4]  # Left shoulder button
            r1_button = msg.buttons[5]  # Right shoulder button
            l2_button = msg.buttons[6]  # Left trigger
            r2_button = msg.buttons[7]  # Right trigger
            
            # Create Twist message for body movement
            twist_msg = Twist()
            twist_msg.linear.x = left_y * linear_scale
            twist_msg.linear.y = left_x * linear_scale
            twist_msg.angular.z = right_x * angular_scale
            
            self.twist_pub.publish(twist_msg)
            
            # Control arms with right stick (only if no special pose active)
            if not any([self.arms_wide_open, self.arms_crossed, self.victory_pose, self.muscle_pose, self.hug_mode]):
                self.joint_positions[12] = right_y * arm_scale  # Right shoulder
                self.joint_positions[15] = -right_y * arm_scale * 0.7  # Right elbow
                self.joint_positions[18] = -right_y * arm_scale * 0.3  # Left shoulder
            
            # Hand controls
            if l1_button:  # Toggle left hand
                if self.left_hand_open:
                    self.set_left_hand_closed()
                else:
                    self.set_left_hand_open()
            
            if r1_button:  # Toggle right hand
                if self.right_hand_open:
                    self.set_right_hand_closed()
                else:
                    self.set_right_hand_open()
            
            # Arm pose controls
            if l2_button and r2_button:  # Both triggers - hug mode
                self.set_hug_position()
            elif l2_button:  # Left trigger - arms wide open
                self.set_arms_wide_open()
            elif r2_button:  # Right trigger - arms crossed
                self.set_arms_crossed()
            
            # Special poses with buttons
            if a_button:  # Victory pose
                self.set_victory_pose()
            
            if b_button:  # Reset to standing
                self.set_standing_position()
                self.reset_arm_poses()
            
            if x_button:  # Muscle pose
                self.set_muscle_pose()
            
            if y_button:  # T-pose (arms wide open)
                self.set_arms_wide_open()
            
            # Calculate and log hand distance
            hand_distance = self.calculate_hand_distance()
            self.get_logger().info(f'Distance between hands: {hand_distance:.1f} mm', throttle_duration_sec=1.0)
            
            # Publish joint commands
            joint_msg = Float64MultiArray()
            joint_msg.data = self.joint_positions
            self.cmd_pub.publish(joint_msg)
            
        except Exception as e:
            self.get_logger().error(f'Error in joy callback: {e}')
    
    def set_left_hand_open(self):
        """Open left hand wide"""
        self.joint_positions[17] = 1.0   # Left wrist roll (open)
        self.joint_positions[18] = 0.5   # Left wrist pitch (spread)
        self.joint_positions[19] = 0.5   # Left wrist yaw (spread)
        self.left_hand_open = True
        self.get_logger().info('Left hand OPEN')
    
    def set_left_hand_closed(self):
        """Close left hand"""
        self.joint_positions[17] = 0.0   # Left wrist roll (closed)
        self.joint_positions[18] = 0.0   # Left wrist pitch
        self.joint_positions[19] = 0.0   # Left wrist yaw
        self.left_hand_open = False
        self.get_logger().info('Left hand CLOSED')
    
    def set_right_hand_open(self):
        """Open right hand wide"""
        self.joint_positions[24] = -1.0  # Right wrist roll (open)
        self.joint_positions[25] = -0.5  # Right wrist pitch (spread)
        self.joint_positions[26] = -0.5  # Right wrist yaw (spread)
        self.right_hand_open = True
        self.get_logger().info('Right hand OPEN')
    
    def set_right_hand_closed(self):
        """Close right hand"""
        self.joint_positions[24] = 0.0   # Right wrist roll (closed)
        self.joint_positions[25] = 0.0   # Right wrist pitch
        self.joint_positions[26] = 0.0   # Right wrist yaw
        self.right_hand_open = False
        self.get_logger().info('Right hand CLOSED')
    
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