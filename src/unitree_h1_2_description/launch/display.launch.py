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

    # RViz config file (optional, create 'rviz/h1_2.rviz' if needed)
    rviz_config_file = os.path.join(
        get_package_share_directory(pkg_name),
        'rviz',
        'h1_2.rviz'
    )

    return LaunchDescription([
        # -------------------------------
        # Joint State Publisher GUI
        # -------------------------------
        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            parameters=[{'use_gui': True, 'include_fixed_joints': True}]
        ),

        # -------------------------------
        # Robot State Publisher
        # -------------------------------
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'robot_description': open(urdf_path).read()}]
        ),

        # -------------------------------
        # LowState -> JointState + TF Node
        # -------------------------------
        Node(
            package='unitree_h1_2_description',
            executable='lowstate_to_jointstate_full',
            name='lowstate_to_jointstate_full',
            output='screen'
        ),

        # -------------------------------
        # Front Camera Node
        # -------------------------------
        Node(
            package='unitree_camera_node',
            executable='camera_publisher',
            name='unitree_front_camera_node',
            output='screen'
        ),

        # -------------------------------
        # RViz2
        # -------------------------------
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file],
            parameters=[{'use_sim_time': True}]
        ),
    ])
