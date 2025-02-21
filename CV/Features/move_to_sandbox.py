# seen https://discuss.luxonis.com/d/1854-reopen-camera-after-deviceclose-throws-segmentation-fault/7
# need pip install blobconverter
# see: https://github.com/luxonis/depthai-model-zoo/blob/main/README.md
import time
import depthai as dai
import blobconverter

def create_pipeline(depth):
    syncNN = True

    # Start defining a pipeline
    pipeline = dai.Pipeline()
    # pipeline.setOpenVINOVersion(version=dai.OpenVINO.Version.VERSION_2021_4)
    # Define a source - color camera
    colorCam = pipeline.create(dai.node.ColorCamera)

    # Define source and output for system info (temps/cpu)
    sysLog = pipeline.create(dai.node.SystemLogger)
    linkOut = pipeline.create(dai.node.XLinkOut)

    linkOut.setStreamName("sysinfo")

    # set system info pipeline to 1Hz sample rate
    sysLog.setRate(1)

    # Link
    sysLog.out.link(linkOut.input)

    if depth:
        mobilenet = pipeline.create(dai.node.MobileNetSpatialDetectionNetwork)
        monoLeft = pipeline.create(dai.node.MonoCamera)
        monoRight = pipeline.create(dai.node.MonoCamera)
        stereo = pipeline.create(dai.node.StereoDepth)
    else:
        mobilenet = pipeline.create(dai.node.MobileNetDetectionNetwork)

    colorCam.setPreviewSize(512, 512)
    colorCam.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    colorCam.setInterleaved(False)
    colorCam.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

    mobilenet.setBlobPath(blobconverter.from_zoo("person-vehicle-bike-detection-crossroad-1016", shaves=6, version="2022.1"))

    mobilenet.setConfidenceThreshold(0.5)
    mobilenet.input.setBlocking(False)

    if depth:
        monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
        monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        monoRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)

        # Setting node configs
        stereo.initialConfig.setConfidenceThreshold(255)
        stereo.depth.link(mobilenet.inputDepth)
        stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)

        mobilenet.setBoundingBoxScaleFactor(0.5)
        mobilenet.setDepthLowerThreshold(100)
        mobilenet.setDepthUpperThreshold(5000)

        monoLeft.out.link(stereo.left)
        monoRight.out.link(stereo.right)

    xoutRgb = pipeline.create(dai.node.XLinkOut)
    xoutRgb.setStreamName("rgb")
    colorCam.preview.link(mobilenet.input)

    if syncNN:
        mobilenet.passthrough.link(xoutRgb.input)
    else:
        colorCam.preview.link(xoutRgb.input)

    xoutNN = pipeline.create(dai.node.XLinkOut)
    xoutNN.setStreamName("detections")
    mobilenet.out.link(xoutNN.input)

    return pipeline

if __name__ == "__main__":

    while True:
        camera_device = dai.Device(create_pipeline(True))
        print("Initiating camera")
        # initiate camera and pipeline
        
        cams = camera_device.getConnectedCameras()
        
        depth_enabled = dai.CameraBoardSocket.CAM_B in cams and dai.CameraBoardSocket.CAM_C in cams
        # Start pipeline

        # Output queues will be used to get the rgb frames and nn data from the outputs defined above
        previewQueue = camera_device.getOutputQueue(name="rgb", maxSize=1, blocking=False)
        detectionNNQueue = camera_device.getOutputQueue(name="detections", maxSize=1, blocking=False)
        sysinfo_queue = camera_device.getOutputQueue(name="sysinfo", maxSize=1, blocking=False)

        frame = None
        detections = []
        frame_counter = 0
        color = (255, 255, 255)

        # camera loop
        print("Starting camera loop for 200 iterations")
        while frame_counter < 200:
            inPreview = previewQueue.get()
            frame_stereo = inPreview.getCvFrame()

            inNN = detectionNNQueue.get()
            detections = inNN.detections

            frame_counter += 1

        print("Closing camera")
        camera_device.close()

        time.sleep(10)
