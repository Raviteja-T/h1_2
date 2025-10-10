import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_name = 'unitree_h1_2_description'
    urdf_file = 'h1_2.urdf'

    urdf_path = os.path.join(
        get_package_share_directory(pkg_name),
        urdf_file
    )

    return LaunchDescription([
        # Use joint_state_publisher_gui to allow interactive joint updates
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'use_gui': True, 'include_fixed_joints': True}]
        ),

        # Robot state publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': open(urdf_path).read()}]
        ),

        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', os.path.join(
                get_package_share_directory(pkg_name),
                'rviz',
                'h1_2.rviz'
            )],
            parameters=[{'use_sim_time': True}]
        )
    ])
