# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import sys
import os

# Add unitree_sdk2_python to path
sys.path.append(os.path.expanduser('~/unitree_sdk2_python'))

from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_

class UnitreeBridgeNode(Node):
    def __init__(self):
        super().__init__('unitree_bridge_node')
        
        # Initialize Unitree SDK2
        ChannelFactoryInitialize(1, "lo")
        self.lowcmd_pub = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_pub.Init()
        
        # Subscribe to joint commands
        self.joint_sub = self.create_subscription(
            Float64MultiArray,
            '/h1/joint_commands',
            self.joint_callback,
            10
        )
        
        self.get_logger().info('Unitree Bridge Node Started')
        self.get_logger().info('Waiting for joint commands...')
    
    def joint_callback(self, msg):
        """Convert ROS2 joint commands to Unitree LowCmd"""
        try:
            lowcmd = unitree_hg_msg_dds__LowCmd_()
            
            # H1_2 motor mapping based on C++ simulator output
            # The C++ simulator has 27 actuators in this order:
            motor_mapping = {
                # Legs
                0: 0,   # left_hip_yaw_joint
                1: 1,   # left_hip_pitch_joint  
                2: 2,   # left_hip_roll_joint
                3: 3,   # left_knee_joint
                4: 4,   # left_ankle_pitch_joint
                5: 5,   # left_ankle_roll_joint
                6: 6,   # right_hip_yaw_joint
                7: 7,   # right_hip_pitch_joint
                8: 8,   # right_hip_roll_joint
                9: 9,   # right_knee_joint
                10: 10, # right_ankle_pitch_joint
                11: 11, # right_ankle_roll_joint
                12: 12, # torso_joint
                
                # Left Arm
                13: 13, # left_shoulder_pitch_joint
                14: 14, # left_shoulder_roll_joint
                15: 15, # left_shoulder_yaw_joint
                16: 16, # left_elbow_joint
                17: 17, # left_wrist_roll_joint
                18: 18, # left_wrist_pitch_joint
                19: 19, # left_wrist_yaw_joint
                
                # Right Arm
                20: 20, # right_shoulder_pitch_joint
                21: 21, # right_shoulder_roll_joint
                22: 22, # right_shoulder_yaw_joint
                23: 23, # right_elbow_joint
                24: 24, # right_wrist_roll_joint
                25: 25, # right_wrist_pitch_joint
                26: 26, # right_wrist_yaw_joint
            }
            
            # Apply joint positions with proper mapping
            num_motors = min(len(msg.data), 27)  # H1_2 has 27 motors
            
            for ros2_index in range(num_motors):
                unitree_index = motor_mapping.get(ros2_index, ros2_index)
                if unitree_index < len(lowcmd.motor_cmd):
                    lowcmd.motor_cmd[unitree_index].q = msg.data[ros2_index]
                    lowcmd.motor_cmd[unitree_index].kp = 100.0  # Higher gain for stability
                    lowcmd.motor_cmd[unitree_index].kd = 5.0
                    lowcmd.motor_cmd[unitree_index].tau = 0.0
            
            # Send to simulator
            if self.lowcmd_pub.Write(lowcmd, 0.1):
                self.get_logger().info(f'Sent command to {num_motors} motors', throttle_duration_sec=2.0)
            else:
                self.get_logger().warn('Failed to send command to simulator')
                
        except Exception as e:
            self.get_logger().error(f'Error in joint callback: {e}')

def main():
    rclpy.init()
    node = UnitreeBridgeNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()