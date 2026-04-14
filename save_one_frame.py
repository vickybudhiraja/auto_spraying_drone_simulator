import os
import cv2
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

TOPIC = "/world/default/model/x500_mono_cam_down_0/link/camera_link/sensor/camera/image"
OUT_PATH = "/work/outputs/frame_001.png"

class FrameSaver(Node):
    def __init__(self):
        super().__init__("frame_saver")
        self.bridge = CvBridge()
        self.saved = False
        self.sub = self.create_subscription(
            Image,
            TOPIC,
            self.callback,
            qos_profile_sensor_data
        )

    def callback(self, msg):
        if self.saved:
            return
        rgb = self.bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
        cv2.imwrite(OUT_PATH, bgr)
        print(f"Saved {OUT_PATH}  shape={rgb.shape}")
        self.saved = True
        self.destroy_node()
        rclpy.shutdown()

def main():
    rclpy.init()
    node = FrameSaver()
    rclpy.spin(node)

if __name__ == "__main__":
    main()