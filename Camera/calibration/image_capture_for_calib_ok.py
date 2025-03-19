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

# path2saveimg = './calib_imgs/smalltarget'
path2saveimg = '/home/pi/Pictures'

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
            queueCAMS = device.getQueueEvent(('CAMB-2L','CAMC-2L'))
            # queueCAMS = device.getQueueEvents(('CAMB-2L','CAMC-2L'))
            # queueCAMB = device.getQueueEvents('CAMB-2L')
            # queueCAMC = device.getQueueEvents('CAMC-2L')
            messageCAMS = device.getOutputQueue(queueCAMS).tryGetAll()
            # print(f'messageCAMS = {messageCAMS}, type: {type(messageCAMS)}')
            for message in messageCAMS:
                if type(message) == dai.ImgFrame:
                    frame = message.getCvFrame()
                    ret, corners = cv2.findChessboardCorners(frame, (rows, columns), chessBoardFlags)
                    cv2.imshow(queueCAMS, frame)
             
                    if ret == True:
                    # if False: #ret == True:
                        conv_size = (11, 11)
                        corners = cv2.cornerSubPix(frame, corners, conv_size, (-1, -1), criteria)
                        result_image = frame
                        cv2.drawChessboardCorners(result_image, (rows,columns), corners, ret)
                        cv2.imshow(f'{queueCAMS}_det', result_image)

            # if type(messageCAMS) == dai.ImgFrame:
            #     cv2.imshow(queueCAMS, messageCAMS.getCvFrame())
            key = cv2.waitKey(waitms)
            if key == ord("q"):
                break # the big while loop
                    # key = cv2.waitKey(waitms)
                    # if key == ord("q"):
                    #     break # the big while loop
                    # elif key == ord("s"): # save image
                    #     print('saving images for calibration')
                    #     saveOAKim1_name = f'{path2saveimg}/oak_{queueCAMS}_{framei:04d}.png'
                    #     saveOAKim2_name = f'{path2saveimg}/oak_{queueCAMS}_{framei:04d}.png'
                    #     cv2.imwrite(saveOAKim1_name,frame)
                    #     framei += 1




            #     for message in messages:
            #         # Display arrived frames
            #         if type(message) == dai.ImgFrame:
            #             frame = message.getCvFrame()
            #             cv2.imshow(stream, frame)

                # Instead of get (blocking), we use tryGet (non-blocking) which will return the available data or None otherwise
            #     inLeft = qLeft.tryGet()
            #     inRight = qRight.tryGet()
            #     oak_frame_1 = inLeft.getCvFrame()
            #     oak_frame_2 = inRight.getCvFrame()

    '''
        # Create pipeline
        pipeline = dai.Pipeline()
        cams = device.getConnectedCameraFeatures()
        streams = []
        xout = {}
        for cam in cams:
            print(str(cam), str(cam.socket), cam.socket)
            # c = pipeline.create(dai.node.Camera)
            c = pipeline.createMonoCamera()
            c.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
            xout[cam] = pipeline.createXLinkOut()
            xout[cam].setStreamName(c)
            # x = pipeline.create(dai.node.XLinkOut)
            # c.preview.link(x.input)
            c.setBoardSocket(cam.socket)
            stream = str(cam.socket)
            if cam.name:
                stream = f'{cam.name} ({stream})'
            x.setStreamName(stream)
            streams.append(stream)

        # Start pipeline
        device.startPipeline(pipeline)
        # parameter for chessboard detection
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)
        rows = 6 
        columns = 9 
        #find the checkerboard
        chessBoardFlags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK
        while not device.isClosed():
            queueNames = device.getQueueEvents(streams)
            for stream in queueNames:
                messages = device.getOutputQueue(stream).tryGetAll()
                for message in messages:
                    # Display arrived frames
                    if type(message) == dai.ImgFrame:
                        frame = message.getCvFrame()
                        cv2.imshow(stream, frame)

                # Instead of get (blocking), we use tryGet (non-blocking) which will return the available data or None otherwise
            #     inLeft = qLeft.tryGet()
            #     inRight = qRight.tryGet()
            #     oak_frame_1 = inLeft.getCvFrame()
            #     oak_frame_2 = inRight.getCvFrame()
                # see if we can detect corners
                        # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
                        # checkerboard specs

                        ret, corners = cv2.findChessboardCorners(frame, (rows, columns), chessBoardFlags)
                        print(f'frame size: {frame.shape}')
                        # result_image = cv2.cvtColor(frame,cv2.COLOR_GRAY2BGR)
                 
                        if False: #ret == True:
                 
                            #Convolution size used to improve corner detection.
                            conv_size = (11, 11)
                 
                            corners = cv2.cornerSubPix(frame, corners, conv_size, (-1, -1), criteria)
                            cv2.drawChessboardCorners(result_image, (rows,columns), corners, ret)
                            # cv2.imshow('img', result_image)


                # oakimH,oakimW = oak_frame_1.shape
                # oak_frame_rgb = cv2.cvtColor(oak_frame,cv2.COLOR_GRAY2BGR)

                # im2show = np.concatenate((tof_im_rsz,oak_frame_rgb),axis=1)
                # cv2.imshow(winname_res, im2show)
            key = cv2.waitKey(waitms)
            if key == ord("q"):
                break # the big while loop
            if key == ord("p"): # 'p' will pause/resume the code.
                pause = not pause
                if pause: # pause is True
                    print("Code paused, 'p' to resume..")
                    while pause: # is True):
                        key = cv2.waitKey(30) & 0xff
                        if key == 112:
                            pause = False
                            print("Resume code")
                            break
            elif key == ord("s"): # save image
                print('saving images for calibration')
                saveOAK2name = f'{path2saveimg}/oak_frame{framei:04d}.png'
                # saveToF2name = f'{path2saveimg}/tof_frame{framei:04d}.png'

                # TODODO TODO flag for depth or confidence image or both
                cv2.imwrite(saveOAK2name,oak_frame)
                # cv2.imwrite(saveToF2name,confidence_img)
                # cv2.imwrite(saveToF2name,confidence_buf)
                # cv2.imwrite(saveToF2name,result_image)
                framei += 1



            if flag.exit():
                print('caught SIGINT, going to close the camera or video reader')

    '''


if __name__ == "__main__":
    main()
