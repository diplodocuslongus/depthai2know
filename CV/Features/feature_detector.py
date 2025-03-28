#!/usr/bin/env python3

# https://docs.luxonis.com/software/depthai/examples/feature_detector/

import cv2
import depthai as dai


# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
featureTrackerLeft = pipeline.create(dai.node.FeatureTracker)
featureTrackerRight = pipeline.create(dai.node.FeatureTracker)

xoutPassthroughFrameLeft = pipeline.create(dai.node.XLinkOut)
xoutTrackedFeaturesLeft = pipeline.create(dai.node.XLinkOut)
xoutPassthroughFrameRight = pipeline.create(dai.node.XLinkOut)
xoutTrackedFeaturesRight = pipeline.create(dai.node.XLinkOut)
xinTrackedFeaturesConfig = pipeline.create(dai.node.XLinkIn)

xoutPassthroughFrameLeft.setStreamName("passthroughFrameLeft")
xoutTrackedFeaturesLeft.setStreamName("trackedFeaturesLeft")
xoutPassthroughFrameRight.setStreamName("passthroughFrameRight")
xoutTrackedFeaturesRight.setStreamName("trackedFeaturesRight")
xinTrackedFeaturesConfig.setStreamName("trackedFeaturesConfig")

# Properties
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setCamera("left")
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setCamera("right")

# Disable optical flow
featureTrackerLeft.initialConfig.setMotionEstimator(False)
featureTrackerRight.initialConfig.setMotionEstimator(False)

# Linking
monoLeft.out.link(featureTrackerLeft.inputImage)
featureTrackerLeft.passthroughInputImage.link(xoutPassthroughFrameLeft.input)
featureTrackerLeft.outputFeatures.link(xoutTrackedFeaturesLeft.input)
xinTrackedFeaturesConfig.out.link(featureTrackerLeft.inputConfig)

monoRight.out.link(featureTrackerRight.inputImage)
featureTrackerRight.passthroughInputImage.link(xoutPassthroughFrameRight.input)
featureTrackerRight.outputFeatures.link(xoutTrackedFeaturesRight.input)
xinTrackedFeaturesConfig.out.link(featureTrackerRight.inputConfig)

featureTrackerConfig = featureTrackerRight.initialConfig.get()

print("Press 's' to switch between Harris and Shi-Thomasi corner detector!")

leftWindowName = "left"
rightWindowName = "right"
cv2.namedWindow(rightWindowName , cv2.WINDOW_NORMAL)
cv2.namedWindow(leftWindowName , cv2.WINDOW_NORMAL)
# cv2.setWindowProperty(rightWindowName , cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
# cv2.setWindowProperty(leftWindowName , cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queues used to receive the results
    passthroughImageLeftQueue = device.getOutputQueue("passthroughFrameLeft", 8, False)
    outputFeaturesLeftQueue = device.getOutputQueue("trackedFeaturesLeft", 8, False)
    passthroughImageRightQueue = device.getOutputQueue("passthroughFrameRight", 8, False)
    outputFeaturesRightQueue = device.getOutputQueue("trackedFeaturesRight", 8, False)

    inputFeatureTrackerConfigQueue = device.getInputQueue("trackedFeaturesConfig")

    def drawFeatures(frame, features):
        pointColor = (0, 255, 0)
        circleRadius = 3
        for feature in features:
            cv2.circle(frame, (int(feature.position.x), int(feature.position.y)), circleRadius, pointColor, -1, cv2.LINE_AA, 0)

    while True:
        inPassthroughFrameLeft = passthroughImageLeftQueue.get()
        passthroughFrameLeft = inPassthroughFrameLeft.getFrame()
        leftFrame = cv2.cvtColor(passthroughFrameLeft, cv2.COLOR_GRAY2BGR)

        inPassthroughFrameRight = passthroughImageRightQueue.get()
        passthroughFrameRight = inPassthroughFrameRight.getFrame()
        rightFrame = cv2.cvtColor(passthroughFrameRight, cv2.COLOR_GRAY2BGR)

        trackedFeaturesLeft = outputFeaturesLeftQueue.get().trackedFeatures
        drawFeatures(leftFrame, trackedFeaturesLeft)
        cv2.putText(leftFrame, str(len(trackedFeaturesLeft)), (10, 10), cv2.FONT_HERSHEY_PLAIN, 1.3, (0, 255, 0), thickness = 1, lineType=cv2.LINE_AA)

        print(f'nb left features {len(trackedFeaturesLeft)}')

        trackedFeaturesRight = outputFeaturesRightQueue.get().trackedFeatures
        cv2.putText(rightFrame, str(len(trackedFeaturesRight)), (10, 10), cv2.FONT_HERSHEY_PLAIN, 1.3, (0, 255, 0), thickness = 1, lineType=cv2.LINE_AA)
        drawFeatures(rightFrame, trackedFeaturesRight)

        # Show the frame
        cv2.imshow(leftWindowName, leftFrame)
        cv2.imshow(rightWindowName, rightFrame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            if featureTrackerConfig.cornerDetector.type == dai.FeatureTrackerConfig.CornerDetector.Type.HARRIS:
                featureTrackerConfig.cornerDetector.type = dai.FeatureTrackerConfig.CornerDetector.Type.SHI_THOMASI
                print("Switching to Shi-Thomasi")
            else:
                featureTrackerConfig.cornerDetector.type = dai.FeatureTrackerConfig.CornerDetector.Type.HARRIS
                print("Switching to Harris")

            cfg = dai.FeatureTrackerConfig()
            cfg.set(featureTrackerConfig)
            inputFeatureTrackerConfigQueue.send(cfg)

