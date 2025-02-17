#!/usr/bin/env python3

import cv2
import depthai as dai
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import numpy as np

class ImageSubscriber(Node):

    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/mono_left',
            self.image_callback,
            10)
        self.cv_window_name = "Received Image"
        cv2.namedWindow(self.cv_window_name, cv2.WINDOW_NORMAL)  # Allow resizing

    def image_callback(self, msg):
        try:
            width = msg.width
            height = msg.height
            encoding = msg.encoding
            data = np.frombuffer(msg.data, dtype=np.uint8)  # Convert to NumPy array

            if encoding == "bgr8":
                cv_image = data.reshape((height, width, 3))  # Reshape for BGR
            elif encoding == "rgb8":
                cv_image = data.reshape((height, width, 3))[:, :, ::-1] # Reshape and RGB to BGR
            elif encoding == "mono8":
                cv_image = data.reshape((height, width))  # Reshape for grayscale
            else:
                self.get_logger().warn(f"Unsupported encoding: {encoding}")
                return  # Don't try to display

            if cv_image is not None and not cv_image.size == 0: # Check if image is valid
                cv2.imshow(self.cv_window_name, cv_image)
                cv2.waitKey(1)
            else:
                self.get_logger().error("Could not create OpenCV image. Check encoding and data.")


        except Exception as e:
            self.get_logger().error(f"Error in callback: {e}")


def main(args=None):
    rclpy.init(args=args)
    image_subscriber = ImageSubscriber()
    rclpy.spin(image_subscriber)

    # Destroy the window when the node is stopped
    cv2.destroyAllWindows()
    image_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
