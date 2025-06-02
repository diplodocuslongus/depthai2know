#!/usr/bin/env python3

# Chobits' script to capture images and IMU from oak-d to follow EuRoC format
import cv2
import depthai as dai
import time
import math
import csv
import pathlib
import numpy as np
import threading, time

gogogo = True
l_img = None
l_ts = 0
r_img = None
r_ts = 0

# path2dataset='/home/ludofw/Data/Drones'
path2dataset='/mnt/Data_3TB/Data/Datasets/Kalibr/oakd_lite_IMU_cam'

def save_png():
    global l_img
    global r_img
    while gogogo:
        if l_img is not None:
            cv2.imwrite(f"{path2dataset}/oakd_lite/mav0/cam0/data/{l_ts}.png", l_img)
            l_img = None
        if r_img is not None:
            cv2.imwrite(f"{path2dataset}/oakd_lite/mav0/cam1/data/{r_ts}.png", r_img)
            r_img = None
        time.sleep(0.0001)

pathlib.Path(path2dataset+"/oakd_lite/mav0/imu0").mkdir(parents=True, exist_ok=True)
pathlib.Path(path2dataset+"/oakd_lite/mav0/cam0/data").mkdir(parents=True, exist_ok=True)
pathlib.Path(path2dataset+"/oakd_lite/mav0/cam1/data").mkdir(parents=True, exist_ok=True)

fs = cv2.FileStorage("q250_imu_cali.yml", cv2.FILE_STORAGE_READ)
acc_misalign = fs.getNode("acc_misalign").mat()
acc_bias = fs.getNode("acc_bias").mat()
acc_scale = fs.getNode("acc_scale").mat()
gyro_misalign = fs.getNode("gyro_misalign").mat()
gyro_scale = fs.getNode("gyro_scale").mat()
gyro_bias = fs.getNode("gyro_bias").mat()
acc_cor =  acc_misalign @ acc_scale
gyro_cor = gyro_misalign @ gyro_scale
fs.release()

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
imu = pipeline.create(dai.node.IMU)
xout_imu = pipeline.create(dai.node.XLinkOut)
monoLeft = pipeline.create(dai.node.MonoCamera)
xoutLeft = pipeline.create(dai.node.XLinkOut)
monoRight = pipeline.create(dai.node.MonoCamera)
xoutRight = pipeline.create(dai.node.XLinkOut)

xout_imu.setStreamName("imu")
xoutLeft.setStreamName("left")
xoutRight.setStreamName("right")

imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, 200)
imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, 200)
# it's recommended to set both setBatchReportThreshold and setMaxBatchReports to 20 when integrating in a pipeline with a lot of input/output connections
# above this threshold packets will be sent in batch of X, if the host is not blocked and USB bandwidth is available
imu.setBatchReportThreshold(5)
# maximum number of IMU packets in a batch, if it's reached device will block sending until host can receive it
# if lower or equal to batchReportThreshold then the sending is always blocking on device
# useful to reduce device's CPU load  and number of lost packets, if CPU load is high on device side due to multiple nodes
imu.setMaxBatchReports(10)
monoLeft.setCamera("left")
monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
monoLeft.setFps(20)
monoRight.setCamera("right")
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)
monoRight.setFps(20)

# Link plugins IMU -> XLINK
imu.out.link(xout_imu.input)
monoLeft.out.link(xoutLeft.input)
monoRight.out.link(xoutRight.input)

t_png = threading.Thread(target=save_png)
t_png.start()

# Pipeline is defined, now we can connect to the device
with dai.Device(pipeline) as device, open(path2dataset+'/oakd_lite/mav0/imu0/data.csv', 'w') as imu_file, open(path2dataset+'/oakd_lite/mav0/cam0/data.csv', 'w') as cam0_file, open(path2dataset+'/oakd_lite/mav0/cam1/data.csv', 'w') as cam1_file:
    print("capture started...")
    imu_writer = csv.writer(imu_file)
    cam0_writer = csv.writer(cam0_file)
    cam1_writer = csv.writer(cam1_file)
    # Output queue for imu bulk packets
    imuQueue = device.getOutputQueue(name="imu", maxSize=200, blocking=False)
    qLeft = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    qRight = device.getOutputQueue(name="right", maxSize=4, blocking=False)
    try:
        while True:
            queueName = device.getQueueEvent()
            if queueName == "imu":
                imuData = imuQueue.get()
                imuPackets = imuData.packets
                for imuPacket in imuPackets:
                    acceleroValues = imuPacket.acceleroMeter
                    gyroValues = imuPacket.gyroscope
                    acc_cali = acc_cor @ (np.array([[acceleroValues.x], [acceleroValues.y], [acceleroValues.z]]) - acc_bias)
                    gyro_cali = gyro_cor @ (np.array([[gyroValues.x], [gyroValues.y], [gyroValues.z]]) - gyro_bias)
                    # align with cam axis
                    imu_writer.writerow((int(acceleroValues.getTimestampDevice().total_seconds()*1e9), gyro_cali[0, 0], -gyro_cali[1, 0], -gyro_cali[2, 0], acc_cali[0, 0], -acc_cali[1, 0], -acc_cali[2, 0]))
            elif queueName == "left":
                inLeft = qLeft.get()
                l_ts = int(inLeft.getTimestampDevice().total_seconds()*1e9)
                l_img = inLeft.getFrame()
                # l_img = inLeft.getCvFrame()
                cam0_writer.writerow((l_ts, f"{l_ts}.png"))
                # cv2.imshow('left', l_img)
                # cv2.waitKey(10)
            elif queueName == "right":
                inRight = qRight.get()
                r_ts = int(inRight.getTimestampDevice().total_seconds()*1e9)
                r_img = inRight.getFrame()
                cam1_writer.writerow((r_ts, f"{r_ts}.png"))
    except KeyboardInterrupt:
        print("ctrl_c")
gogogo = False
t_png.join()
print("bye")

