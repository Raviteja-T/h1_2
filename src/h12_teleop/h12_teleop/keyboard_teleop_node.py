# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64MultiArray
import math
import select
import sys
import termios
import tty

# Import the gait controller
from .gait_controller import BipedalGaitController, GaitState

class KeyboardTeleopNode(Node):
    def __init__(self):
        super().__init__('keyboard_teleop_node')
        
        # Publishers
        self.cmd_pub = self.create_publisher(Float64MultiArray, '/h1/joint_commands', 10)
        self.twist_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # Gait controller
        self.gait_controller = BipedalGaitController()
        
        # H1_2 joint positions (27 motors)
        self.joint_positions = [0.0] * 27
        self.set_standing_position()
        
        # Control state
        self.control_mode = 'BODY'  # 'BODY', 'ARMS', or 'WALKING'
        self.arm_wave_active = False
        self.wave_counter = 0
        self.body_movement_active = False
        self.body_movement_counter = 0
        self.walking_active = False
        self.walk_commands = [0.0, 0.0, 0.0]  # [forward, lateral, rotational]
        
        # Hand control state
        self.left_hand_open = False
        self.right_hand_open = False
        self.hug_mode = False
        
        self.get_logger().info('H12 Keyboard Teleoperation Node Started')
        self.print_controls()
        
        # Timer for periodic publishing
        self.timer = self.create_timer(0.1, self.timer_callback)  # 10Hz
        self.last_time = self.get_clock().now()
    
    def set_standing_position(self):
        """Set default standing position for H1_2"""
        # Reset all joints to zero first
        self.joint_positions = [0.0] * 27
        
        # Legs - standing position
        # Left leg
        self.joint_positions[1] = -0.4   # Left hip pitch
        self.joint_positions[3] = 0.8    # Left knee  
        self.joint_positions[4] = -0.4   # Left ankle pitch
        
        # Right leg
        self.joint_positions[7] = -0.4   # Right hip pitch
        self.joint_positions[9] = 0.8    # Right knee
        self.joint_positions[10] = -0.4  # Right ankle pitch
        
        # Torso - upright
        self.joint_positions[12] = 0.0   # Torso joint
        
        # Arms - neutral position
        # Left arm
        self.joint_positions[13] = 0.0   # Left shoulder pitch
        self.joint_positions[16] = 0.0   # Left elbow
        
        # Right arm
        self.joint_positions[20] = 0.0   # Right shoulder pitch
        self.joint_positions[23] = 0.0   # Right elbow
        
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
        self.get_logger().info('Both hands CLOSED')
    
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
        self.get_logger().info('Both hands OPEN')
    
    def set_hug_position(self):
        """Set hands in hugging position to hold objects"""
        # Bring arms forward and hands in grasping position
        self.joint_positions[13] = -0.8   # Left shoulder pitch (forward)
        self.joint_positions[16] = -1.2   # Left elbow (bent)
        self.joint_positions[20] = -0.8   # Right shoulder pitch (forward)
        self.joint_positions[23] = -1.2   # Right elbow (bent)
        
        # Hands in gentle grip position
        self.joint_positions[17] = 0.3    # Left wrist roll (slightly open)
        self.joint_positions[24] = -0.3   # Right wrist roll (slightly open)
        
        self.hug_mode = True
        self.get_logger().info('Hug mode ACTIVATED - ready to hold objects!')
    
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
        shoulder_pitch = self.joint_positions[13] or 0.0
        elbow = self.joint_positions[16] or 0.0
        
        # Approximate arm lengths (meters)
        upper_arm_length = 0.3
        lower_arm_length = 0.3
        
        x = upper_arm_length * math.sin(shoulder_pitch) + lower_arm_length * math.sin(shoulder_pitch + elbow)
        y = 0.2  # Left side offset
        z = upper_arm_length * math.cos(shoulder_pitch) + lower_arm_length * math.cos(shoulder_pitch + elbow)
        
        return [x, y, z]
    
    def calculate_forward_kinematics_right(self):
        """Simplified forward kinematics for right hand"""
        shoulder_pitch = self.joint_positions[20] or 0.0
        elbow = self.joint_positions[23] or 0.0
        
        # Approximate arm lengths (meters)
        upper_arm_length = 0.3
        lower_arm_length = 0.3
        
        x = upper_arm_length * math.sin(shoulder_pitch) + lower_arm_length * math.sin(shoulder_pitch + elbow)
        y = -0.2  # Right side offset
        z = upper_arm_length * math.cos(shoulder_pitch) + lower_arm_length * math.cos(shoulder_pitch + elbow)
        
        return [x, y, z]
    
    def print_controls(self):
        """Print keyboard controls"""
        print("\n=== H12 Keyboard Controls ===")
        print("BODY MOVEMENT (WASD + QE):")
        print("  W/S: Forward/Backward (lean body)")
        print("  A/D: Left/Right (lean body)")
        print("  Q/E: Rotate Left/Right (twist torso)")
        print("  X: Stop movement")
        
        print("\nARM CONTROL (IJKL + UO):")
        print("  I/K: Right Arm Up/Down")
        print("  J/L: Left Arm Up/Down")
        print("  U/O: Both Arms Up/Down")
        
        print("\nHAND CONTROL (FGH):")
        print("  F: Open both hands wide")
        print("  G: Close both hands")
        print("  H: Hug mode (hold objects)")
        print("  V: Toggle left hand")
        print("  B: Toggle right hand")
        
        print("\nWALKING GAIT (WALKING MODE):")
        print("  W/S: Walk Forward/Backward")
        print("  A/D: Strafe Left/Right")
        print("  Q/E: Turn Left/Right")
        print("  X: Stop walking")
        
        print("\nSPECIAL ACTIONS:")
        print("  R: Reset to standing")
        print("  T: Toggle arm waving")
        print("  M: Switch control mode")
        print("  G: Toggle walking")
        print("  C: Current status")
        print("  Ctrl+C: Exit")
        print(f"\nCurrent Mode: {self.control_mode}")
        print("=============================\n")
    
    def get_key(self):
        """Get single key input without blocking"""
        if select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None
    
    def timer_callback(self):
        """Main control loop"""
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time
        
        key = self.get_key()
        
        if key:
            self.handle_key_input(key.lower())
        
        # Handle arm waving if active
        if self.arm_wave_active:
            self.wave_counter += 1
            self.joint_positions[20] = math.sin(self.wave_counter * 0.2) * 0.5  # Right shoulder pitch
            self.joint_positions[23] = -math.sin(self.wave_counter * 0.2) * 0.3  # Right elbow
        
        # Handle body movement effects
        if self.body_movement_active and self.control_mode == 'BODY':
            self.body_movement_counter += 1
            self.apply_body_movement()
        
        # Handle walking gait
        if self.walking_active and self.control_mode == 'WALKING':
            self.joint_positions = self.gait_controller.update(dt, self.walk_commands)
        
        # Calculate and log hand distance
        hand_distance = self.calculate_hand_distance()
        self.get_logger().info(f'Distance between hands: {hand_distance:.1f} mm', throttle_duration_sec=1.0)
        
        # Publish joint commands
        self.publish_joint_commands()
    
    def handle_key_input(self, key):
        """Process keyboard input"""
        if self.control_mode == 'BODY':
            self.handle_body_controls(key)
        elif self.control_mode == 'ARMS':
            self.handle_arm_controls(key)
        elif self.control_mode == 'WALKING':
            self.handle_walking_controls(key)
        
        # Hand controls (mode-independent)
        if key == 'f':  # Open both hands
            self.set_hands_open()
        elif key == 'g':  # Close both hands
            self.set_hands_closed()
        elif key == 'h':  # Hug mode
            self.set_hug_position()
        elif key == 'v':  # Toggle left hand
            if self.left_hand_open:
                self.set_left_hand_closed()
            else:
                self.set_left_hand_open()
        elif key == 'b':  # Toggle right hand
            if self.right_hand_open:
                self.set_right_hand_closed()
            else:
                self.set_right_hand_open()
        
        # Mode-independent controls
        if key == 'r':  # Reset
            self.set_standing_position()
            self.body_movement_active = False
            self.walking_active = False
            self.walk_commands = [0.0, 0.0, 0.0]
            self.hug_mode = False
            self.get_logger().info('Reset to standing position')
        
        elif key == 't':  # Toggle arm wave
            self.arm_wave_active = not self.arm_wave_active
            status = "ON" if self.arm_wave_active else "OFF"
            self.get_logger().info(f'Arm waving {status}')
        
        elif key == 'm':  # Switch mode
            if self.control_mode == 'BODY':
                self.control_mode = 'ARMS'
            elif self.control_mode == 'ARMS':
                self.control_mode = 'WALKING'
            else:
                self.control_mode = 'BODY'
            self.get_logger().info(f'Switched to {self.control_mode} mode')
            self.print_controls()
        
        elif key == 'c':  # Status
            self.get_logger().info(f'Mode: {self.control_mode}, Walking: {self.walking_active}, Arm Wave: {self.arm_wave_active}')
            self.get_logger().info(f'Left hand: {"OPEN" if self.left_hand_open else "CLOSED"}, Right hand: {"OPEN" if self.right_hand_open else "CLOSED"}')
            self.get_logger().info(f'Hug mode: {"ACTIVE" if self.hug_mode else "INACTIVE"}')
    
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
    
    def handle_body_controls(self, key):
        """Handle body movement controls"""
        twist_msg = Twist()
        self.body_movement_active = True
        
        if key == 'w':  # Forward - lean forward
            twist_msg.linear.x = 0.5
            self.current_body_action = 'forward'
            self.get_logger().info('Leaning FORWARD')
        elif key == 's':  # Backward - lean backward
            twist_msg.linear.x = -0.5
            self.current_body_action = 'backward'
            self.get_logger().info('Leaning BACKWARD')
        elif key == 'a':  # Left - lean left
            twist_msg.linear.y = 0.5
            self.current_body_action = 'left'
            self.get_logger().info('Leaning LEFT')
        elif key == 'd':  # Right - lean right
            twist_msg.linear.y = -0.5
            self.current_body_action = 'right'
            self.get_logger().info('Leaning RIGHT')
        elif key == 'q':  # Rotate left - twist torso left
            twist_msg.angular.z = 1.0
            self.current_body_action = 'rotate_left'
            self.get_logger().info('Rotating torso LEFT')
        elif key == 'e':  # Rotate right - twist torso right
            twist_msg.angular.z = -1.0
            self.current_body_action = 'rotate_right'
            self.get_logger().info('Rotating torso RIGHT')
        elif key == 'x':  # Stop
            twist_msg.linear.x = 0.0
            twist_msg.linear.y = 0.0
            twist_msg.angular.z = 0.0
            self.body_movement_active = False
            self.get_logger().info('STOPPING body movement')
        
        self.twist_pub.publish(twist_msg)
    
    def handle_walking_controls(self, key):
        """Handle walking gait controls"""
        walk_speed = 0.5
        turn_speed = 0.3
        
        if key == 'w':  # Walk forward
            self.walk_commands[0] = walk_speed
            self.get_logger().info('Walking FORWARD')
        elif key == 's':  # Walk backward
            self.walk_commands[0] = -walk_speed
            self.get_logger().info('Walking BACKWARD')
        elif key == 'a':  # Strafe left
            self.walk_commands[1] = walk_speed
            self.get_logger().info('Strafing LEFT')
        elif key == 'd':  # Strafe right
            self.walk_commands[1] = -walk_speed
            self.get_logger().info('Strafing RIGHT')
        elif key == 'q':  # Turn left
            self.walk_commands[2] = turn_speed
            self.get_logger().info('Turning LEFT')
        elif key == 'e':  # Turn right
            self.walk_commands[2] = -turn_speed
            self.get_logger().info('Turning RIGHT')
        elif key == 'x':  # Stop walking
            self.walk_commands = [0.0, 0.0, 0.0]
            self.get_logger().info('STOPPING walking')
    
    def apply_body_movement(self):
        """Apply body movement effects to joint positions"""
        if not hasattr(self, 'current_body_action'):
            return
            
        # Reset to standing position first
        base_hip_pitch = -0.4
        base_knee = 0.8
        base_ankle_pitch = -0.4
        
        movement_magnitude = math.sin(self.body_movement_counter * 0.3) * 0.2
        
        if self.current_body_action == 'forward':
            # Lean forward: hips forward, knees bent more
            self.joint_positions[1] = base_hip_pitch + movement_magnitude  # Left hip
            self.joint_positions[7] = base_hip_pitch + movement_magnitude  # Right hip
            self.joint_positions[3] = base_knee + movement_magnitude * 0.5  # Left knee
            self.joint_positions[9] = base_knee + movement_magnitude * 0.5  # Right knee
            
        elif self.current_body_action == 'backward':
            # Lean backward: hips backward
            self.joint_positions[1] = base_hip_pitch - movement_magnitude  # Left hip
            self.joint_positions[7] = base_hip_pitch - movement_magnitude  # Right hip
            
        elif self.current_body_action == 'left':
            # Lean left: left hip different from right hip
            self.joint_positions[2] = movement_magnitude  # Left hip roll
            self.joint_positions[8] = -movement_magnitude  # Right hip roll
            
        elif self.current_body_action == 'right':
            # Lean right: right hip different from left hip
            self.joint_positions[2] = -movement_magnitude  # Left hip roll
            self.joint_positions[8] = movement_magnitude  # Right hip roll
            
        elif self.current_body_action == 'rotate_left':
            # Rotate torso left
            self.joint_positions[12] = movement_magnitude  # Torso joint
            
        elif self.current_body_action == 'rotate_right':
            # Rotate torso right
            self.joint_positions[12] = -movement_magnitude  # Torso joint
    
    def handle_arm_controls(self, key):
        """Handle arm movement controls"""
        if key == 'i':  # Right arm up
            self.joint_positions[20] -= 0.1  # Right shoulder pitch
            self.get_logger().info('Right arm UP')
        elif key == 'k':  # Right arm down
            self.joint_positions[20] += 0.1  # Right shoulder pitch
            self.get_logger().info('Right arm DOWN')
        elif key == 'j':  # Left arm up
            self.joint_positions[13] -= 0.1  # Left shoulder pitch
            self.get_logger().info('Left arm UP')
        elif key == 'l':  # Left arm down
            self.joint_positions[13] += 0.1  # Left shoulder pitch
            self.get_logger().info('Left arm DOWN')
        elif key == 'u':  # Both arms up
            self.joint_positions[20] -= 0.1  # Right shoulder pitch
            self.joint_positions[13] -= 0.1  # Left shoulder pitch
            self.get_logger().info('Both arms UP')
        elif key == 'o':  # Both arms down
            self.joint_positions[20] += 0.1  # Right shoulder pitch
            self.joint_positions[13] += 0.1  # Left shoulder pitch
            self.get_logger().info('Both arms DOWN')
    
    def publish_joint_commands(self):
        """Publish joint commands to Unitree bridge"""
        joint_msg = Float64MultiArray()
        joint_msg.data = self.joint_positions
        self.cmd_pub.publish(joint_msg)

def main():
    # Setup terminal for non-blocking input
    old_attr = termios.tcgetattr(sys.stdin)
    tty.setraw(sys.stdin.fileno())
    
    rclpy.init()
    node = KeyboardTeleopNode()
    
    try:
        print("Starting keyboard teleoperation...")
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        node.destroy_node()
        rclpy.shutdown()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_attr)
        print("Terminal restored.")

if __name__ == '__main__':
    main()