import cv2
import depthai as dai
import numpy as np

# Create pipeline
pipeline = dai.Pipeline()

# Define nodes
left = pipeline.create(dai.node.MonoCamera)
right = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
feature_tracker = pipeline.create(dai.node.FeatureTracker)

xout_left = pipeline.create(dai.node.XLinkOut)
xout_right = pipeline.create(dai.node.XLinkOut)
xout_disparity = pipeline.create(dai.node.XLinkOut)
xout_features = pipeline.create(dai.node.XLinkOut)

# Set node properties
# left.setBoardSocket(dai.CameraBoardSocket.LEFT)
left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
left.setCamera("left")
# left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_X_720)
# right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
right.setCamera("left")
# right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_X_720)

stereo.initialConfig.setConfidenceThreshold(255)
stereo.initialConfig.setLeftRightCheck(True)
stereo.initialConfig.setSubpixel(False)

# Linking
left.out.link(stereo.left)
right.out.link(stereo.right)
stereo.syncedLeft.link(xout_left.input)
stereo.syncedRight.link(xout_right.input)
stereo.disparity.link(xout_disparity.input)

# FeatureTracker Linking
stereo.rectifiedLeft.link(feature_tracker.inputImage)
# feature_tracker.out.link(xout_features.input)
# feature_tracker.out.link(xout_features.input) # Corrected line
# feature_tracker.trackedFeatures.link(xout_features.input) # Corrected line

# XLinkOut properties
xout_left.setStreamName("left")
xout_right.setStreamName("right")
xout_disparity.setStreamName("disparity")
xout_features.setStreamName("features")

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    left_queue = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    right_queue = device.getOutputQueue(name="right", maxSize=4, blocking=False)
    disparity_queue = device.getOutputQueue(name="disparity", maxSize=4, blocking=False)
    features_queue = device.getOutputQueue(name="features", maxSize=4, blocking=False)

    while True:
        left_frame = left_queue.get().getCvFrame()
        right_frame = right_queue.get().getCvFrame()
        disparity_frame = disparity_queue.get().getCvFrame()
        features = features_queue.get().features

        # Normalize disparity for better visualization
        disparity_normalized = (disparity_frame * (255 / stereo.initialConfig.getMaxDisparity())).astype(np.uint8)

        # Draw features on the rectified left frame
        for feature in features:
            cv2.circle(left_frame, (int(feature.x), int(feature.y)), 3, (0, 255, 0), -1)

        # Display images
        cv2.imshow("Left", left_frame)
        cv2.imshow("Right", right_frame)
        cv2.imshow("Disparity", disparity_normalized)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
