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
import math

sys.path.insert(0, '/home/pi/Programs/warehouse_nav/lines_and_template')
# sys.path.insert(0, '/home/pi/Programs/warehouse_nav/lines_and_template')

import LSD_utils as mll

# compute the line origin at the image border
# takes a line_mll structure, size of image
# use a margin so that point is displayed (could be done outside)
def line_orig(line_mll,W,H):
    global marg_px
#    marg = marg_px # in pixels, attention to the equivalent in normlized points when setting the ROI
    a,b,c=line_mll[4],line_mll[5],line_mll[6]
    y=H - marg_px
    x = -1/a*(b*H+c)
    if x>W:
        # need to use the width
        x = W - marg_px
        y = -1/b*(a*W+c)
    if x<0:
        # need to set to 0 + margin
        x =  marg_px
        y = -1/b*(a*W+c)
    return np.asarray([int(x),int(y)])



show_dist = True # show distance to point (true) or x,y,z in world coordinates
show_lines = False
min_line_length = 150# min line length
#Create default parametrization LSD
lsd = cv2.createLineSegmentDetector(0)
stepSize = 0.05
marg_px = 50 # margin from image border, in pixels
norm_marg = (marg_px-1) / 640 # margin from image border, in units normalized to img size
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

#------------------------------
# define ROI for depth estimation
#------------------------------
spatialLocationCalculator.inputConfig.setWaitForMessage(False)
# ! these are in normalized point (0-1) -> (0-image width), same for height
if 0:
    topLeft_1 = dai.Point2f(0.921875, 0.6899999976158142)
    bottomRight_1 = dai.Point2f(0.9984375238418579, 0.7665625214576721)
else:
    topLeft_1 = dai.Point2f(0.2, 0.2)
    bottomRight_1 = dai.Point2f(0.3, 0.3)
config = dai.SpatialLocationCalculatorConfigData()
config.depthThresholds.lowerThreshold = 100
config.depthThresholds.upperThreshold = 10000
calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
config.roi = dai.Rect(topLeft_1, bottomRight_1)
spatialLocationCalculator.initialConfig.addROI(config)

spatialLocationCalculator.inputConfig.setWaitForMessage(False)
spatialLocationCalculator.initialConfig.addROI(config)
# add a second ROI for test
topLeft_2 = dai.Point2f(0.7828125, 0.4975000262260437)
bottomRight_2 = dai.Point2f(0.8593750238418579, 0.5740625500679016)
config = dai.SpatialLocationCalculatorConfigData()
config.depthThresholds.lowerThreshold = 100
config.depthThresholds.upperThreshold = 10000
calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
config.roi = dai.Rect(topLeft_2, bottomRight_2)

spatialLocationCalculator.inputConfig.setWaitForMessage(False)
spatialLocationCalculator.initialConfig.addROI(config)

print(f'{topLeft_1,topLeft_2}, {bottomRight_1,bottomRight_2}')
#pouet
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
    colorR = (255, 0, 0)

    print("Use WASD keys to move ROI!")

    while True:
        #linesLeft =  None
        inLeft = leftQueue.get().getCvFrame()
        inDepth = depthQueue.get() # Blocking call, will wait until a new data has arrived
        linesLeft = lsd.detect(inLeft)[0] 
        linesLeft = mll.from_lsd(linesLeft)

        # filter out the short segments
        linesLeft = linesLeft[linesLeft[...,7] > min_line_length]
        if len(linesLeft) > 3: # is not None:
            ptc_1 = line_orig(linesLeft[0],depthFrameColor.shape[1],depthFrameColor.shape[0])
            ptc_2 = line_orig(linesLeft[2],depthFrameColor.shape[1],depthFrameColor.shape[0])
            print(f'ptc_1 = {ptc_1}, ptc_2 = {ptc_2}')
            frameLeftColor= cv2.cvtColor(inLeft, cv2.COLOR_GRAY2BGR)
            mll.draw_lines(frameLeftColor, linesLeft, (200, 20, 20), 3)
            # get depth at line origin
            # equation is ax+by+c = 0
            # and show the origin as a circle
            ptc = ptc_1
            ptc[0] = ptc[0] - marg_px/2
            ptc[1] = ptc[1] - marg_px/2
            #ptc = (int(linesLeft[0][0]),int(linesLeft[0][1]))
            topLeft_1.x = ptc[0]/depthFrameColor.shape[1]
            topLeft_1.y = ptc[1]/depthFrameColor.shape[0]
            bottomRight_1.x=topLeft_1.x+norm_marg # 0.1 
            bottomRight_1.y=topLeft_1.y+norm_marg # 0.1 
            print(f'{topLeft_1.x,topLeft_1.y}, {bottomRight_1.x,bottomRight_1.y}')
            cv2.circle(frameLeftColor,ptc, 10, (0,0,255), -1)

            # repeat for the other point TODO: loop
            ptc = ptc_2
            ptc[0] = ptc[0] - marg_px/2
            ptc[1] = ptc[1] - marg_px/2
            topLeft_2.x = ptc[0]/depthFrameColor.shape[1]
            topLeft_2.y = ptc[1]/depthFrameColor.shape[0]
            bottomRight_2.x=topLeft_2.x+norm_marg # 0.1 
            bottomRight_2.y=topLeft_2.y+norm_marg # 0.1 
            print(f'topl_2 {topLeft_2.x,topLeft_2.y}, {bottomRight_2.x,bottomRight_2.y}')
            cv2.circle(frameLeftColor,ptc, 10, (0,255,0), -1)
            newConfig = True
            #newConfig = False # True
            cv2.imshow('leftline', frameLeftColor)


        depthFrame = inDepth.getFrame() # depthFrame values are in millimeters
        W = depthFrame.shape[1]
        H = depthFrame.shape[0]

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

            xtxt = xmin -10 if xmin > W/2 else (xmin + 10)
            ytxt = ymin -10 if ymin > H/2 else (ymin + 10)

            depthMin = depthData.depthMin
            depthMax = depthData.depthMax

            coords = depthData.spatialCoordinates
            distance = math.sqrt(coords.x ** 2 + coords.y ** 2 + coords.z ** 2)
            fontType = cv2.FONT_HERSHEY_TRIPLEX
            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, 1)
            if show_dist:
                cv2.putText(depthFrameColor, f"{distance/1000:.2f}m", (xtxt,ytxt), fontType, 0.5, color)
            else:
                cv2.putText(depthFrameColor, f"X: {int(depthData.spatialCoordinates.x)} mm", (xtxt,ytxt), fontType, 0.5, color)
                cv2.putText(depthFrameColor, f"Y: {int(depthData.spatialCoordinates.y)} mm", (xtxt,ytxt + 15), fontType, 0.5, color)
                cv2.putText(depthFrameColor, f"Z: {int(depthData.spatialCoordinates.z)} mm", (xtxt,ytxt + 30), fontType, 0.5, color)
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

        # update the roi for depth calculation, etc...
        if newConfig:
            config.roi = dai.Rect(topLeft_1, bottomRight_1)
            config.calculationAlgorithm = calculationAlgorithm
            cfg = dai.SpatialLocationCalculatorConfig()
            cfg.addROI(config)
            config.roi = dai.Rect(topLeft_2, bottomRight_2)
            config.calculationAlgorithm = calculationAlgorithm
            cfg = dai.SpatialLocationCalculatorConfig()
            cfg.addROI(config)
            spatialCalcConfigInQueue.send(cfg)
            if 0: 
                config.roi = dai.Rect(topLeft_1, bottomRight_1)
                cfg = dai.SpatialLocationCalculatorConfig()
                cfg.addROI(config)
                #config.roi = dai.Rect(topLeft_2, bottomRight_2)
                #cfg = dai.SpatialLocationCalculatorConfig()
                #cfg.addROI(config)
                #spatialCalcConfigInQueue.send(cfg)
            newConfig = False
