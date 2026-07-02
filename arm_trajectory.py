#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from trajectory_msgs.msg import JointTrajectory
from trajectory_msgs.msg import JointTrajectoryPoint
from builtin_interfaces.msg import Duration


class ArmTrajectory(Node):

    def __init__(self):

        super().__init__("arm_trajectory")

        self.publisher = self.create_publisher(
            JointTrajectory,
            "/arm_controller/joint_trajectory",
            10
        )

        self.timer = self.create_timer(2.0, self.publish_trajectory)

        self.sent = False

    def publish_trajectory(self):

        if self.sent:
            return

        msg = JointTrajectory()

        msg.joint_names = [
            "shoulder_pan_joint",
            "shoulder_lift_joint",
            "elbow_joint",
            "wrist_joint"
        ]

        point = JointTrajectoryPoint()

        #
        # Target:
        # X = 0.40
        # Y = 0.20
        # Z = 0.15
        #
        # Joint angles obtained from inverse kinematics
        #

        point.positions = [
            0.463648,      # j0
            -0.8386,       # j1
            1.9823,        # j2
            -1.1437        # j3
        ]

        point.time_from_start = Duration(sec=5)

        msg.points.append(point)

        self.publisher.publish(msg)

        self.get_logger().info("Publishing trajectory to arm_controller...")

        self.sent = True


def main(args=None):

    rclpy.init(args=args)

    node = ArmTrajectory()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()