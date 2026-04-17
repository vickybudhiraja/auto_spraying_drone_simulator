import os
import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

TOPIC = "/world/real_terrain/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image"
OUT_DIR = "/work/outputs/frames"
SAVE_EVERY_N = 10

class FrameSaver(Node):
    def __init__(self):
        super().__init__("frame_saver")
        self.bridge = CvBridge()
        self.frame_idx = 0
        self.saved_idx = 0
        os.makedirs(OUT_DIR, exist_ok=True)

        self.sub = self.create_subscription(
            Image,
            TOPIC,
            self.callback,
            qos_profile_sensor_data
        )

    def callback(self, msg):
        self.frame_idx += 1

        if self.frame_idx % SAVE_EVERY_N != 0:
            return

        rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

        out_path = os.path.join(OUT_DIR, f"frame_{self.saved_idx:05d}.png")
        cv2.imwrite(out_path, bgr)
        print(f"Saved {out_path}")

        self.saved_idx += 1

def main():
    rclpy.init()
    node = FrameSaver()
    rclpy.spin(node)

if __name__ == "__main__":
    main()