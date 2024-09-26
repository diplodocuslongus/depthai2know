#!/usr/bin/env python3
# align left image to disparity map, all in B&W
# based on rgb_depth_aligned and stereo_depth_video from the StereoDepth examples of depthai-python
# disparity map is aligned to the rectified right frame by default

import cv2
import numpy as np
import depthai as dai
import argparse

# Weights to use when blending depth/rgb image (should equal 1.0)
rgbWeight = 0.4
depthWeight = 0.6

parser = argparse.ArgumentParser()
parser.add_argument('-alpha', type=float, default=None, help="Alpha scaling parameter to increase float. [0,1] valid interval.")
args = parser.parse_args()
alpha = args.alpha

def updateBlendWeights(percent_rgb):
    """
    Update the rgb and depth weights used to blend depth/rgb image

    @param[in] percent_rgb The rgb weight expressed as a percentage (0..100)
    """
    global depthWeight
    global rgbWeight
    rgbWeight = float(percent_rgb)/100.0
    depthWeight = 1.0 - rgbWeight


fps = 30
# The disparity is computed at this resolution, then upscaled to RGB resolution
monoResolution = dai.MonoCameraProperties.SensorResolution.THE_400_P

# Create pipeline
pipeline = dai.Pipeline()
device = dai.Device()
queueNames = []

# Define sources and outputs
# camRgb = pipeline.create(dai.node.Camera)
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)

xoutLeft = pipeline.create(dai.node.XLinkOut)
xoutRight = pipeline.create(dai.node.XLinkOut)
#rgbOut = pipeline.create(dai.node.XLinkOut)
disparityOut = pipeline.create(dai.node.XLinkOut)

#rgbOut.setStreamName("rgb")
#queueNames.append("rgb")
xoutLeft.setStreamName("left")
queueNames.append("left")
xoutRight.setStreamName("right")
queueNames.append("right")
disparityOut.setStreamName("disp")
queueNames.append("disp")

#Properties
#rgbCamSocket = dai.CameraBoardSocket.CAM_A

#camRgb.setBoardSocket(rgbCamSocket)
#camRgb.setSize(1280, 720)
#camRgb.setFps(fps)

# For now, RGB needs fixed focus to properly align with depth.
# This value was used during calibration
#try:
#    calibData = device.readCalibration2()
#    lensPosition = calibData.getLensPosition(rgbCamSocket)
#    if lensPosition:
#        camRgb.initialControl.setManualFocus(lensPosition)
#except:
#    raise
left.setResolution(monoResolution)
left.setCamera("left")
left.setFps(fps)
right.setResolution(monoResolution)
right.setCamera("right")
right.setFps(fps)

stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
# LR-check is required for depth alignment
stereo.setLeftRightCheck(True)
print("before")
#stereo.setDepthAlign(right) # crashes here with incompatible arguments
print("after")
#stereo.setDepthAlign(rgbCamSocket)

# Linking
# camRgb.video.link(rgbOut.input)
left.out.link(stereo.left)
right.out.link(stereo.right)
stereo.syncedLeft.link(xoutLeft.input)
stereo.syncedRight.link(xoutRight.input)
stereo.disparity.link(disparityOut.input)

# camRgb.setMeshSource(dai.CameraProperties.WarpMeshSource.CALIBRATION)
if alpha is not None:
    # camRgb.setCalibrationAlpha(alpha)
    stereo.setAlphaScaling(alpha)

# Connect to device and start pipeline
with device:
    device.startPipeline(pipeline)

    frameRgb = None
    frameDisp = None

    # Configure windows; trackbar adjusts blending ratio of rgb/depth
    rgbWindowName = "mono"
    depthWindowName = "depth"
    blendedWindowName = "mono-depth"
    cv2.namedWindow(rgbWindowName)
    cv2.namedWindow(depthWindowName)
    cv2.namedWindow(blendedWindowName)
    cv2.createTrackbar('RGB Weight %', blendedWindowName, int(rgbWeight*100), 100, updateBlendWeights)
    print("output queue name: ")
    print(device.getOutputQueueNames)
    print("input queue name: ")
    print(device.getInputQueueNames)
    while True:
        latestPacket = {}
        latestPacket["left"] = None
        latestPacket["disp"] = None

        queueEvents = device.getQueueEvents(("left", "disp"))
        for queueName in queueEvents:
            packets = device.getOutputQueue(queueName).tryGetAll()
            if len(packets) > 0:
                latestPacket[queueName] = packets[-1]

        #if latestPacket["left"] is not None:
        #    frameRgb = latestPacket["left"].getCvFrame()
        #    # Optional, apply false colorization
        #    if 1: frameRgb = cv2.applyColorMap(frameRgb, cv2.COLORMAP_HOT)
        #    frameRgb = np.ascontiguousarray(frameRgb)
        #    cv2.imshow(rgbWindowName, frameRgb)

        if latestPacket["disp"] is not None:
            frameDisp = latestPacket["disp"].getFrame()
            maxDisparity = stereo.initialConfig.getMaxDisparity()
            # Optional, extend range 0..95 -> 0..255, for a better visualisation
            if 1: frameDisp = (frameDisp * 255. / maxDisparity).astype(np.uint8)
            # Optional, apply false colorization
            if 1: frameDisp = cv2.applyColorMap(frameDisp, cv2.COLORMAP_HOT)
            frameDisp = np.ascontiguousarray(frameDisp)
            cv2.imshow(depthWindowName, frameDisp)

        # Blend when both received
        if 0:
            if frameRgb is not None and frameDisp is not None:
                # Need to have both frames in BGR format before blending
                if len(frameDisp.shape) < 3:
                    frameDisp = cv2.cvtColor(frameDisp, cv2.COLOR_GRAY2BGR)
                blended = cv2.addWeighted(frameRgb, rgbWeight, frameDisp, depthWeight, 0)
                cv2.imshow(blendedWindowName, blended)
                frameRgb = None
                frameDisp = None

        if cv2.waitKey(1) == ord('q'):
            break
