#!/usr/bin/env python3

import cv2
import depthai as dai
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Header
import numpy as np

rclpy.init()
node = rclpy.create_node('oakd')
img_pub = node.create_publisher(Image, "mono_left", 1)

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
xoutLeft = pipeline.create(dai.node.XLinkOut)

xoutLeft.setStreamName('left')

# Properties
monoLeft.setCamera("left")
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)

# Linking
monoLeft.out.link(xoutLeft.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queues will be used to get the grayscale frames from the outputs defined above
    qLeft = device.getOutputQueue(name="left", maxSize=4, blocking=False)

    while rclpy.ok():
        inLeft = qLeft.get()
        frame = inLeft.getCvFrame()

        header = Header()
        header.frame_id = "body"
        header.stamp = node.get_clock().now().to_msg()
        img = Image()
        img.header = header
        img.height = inLeft.getHeight()
        img.width = inLeft.getWidth()
        img.is_bigendian = 0
        img.encoding = "mono8"
        img.step = inLeft.getWidth()
        img.data = frame.ravel()
        img_pub.publish(img)

rclpy.shutdown()
