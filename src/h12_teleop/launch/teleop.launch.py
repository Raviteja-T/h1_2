# Author: Raviteja Tirumalapudi
# Email: t.raviteja@gmail.com

from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # # Joystick driver (if using a gamepad)
        # Node(
        #     package='joy',
        #     executable='joy_node',
        #     name='joy_node',
        #     output='screen',
        #     parameters=[{'dev': '/dev/input/js0'}]
        # ),
        
        # Keyboard teleoperation node
        Node(
            package='h12_teleop',
            executable='keyboard_teleop_node',
            name='keyboard_teleop_node',
            output='screen',
            prefix='xterm -e'
        ),
        
        # H1 Teleoperation node
        Node(
            package='h12_teleop',
            executable='h12_teleop_node',
            name='h12_teleop_node',
            output='screen',
            parameters=[
                {'linear_scale': 0.5},
                {'angular_scale': 1.0},
                {'arm_scale': 0.3}
            ]
        ),
        
        # Unitree bridge node
        Node(
            package='h12_teleop',
            executable='unitree_bridge_node',
            name='unitree_bridge_node',
            output='screen'
        )
    ])