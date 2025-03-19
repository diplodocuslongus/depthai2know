# capture oak camera images (RGB or mono) for camera calibration using a checkerboard

import cv2
import numpy as np
import depthai as dai
import sys
import os
from math import tan, pi,atan,degrees
import signal
import time
# this is optional, for reading offline videos
import argparse 
import itertools as itt

# https://stackoverflow.com/a/57649638/6358973
class GracefulExiter():

    def __init__(self):
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum, frame):
        print("exit flag set to True (repeat to exit now)")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit(self):
        return self.state

path2saveimg = './calib_imgs/smalltarget'
# path2saveimg = '/home/pi/Pictures'

winname_filt = None
winname_res = 'result'

def usage(argv0):
    print("Usage: python " + argv0 + " [options]")
    print("Available options are:")
    print(" -d        Choose the video to use")


def set_oak_camera(leftStr='CAMB-2L',rightStr='CAMC-2L'):
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and outputs
    monoLeft = pipeline.create(dai.node.MonoCamera)
    monoRight = pipeline.create(dai.node.MonoCamera)
    xoutLeft = pipeline.create(dai.node.XLinkOut)
    xoutRight = pipeline.create(dai.node.XLinkOut)

    # cams = dai.Device.getConnectedCameraFeatures()

    xoutLeft.setStreamName(leftStr)
    xoutRight.setStreamName(rightStr)


    # Properties
    # stream = str(cam.socket)
    # monoLeft.setCamera("left")
    monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setBoardSocket(dai.CameraBoardSocket.CAM_B)
    # monoRight.setCamera("right")
    monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoRight.setBoardSocket(dai.CameraBoardSocket.CAM_C)


    # Linking
    monoRight.out.link(xoutRight.input)
    monoLeft.out.link(xoutLeft.input)

    return pipeline


def main():
    framei = 0 # captured frame counter
    # set_oak_camera()
    oak_pipeline = set_oak_camera("CAMB-2L","CAMC-2L")
    # oak_device = dai.Device(oak_pipeline)
        # Output queues will be used to get the grayscale frames from the outputs defined above
    # qLeft = oak_device.getOutputQueue(name=leftStr, maxSize=4, blocking=False)
    # qRight = oak_device.getOutputQueue(name=rightStr, maxSize=4, blocking=False)

    print('done')
    flag = GracefulExiter()
    # decide here if read from video file or use camera
    inputvidfn = None #'/home/pi/Videos/warehouse/20250123/set4/out.mp4'
    inputimgfn = None #'/home/pi/Videos/warehouse/20250123/set4/out.mp4'
    argp = argparse.ArgumentParser()
    argp.add_argument('-i','--image',required = False,help='path to image')
    argp.add_argument('-v','--video',required = False,help='path to video')
    args = argp.parse_args()
    print(args.image, args.video)
    # cass
     
    black_color = (0, 0, 0)
    white_color = (255, 255, 255)

    lsd_oak = cv2.createLineSegmentDetector(0)


    # cv2.namedWindow(winname_res ,cv2.WINDOW_NORMAL)
    # cv2.resizeWindow(winname_res,480,360)
    # cv2.moveWindow(winname_res, 10,20) # doesn t work on wayland! , cd raspi forum (opencv movewindow won't move)
    if winname_filt is not None:
        cv2.namedWindow(winname_filt,cv2.WINDOW_NORMAL)
        cv2.resizeWindow(winname_filt,480,360)
    pause = False
    waitms = 10 # wait time for cvWaitKey, ! if too large will cause lag and issue with image capture with the OAK FFC
    # OAK camera
    # parameter for chessboard detection
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
    rows = 6 
    columns = 9 
    #find the checkerboard
    chessBoardFlags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK

    # Connect to device and start pipeline
    with dai.Device() as device:
        # Device name
        print('Device name:', device.getDeviceName())
        # Connected cameras
        print('Connected cameras:', device.getConnectedCameraFeatures())
        # Start pipeline
        device.startPipeline(oak_pipeline)
        # Clear queue events
        device.getQueueEvents()

        while not device.isClosed():
            # queueCAMS = device.getQueueEvent(('CAMB-2L','CAMC-2L'))
            # queueCAMS = device.getQueueEvents(('CAMB-2L','CAMC-2L'))
            queueCAMB = device.getQueueEvent(('CAMB-2L'))
            queueCAMC = device.getQueueEvent(('CAMC-2L'))
            # centerQueue = device.getOutputQueue(name='center', maxSize=4, blocking=False)
            # dispQueue = device.getOutputQueue(name='disparity', maxSize=4, blocking=False)
            messageCAMB = device.getOutputQueue(queueCAMB).tryGet()
            messageCAMC = device.getOutputQueue(queueCAMC).tryGet()
            # messageCAMS = device.getOutputQueue(queueCAMS).tryGetAll()
            # print(f'messageCAMS = {messageCAMS}, type: {type(messageCAMS)}')
            # print(f'messageCAMB = {messageCAMB}, type: {type(messageCAMB)}')
            if type(messageCAMB) == dai.ImgFrame:
                frameB = messageCAMB.getCvFrame()
                retB = False
                retB, corners = cv2.findChessboardCorners(frameB, (rows, columns), chessBoardFlags)
                if retB == True:
                    conv_size = (11, 11)
                    corners = cv2.cornerSubPix(frameB, corners, conv_size, (-1, -1), criteria)
                    result_image = cv2.cvtColor(frameB,cv2.COLOR_GRAY2BGR)
                    cv2.drawChessboardCorners(result_image, (rows,columns), corners, retB)
                    cv2.imshow(f'{queueCAMB}_det', result_image)

                cv2.imshow(queueCAMB, frameB)
         
            if type(messageCAMC) == dai.ImgFrame:
                frameC = messageCAMC.getCvFrame()
                retC = False
                retC, corners = cv2.findChessboardCorners(frameC, (rows, columns), chessBoardFlags)
                if retC == True:
                    conv_size = (11, 11)
                    corners = cv2.cornerSubPix(frameC, corners, conv_size, (-1, -1), criteria)
                    result_image = cv2.cvtColor(frameC,cv2.COLOR_GRAY2BGR)
                    cv2.drawChessboardCorners(result_image, (rows,columns), corners, retC)
                    cv2.imshow(f'{queueCAMC}_det', result_image)

                cv2.imshow(queueCAMC, frameC)
         
            key = cv2.waitKey(waitms)
            if key == ord("q"):
                break # the big while loop
            elif key == ord("s"): # save image
                print('saving images for calibration')
                saveOAKim1_name = f'{path2saveimg}/oak_{queueCAMB}_{framei:04d}.png'
                saveOAKim2_name = f'{path2saveimg}/oak_{queueCAMC}_{framei:04d}.png'
                cv2.imwrite(saveOAKim1_name,frameB)
                cv2.imwrite(saveOAKim2_name,frameC)
                framei += 1

            if flag.exit():
                print('caught SIGINT, going to close the camera or video reader')
if __name__ == "__main__":
    main()
