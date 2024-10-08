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

sys.path.insert(0, '/home/ludofw/mygitrepos/opencv2know/line_detection/frezza_supelec')

import LSD_utils as mll

# compute the line origin at the image border
# takes a line_mll structure, size of image
# use a margin so that point is displayed (could be done outside)
# find line extrimities
# return 2 points
def line_extremities(line_mll,W,H):
    global marg_px
    lext_1 = np.array([0,0])
    lext_2 = np.array([0,0])
#    marg = marg_px # in pixels, attention to the equivalent in normlized points when setting the ROI
    a,b,c=line_mll[4],line_mll[5],line_mll[6]
    if a != 0:
        y1= marg_px
        x1 = -1/a*(b*y1+c)
        if x1<marg_px:
            # need to set to 0 + margin
            x1 =  marg_px
            y1 = -1/b*(a*x1+c)
        elif x1>(W-marg_px):
            # need to use the width
            x1 = W - marg_px
            y1 = -1/b*(a*x1+c)
        y2=H - marg_px
        x2 = -1/a*(b*y2+c)
        if x2<marg_px:
            # need to set to 0 + margin
            x2 =  marg_px
            y2 = -1/b*(a*x2+c)
        elif x2>(W-marg_px):
            # need to use the width
            x2 = W - marg_px
            y2 = -1/b*(a*x2+c)
    else: # horizontal line
        x1 = marg_px
        y1 = -c/b
        x2 = W - marg_px
        y2 = -c/b

    lext_1 = [int(x1),int(y1)]
    lext_2 = [int(x2),int(y2)]
    if 1:
        print(f'line extrimities = {lext_1,lext_2}')
    return lext_1,lext_2

def line_orig(line_mll,W,H):
    global marg_px
#    marg = marg_px # in pixels, attention to the equivalent in normlized points when setting the ROI
    a,b,c=line_mll[4],line_mll[5],line_mll[6]
    y=H - marg_px
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
marg_px = 30 # margin from image border, in pixels
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
nb_roi = 4
ptc = np.zeros((nb_roi,2),dtype=np.int64)
roi_pts2f = [] # empty list of dai.Point2f
roi_br_pts2f = [] # empty list of dai.Point2f
# initialize all n ROI to same location (image center or other)
pt_tl = dai.Point2f(0.2, 0.2)
roi_norm_wh = 0.1 # normalized roi width and height
pt_br = dai.Point2f(0.3, 0.3)
if 0:
    topLeft_1 = dai.Point2f(0.921875, 0.6899999976158142)
    bottomRight_1 = dai.Point2f(0.9984375238418579, 0.7665625214576721)
else:
    for i in range(nb_roi):
#        pt = dai.Point2f()
#        pt.x, pt.y = p[0], p[1]
        roi_pts2f.append(dai.Point2f(0.1+i*0.01,0.1+2*i*0.01))
        roi_br_pts2f.append(dai.Point2f(0.2+i*0.01,0.2+2*i*0.01))
        #roi_pts2f.append(pt_tl)
        #roi_br_pts2f.append(pt_br)
        print(f'{roi_pts2f[i], roi_br_pts2f[i]}')
        config = dai.SpatialLocationCalculatorConfigData()
        config.depthThresholds.lowerThreshold = 100
        config.depthThresholds.upperThreshold = 10000
        calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
        config.roi = dai.Rect(roi_pts2f[i], roi_br_pts2f[i])
        spatialLocationCalculator.initialConfig.addROI(config)
for i in range(nb_roi):
    print(f'{roi_pts2f[i], roi_br_pts2f[i]}')
#spatialLocationCalculator.inputConfig.setWaitForMessage(False)
#spatialLocationCalculator.initialConfig.addROI(config)
## add a second ROI for test
#topLeft_2 = dai.Point2f(0.7828125, 0.4975000262260437)
#bottomRight_2 = dai.Point2f(0.8593750238418579, 0.5740625500679016)
#config = dai.SpatialLocationCalculatorConfigData()
#config.depthThresholds.lowerThreshold = 100
#config.depthThresholds.upperThreshold = 10000
#calculationAlgorithm = dai.SpatialLocationCalculatorAlgorithm.MEDIAN
#config.roi = dai.Rect(topLeft_2, bottomRight_2)
#
#spatialLocationCalculator.inputConfig.setWaitForMessage(False)
#spatialLocationCalculator.initialConfig.addROI(config)

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


    while True:
        #linesLeft =  None
        inLeft = leftQueue.get().getCvFrame()
        inDepth = depthQueue.get() # Blocking call, will wait until a new data has arrived
        linesLeft = lsd.detect(inLeft)[0] 
        linesLeft = mll.from_lsd(linesLeft)

        # filter out the short segments
        linesLeft = linesLeft[linesLeft[...,7] > min_line_length]
        frameLeftColor= cv2.cvtColor(inLeft, cv2.COLOR_GRAY2BGR)
        #print(f'nb of lines detected: {len(linesLeft)}') # is not None:
        if len(linesLeft) > 3: # is not None:
            for i in range(nb_roi):
                #ptc_= line_orig(linesLeft[i],depthFrameColor.shape[1],depthFrameColor.shape[0])
                ptc_,_= line_extremities(linesLeft[i],depthFrameColor.shape[1],depthFrameColor.shape[0])
                #print(f'ptc_ dtype = {ptc_.dtype,type(ptc_)} ptc_ = {ptc_}')
                #print(f'ptc dtype = {ptc.dtype,type(ptc)} ptc = {ptc,ptc[i]}')
                ptc[i][0]=ptc_[0]
                ptc[i][1]=ptc_[1]
                #print(f'ptc[{i}] = {ptc[i]}')
                # get depth at line origin
                # equation is ax+by+c = 0
                # and show the origin as a circle
                ptc[i][0] = ptc[i][0] - marg_px/2
                ptc[i][1] = ptc[i][1] - marg_px/2
                #ptc = (int(linesLeft[0][0]),int(linesLeft[0][1]))
                roi_pts2f[i].x = ptc[i][0]/depthFrameColor.shape[1]
                roi_pts2f[i].y = ptc[i][1]/depthFrameColor.shape[0]
                roi_br_pts2f[i].x=roi_pts2f[i].x+norm_marg # 0.1 
                roi_br_pts2f[i].y=roi_pts2f[i].y+norm_marg # 0.1 
                #print(f'{roi_pts2f[i].x,roi_pts2f[i].y}, {roi_br_pts2f[i].x,roi_br_pts2f[i].y}')
                cv2.circle(frameLeftColor,ptc_, 10, (0,0,255), -1)
                #cv2.circle(frameLeftColor,ptc[i], 10, (0,0,255), -1)
            mll.draw_lines(frameLeftColor, linesLeft, (200, 20, 20), 3)

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
        print(f'nb of roi detected: {len(spatialData)}')
        for depthData in spatialData:
            #print(f'in for {depthData}')
            roi = depthData.config.roi
            roi = roi.denormalize(width=depthFrameColor.shape[1], height=depthFrameColor.shape[0])
            print(f'roi = {roi}')
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
            #print(f'rect: {xmin,ymin} and {xmax,ymax}')
            cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, 1)
            if show_dist:
                cv2.putText(depthFrameColor, f"{distance/1000:.2f}m", (xtxt,ytxt), fontType, 0.5, color)
                cv2.putText(frameLeftColor, f"{distance/1000:.2f}m", (xtxt,ytxt), fontType, 0.5, color)
            else:
                cv2.putText(depthFrameColor, f"X: {int(depthData.spatialCoordinates.x)} mm", (xtxt,ytxt), fontType, 0.5, color)
                cv2.putText(depthFrameColor, f"Y: {int(depthData.spatialCoordinates.y)} mm", (xtxt,ytxt + 15), fontType, 0.5, color)
                cv2.putText(depthFrameColor, f"Z: {int(depthData.spatialCoordinates.z)} mm", (xtxt,ytxt + 30), fontType, 0.5, color)
        # Show the frame
        cv2.imshow("depth", depthFrameColor)
        cv2.imshow('leftline', frameLeftColor)
        #cv2.imshow("left", inLeft)

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
            print('new config')
            cfg = dai.SpatialLocationCalculatorConfig()
            for i in range(nb_roi):
                #print(f'{roi_pts2f[i], roi_br_pts2f[i]}')
                #print(f'{roi_pts2f[i].x, roi_pts2f[i].y}')
                #print(f'{roi_br_pts2f[i].x, roi_br_pts2f[i].y}')
                config.roi = dai.Rect(roi_pts2f[i], roi_br_pts2f[i])
                config.calculationAlgorithm = calculationAlgorithm
                cfg.addROI(config)
                spatialCalcConfigInQueue.send(cfg)
            for i in range(0): #nb_roi):
                #print(f'{roi_pts2f[i], roi_br_pts2f[i]}')
                #print(f'{roi_pts2f[i].x, roi_pts2f[i].y}')
                #print(f'{roi_br_pts2f[i].x, roi_br_pts2f[i].y}')
                config.roi = dai.Rect(roi_pts2f[i], roi_br_pts2f[i])
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
