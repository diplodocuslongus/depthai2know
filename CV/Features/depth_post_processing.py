#!/usr/bin/env python3

import cv2
import depthai as dai
import numpy as np

def bin_dispmap(disparity_map, bin_sz):
    height, width = disparity_map.shape
    bin_h, bin_w = bin_sz

    # dims of the binned map
    bin_height = height // bin_h
    bin_width = width // bin_w
    binned_disp= np.zeros((bin_height, bin_width), dtype=np.float32)
    # TODO: use numpy instead of for loop
    for i in range(bin_height):
        for j in range(bin_width):
            bin_data = disparity_map[i * bin_h:(i + 1) * bin_h, j * bin_w:(j + 1) * bin_w]
            # mean of the bin (or median)
            # binned_disparity[i, j] = np.mean(bin_data)
            binned_disparity[i, j] = np.median(bin_data)

    return binned_disparity
# Closer-in minimum depth, disparity range is doubled (from 95 to 190):
extended_disparity = False
# Better accuracy for longer distance, fractional disparity 32-levels:
subpixel = False
# Better handling for occlusions:
lr_check = True

bin_sz = (8, 8)
# bin_sz = (4, 4)
# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
depth = pipeline.create(dai.node.StereoDepth)
xoutDisparity = pipeline.create(dai.node.XLinkOut)

xoutDisparity.setStreamName("disparity")

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setCamera("left")
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setCamera("right")

# Create a node that will produce the depth map (using disparity output as it's easier to visualize depth this way)
depth.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
# Options: MEDIAN_OFF, KERNEL_3x3, KERNEL_5x5, KERNEL_7x7 (default)
depth.initialConfig.setMedianFilter(dai.MedianFilter.KERNEL_7x7)
depth.setLeftRightCheck(lr_check)
depth.setExtendedDisparity(extended_disparity)
depth.setSubpixel(subpixel)

config = depth.initialConfig.get()
config.postProcessing.speckleFilter.enable = False
config.postProcessing.speckleFilter.speckleRange = 50
config.postProcessing.temporalFilter.enable = True
config.postProcessing.spatialFilter.enable = True
config.postProcessing.spatialFilter.holeFillingRadius = 2
config.postProcessing.spatialFilter.numIterations = 1
config.postProcessing.thresholdFilter.minRange = 400
# config.postProcessing.thresholdFilter.maxRange = 15000
config.postProcessing.thresholdFilter.maxRange = 900 #15000
config.postProcessing.decimationFilter.decimationFactor = 1
depth.initialConfig.set(config)

# Linking
monoLeft.out.link(depth.left)
monoRight.out.link(depth.right)
depth.disparity.link(xoutDisparity.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queue will be used to get the disparity frames from the outputs defined above
    q = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)

    while True:
        inDisparity = q.get()  # blocking call, will wait until a new data has arrived
        frame = inDisparity.getFrame()
        binned_map = bin_dispmap(frame, bin_sz)
        # Normalization for better visualization
        frame = (frame * (255 / depth.initialConfig.getMaxDisparity())).astype(np.uint8)

        cv2.imshow("disparity", frame)


        # Optionally display the binned disparity map
        normalized_binned_disp = cv2.normalize(binned_map, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        cv2.imshow("Binned Disparity", normalized_binned_disp)
        # cv2.imshow("Binned Disparity", binned_map)
        # cv2.waitKey(1)

        # Available color maps: https://docs.opencv.org/3.4/d3/d50/group__imgproc__colormap.html
        # frame = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
        # cv2.imshow("disparity_color", frame)

        if cv2.waitKey(1) == ord('q'):
            break
