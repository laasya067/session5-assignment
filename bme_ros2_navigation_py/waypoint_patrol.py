import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import FollowWaypoints
from action_msgs.msg import GoalStatus

from tf_transformations import quaternion_from_euler


class WaypointPatrol(Node):

    def __init__(self):
        super().__init__("waypoint_patrol")

        self.client = ActionClient(
            self,
            FollowWaypoints,
            "/follow_waypoints"
        )

        self.last_waypoint = -1

        self.get_logger().info("Waiting for Nav2 FollowWaypoints server...")

        self.client.wait_for_server()

        self.get_logger().info("Connected!")

        self.send_waypoints()

    def make_pose(self, x, y, yaw):

        pose = PoseStamped()

        pose.header.frame_id = "map"

        pose.pose.position.x = x
        pose.pose.position.y = y

        q = quaternion_from_euler(0.0, 0.0, yaw)

        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]

        return pose

    def send_waypoints(self):

        goal = FollowWaypoints.Goal()

        goal.poses = [
            self.make_pose(0.0, 0.0, 0.0),
            self.make_pose(1.0, 0.0, 0.0),
            self.make_pose(1.0, 1.0, 1.57)
        ]

        self.get_logger().info("Sending 3 waypoints...")

        future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):

        current = feedback_msg.feedback.current_waypoint

        if self.last_waypoint == -1:
            self.last_waypoint = current
            self.get_logger().info(
                f"Navigating to Waypoint {current + 1}..."
            )
            return

        if current != self.last_waypoint:
            self.get_logger().info(
                f"Waypoint {self.last_waypoint + 1} Reached!"
            )

            self.last_waypoint = current

            self.get_logger().info(
                f"Navigating to Waypoint {current + 1}..."
            )

    def goal_response_callback(self, future):

        goal_handle = future.result()

        if not goal_handle.accepted:

            self.get_logger().info("Goal rejected!")

            return

        self.get_logger().info("Goal accepted!")

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):

        status = future.result().status

        if status == GoalStatus.STATUS_SUCCEEDED:

            self.get_logger().info(
                f"Waypoint {self.last_waypoint + 1} Reached!"
            )

            self.get_logger().info("All waypoints completed!")

        else:

            self.get_logger().info(
                f"Navigation failed. Status = {status}"
            )

        rclpy.shutdown()


def main(args=None):

    rclpy.init(args=args)

    node = WaypointPatrol()

    rclpy.spin(node)


if __name__ == "__main__":
    main()