#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from unitree_sdk2py.core.channel import ChannelSubscriber, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowState_


class LowStateToJointStateFull(Node):
    def __init__(self):
        super().__init__('lowstate_to_jointstate_full')

        # Publisher for joint states
        self.joint_pub = self.create_publisher(JointState, '/joint_states', 10)

        # TF broadcaster for floating base
        self.tf_broadcaster = TransformBroadcaster(self)

        # Initialize the Unitree SDK channels
        ChannelFactoryInitialize(0)

        # Subscribe to the SDK LowState_ channel
        self.subscriber = ChannelSubscriber("rt/lowstate", LowState_)
        self.subscriber.Init(self.lowstate_callback, 10)

        # Full URDF joints (legs + torso + arms + hands)
        self.joint_names = [
            'left_hip_yaw_joint', 'left_hip_pitch_joint', 'left_hip_roll_joint',
            'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
            'right_hip_yaw_joint', 'right_hip_pitch_joint', 'right_hip_roll_joint',
            'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
            'torso_joint',
            'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
            'left_elbow_joint', 'left_wrist_roll_joint', 'left_wrist_pitch_joint', 'left_wrist_yaw_joint',
            'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
            'right_elbow_joint', 'right_wrist_roll_joint', 'right_wrist_pitch_joint', 'right_wrist_yaw_joint',
            # Left hand
            'L_thumb_proximal_yaw_joint', 'L_thumb_proximal_pitch_joint', 'L_thumb_intermediate_joint', 'L_thumb_distal_joint',
            'L_index_proximal_joint', 'L_index_intermediate_joint',
            'L_middle_proximal_joint', 'L_middle_intermediate_joint',
            'L_ring_proximal_joint', 'L_ring_intermediate_joint',
            'L_pinky_proximal_joint', 'L_pinky_intermediate_joint',
            # Right hand
            'R_thumb_proximal_yaw_joint', 'R_thumb_proximal_pitch_joint', 'R_thumb_intermediate_joint', 'R_thumb_distal_joint',
            'R_index_proximal_joint', 'R_index_intermediate_joint',
            'R_middle_proximal_joint', 'R_middle_intermediate_joint',
            'R_ring_proximal_joint', 'R_ring_intermediate_joint',
            'R_pinky_proximal_joint', 'R_pinky_intermediate_joint'
        ]

    def lowstate_callback(self, msg: LowState_):
        # --------------------------
        # Publish floating base as TF
        # --------------------------
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'world'
        t.child_frame_id = 'pelvis'

        # Fill translation and rotation (default zeros if unavailable)
        t.transform.translation.x = getattr(msg, 'x', 0.0)
        t.transform.translation.y = getattr(msg, 'y', 0.0)
        t.transform.translation.z = getattr(msg, 'z', 0.0)
        t.transform.rotation.x = getattr(msg, 'qx', 0.0)
        t.transform.rotation.y = getattr(msg, 'qy', 0.0)
        t.transform.rotation.z = getattr(msg, 'qz', 0.0)
        t.transform.rotation.w = getattr(msg, 'qw', 1.0)

        self.tf_broadcaster.sendTransform(t)

        # --------------------------
        # Publish joint states
        # --------------------------
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = self.joint_names

        # 35 motors from LowState_ (legs + torso + arms)
        positions = [m.q for m in msg.motor_state]
        velocities = [m.dq for m in msg.motor_state]
        efforts = [m.tau_est for m in msg.motor_state]

        # Fill remaining hand joints with zeros
        num_extra = len(self.joint_names) - len(positions)
        if num_extra > 0:
            positions += [0.0] * num_extra
            velocities += [0.0] * num_extra
            efforts += [0.0] * num_extra

        js.position = positions
        js.velocity = velocities
        js.effort = efforts

        self.joint_pub.publish(js)
        self.get_logger().debug(f'Published {len(self.joint_names)} joint states.')


def main(args=None):
    rclpy.init(args=args)
    node = LowStateToJointStateFull()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
