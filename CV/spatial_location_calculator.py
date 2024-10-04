#!/usr/bin/env python3
# TODO 
# add multiple ROI at each line extrimities (for each lines, then refine by line length, strenght)
# fix the exposire to get a more reliable detection (maybe)
'''
                [[x1, y1, x2, y2, a, b, c, L],

#                 - [(x1, y1), (x2, y2)] is the segment (in image coordinates).
                - ax + by + c = 0 is the line equation
                - (a, b) is the normal vector of the line
                - |(a, b)| = 1, b >= 0
                - L is the length of the segment.

size of depthFrameColor: {depthFrameColor.shape[1],depthFrameColor.shape[0]}')
640x400

'''
import cv2
import depthai as dai
import numpy as np
import sys

sys.path.insert(0, '/home/ludofw/mygitrepos/opencv2know/line_detection/frezza_supelec')

import LSD_utils as mll

def line_orig(line_mll,W,H):
    global marg_px
    marg = marg_px # in pixels, attention to the equivalent in normlized points when setting the ROI
    a,b,c=line_mll[4],line_mll[5],line_mll[6]
    y=H - marg
    x = -1/a*(b*H+c)
    if x<0:
        # need to use the width
        x = W - marg
        y = -1/b*(a*W+c)
    return (int(x),int(y))



show_lines = False
min_line_length = 100# min line length
#Create default parametrization LSD
lsd = cv2.createLineSegmentDetector(0)
stepSize = 0.05
marg_px = 10 # margin from image border, in pixels
norm_marg = (marg_px-1) / 400 # margin from image border, in units normalized to img size
newConfig = False

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
spatialLocationCalculator = pipeline.create(dai.node.SpatialLocationCalculator)

xoutLeft = pipeline.create(dai.node.XLinkOut)
xoutDepth = pipeline.create(dai.node.XLinkOut)
xoutSpatialData = pipeline.create(dai.node.XLinkOut)
xinSpatialCalcConfig = pipeline.create(dai.node.XLinkIn)

xoutLeft.setStreamName("left")
xoutDepth.setStreamName("depth")
xoutSpatialData.setStreamName("spatialData")
xinSpatialCalcConfig.setStreamName("spatialCalcConfig")

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setCamera("left")
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setCamera("right")

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
stereo.setLeftRightCheck(True)
stereo.setSubpixel(True)

# Config 
# define ROI in normalized point (0-1) -> (0-image width), same for height
topLeft = dai.Point2f(0.2, 0.2) #(0.4, 0.4)
bottomRight = dai.Point2f(0.2, 0.2)#(0.6, 0.6)

config = dai.SpatialLocationCalculatorConfigData()
config.depthThresholds.lowerThreshold = 100
config.depthThresholds.upperThreshold = 10000
calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
config.roi = dai.Rect(topLeft, bottomRight)

spatialLocationCalculator.inputConfig.setWaitForMessage(False)
spatialLocationCalculator.initialConfig.addROI(config)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)
stereo.syncedLeft.link(xoutLeft.input)

spatialLocationCalculator.passthroughDepth.link(xoutDepth.input)
stereo.depth.link(spatialLocationCalculator.inputDepth)

spatialLocationCalculator.out.link(xoutSpatialData.input)
xinSpatialCalcConfig.out.link(spatialLocationCalculator.inputConfig)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queue will be used to get the depth frames from the outputs defined above
    leftQueue = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)
    spatialCalcQueue = device.getOutputQueue(name="spatialData", maxSize=4, blocking=False)
    spatialCalcConfigInQueue = device.getInputQueue("spatialCalcConfig")

    color = (255, 255, 255)

    print("Use WASD keys to move ROI!")

    while True:
        #linesLeft =  None
        inLeft = leftQueue.get().getCvFrame()
        inDepth = depthQueue.get() # Blocking call, will wait until a new data has arrived
        linesLeft = lsd.detect(inLeft)[0] 
        linesLeft = mll.from_lsd(linesLeft)

        # filter out the short segments
        linesLeft = linesLeft[linesLeft[...,7] > min_line_length]
        if len(linesLeft) > 1: # is not None:
            ptc_ = line_orig(linesLeft[0],depthFrameColor.shape[1],depthFrameColor.shape[0])
            print(line_orig(linesLeft[0],depthFrameColor.shape[1],depthFrameColor.shape[0]))
            frameLeftColor= cv2.cvtColor(inLeft, cv2.COLOR_GRAY2BGR)
            mll.draw_lines(frameLeftColor, linesLeft, (200, 20, 20), 3)
            # get depth at line origin
            # equation is ax+by+c = 0
            # and show the origin as a circle
            ptc = ptc_
            #ptc = (int(linesLeft[0][0]),int(linesLeft[0][1]))
            topLeft.x = ptc[0]/depthFrameColor.shape[1]
            topLeft.y = ptc[1]/depthFrameColor.shape[0]
            bottomRight.x=topLeft.x+norm_marg # 0.1 
            bottomRight.y=topLeft.y+norm_marg # 0.1 
            #topLeft_ = (ptc[0]/depthFrameColor.shape[1],ptc[1]/depthFrameColor.shape[0])
            #bottomRight_ = topLeft_ + 0.1 #ptc[1]/depthFrameColor.shape[0]
            print(topLeft, bottomRight)
            #print(ptc)
            #print(f'nb detected lines = {len(linesLeft)}, specs: {linesLeft}, {linesLeft[0][0:1]}, { linesLeft[1][0:1]}')
            cv2.circle(frameLeftColor,ptc, 10, (0,0,255), -1)
            #cv2.circle(frameLeftColor,(447,63), 6, (0,0,255), -1)
            newConfig = True
            cv2.imshow('leftline', frameLeftColor)


        depthFrame = inDepth.getFrame() # depthFrame values are in millimeters

        depth_downscaled = depthFrame[::4]
        if np.all(depth_downscaled == 0):
            min_depth = 0  # Set a default minimum depth value when all elements are zero
        else:
            min_depth = np.percentile(depth_downscaled[depth_downscaled != 0], 1)
        max_depth = np.percentile(depth_downscaled, 99)
        depthFrameColor = np.interp(depthFrame, (min_depth, max_depth), (0, 255)).astype(np.uint8)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

        spatialData = spatialCalcQueue.get().getSpatialLocations()
        #print(len(spatialData))
        for depthData in spatialData:
            #print(f'in for {depthData}')
            roi = depthData.config.roi
            roi = roi.denormalize(width=depthFrameColor.shape[1], height=depthFrameColor.shape[0])
            xmin = int(roi.topLeft().x)
            ymin = int(roi.topLeft().y)
            xmax = int(roi.bottomRight().x)
            ymax = int(roi.bottomRight().y)

            depthMin = depthData.depthMin
            depthMax = depthData.depthMax

            fontType = cv2.FONT_HERSHEY_TRIPLEX
            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, 1)
            cv2.putText(depthFrameColor, f"X: {int(depthData.spatialCoordinates.x)} mm", (xmin + 10, ymin - 20), fontType, 0.5, color)
            cv2.putText(depthFrameColor, f"Y: {int(depthData.spatialCoordinates.y)} mm", (xmin + 10, ymin - 35), fontType, 0.5, color)
            cv2.putText(depthFrameColor, f"Z: {int(depthData.spatialCoordinates.z)} mm", (xmin + 10, ymin - 50), fontType, 0.5, color)
        # Show the frame
        cv2.imshow("depth", depthFrameColor)
        cv2.imshow("left", inLeft)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('w'):
            if topLeft.y - stepSize >= 0:
                topLeft.y -= stepSize
                bottomRight.y -= stepSize
                newConfig = True
        elif key == ord('a'):
            if topLeft.x - stepSize >= 0:
                topLeft.x -= stepSize
                bottomRight.x -= stepSize
                newConfig = True
        elif key == ord('s'):
            if bottomRight.y + stepSize <= 1:
                topLeft.y += stepSize
                bottomRight.y += stepSize
                newConfig = True
        elif key == ord('d'):
            if bottomRight.x + stepSize <= 1:
                topLeft.x += stepSize
                bottomRight.x += stepSize
                newConfig = True
        elif key == ord('1'):
            calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEAN
            print('Switching calculation algorithm to MEAN!')
            newConfig = True
        elif key == ord('2'):
            calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MIN
            print('Switching calculation algorithm to MIN!')
            newConfig = True
        elif key == ord('3'):
            calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MAX
            print('Switching calculation algorithm to MAX!')
            newConfig = True
        elif key == ord('4'):
            calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MODE
            print('Switching calculation algorithm to MODE!')
            newConfig = True
        elif key == ord('5'):
            calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
            print('Switching calculation algorithm to MEDIAN!')
            newConfig = True

        if newConfig:
            config.roi = dai.Rect(topLeft, bottomRight)
            config.calculationAlgorithm = calculationAlgorithm
            cfg = dai.SpatialLocationCalculatorConfig()
            cfg.addROI(config)
            spatialCalcConfigInQueue.send(cfg)
            newConfig = False
