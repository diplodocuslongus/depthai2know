#!/usr/bin/env python3
# saves imu data for further analysis (e.g. Allan variance)
# this is for the OAK-D pro, make sure to set the sample rate 
# corresponding to the IMU chip actually on board the OAK
# get it with e.g. get_imu_part_number
# data format
# accTs, accX, accY, accZ, gyrTs, gyrX, gyrY, gyrZ 
# Ts = time stamp 
# accX,...: component of raw accelerometer m/s^2
# gyrX,...: component of raw gyroscope, rad/s
# https://docs.luxonis.com/projects/api/en/latest/components/nodes/imu/
# added camera timestamp

import depthai as dai
import time
import math
import csv

# parameters for the data collection
ACQ_T_HR = 0.1 #1.5
#ACQ_T = 10 # total acquisition time in seconds
ACQ_T = ACQ_T_HR * 3600 # total acquisition time in seconds
#ACQ_T = 1.0 * 3600 # total acquisition time in seconds
IMU_ACCEL_SR = 500 # frequency / sample rate of the accelerometer, in Hz
#IMU_ACCEL_SR = 125 # frequency / sample rate of the accelerometer, in Hz
IMU_GYRO_SR = 400 # frequency / sample rate of the gyro, in Hz
#IMU_GYRO_SR = 100 # frequency / sample rate of the gyro, in Hz
N_SAMPLES = int(ACQ_T) * IMU_GYRO_SR
#N_SAMPLES = 10 #int(ACQ_T) * IMU_GYRO_SR
SHOW_DATA = False # show live data in terminal
# put the imu orientation in a dict for conveniently setting the output csv filename
IMU_ORIENTATION = {0:'level',1:'xUp',2:'xDown',3:'yUp',4:'yDown',5:'zUp',6:'zDown'}
CSV_FILENAME = f'oak_BNO086_{int(ACQ_T_HR*60)}mn_gyroSR{IMU_GYRO_SR}_accSR{IMU_ACCEL_SR}_{IMU_ORIENTATION[3]}.csv'
#CSV_FILENAME = '/home/ludofw/Data/Drones/IMU/imu_oak_BNO086_2hr_02042024.csv'
#CSV_FILENAME = '~/Data/Drones/IMU/imu_oak_BNO086_2hr_02042024.csv'

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)

xlinkOut.setStreamName("imu")

# enable ACCELEROMETER_RAW at IMU_ACCEL_SR hz rate
imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_ACCEL_SR)
# enable GYROSCOPE_RAW at IMU_GYRO_SR hz rate
imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, IMU_GYRO_SR)
# it's recommended to set both setBatchReportThreshold and setMaxBatchReports to 20 when integrating in a pipeline with a lot of input/output connections
# above this threshold packets will be sent in batch of X, if the host is not blocked and USB bandwidth is available
imu.setBatchReportThreshold(1)
# maximum number of IMU packets in a batch, if it's reached device will block sending until host can receive it
# if lower or equal to batchReportThreshold then the sending is always blocking on device
# useful to reduce device's CPU load  and number of lost packets, if CPU load is high on device side due to multiple nodes
imu.setMaxBatchReports(10)

# Link plugins IMU -> XLINK
imu.out.link(xlinkOut.input)

# Pipeline is defined, now we can connect to the device
with dai.Device(pipeline) as device, open(CSV_FILENAME, newline='', mode='w') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')

    def timeDeltaToMilliS(delta) -> float:
        return delta.total_seconds()*1000

    # Output queue for imu bulk packets
    imuQueue = device.getOutputQueue(name="imu", maxSize=50, blocking=False)
    baseTs = None
    #while True:
    for _ in range(N_SAMPLES):
        imuData = imuQueue.get()  # blocking call, will wait until a new data has arrived

        imuPackets = imuData.packets
        for imuPacket in imuPackets:
            acceleroValues = imuPacket.acceleroMeter
            gyroValues = imuPacket.gyroscope

            acceleroTs = acceleroValues.getTimestampDevice()
            gyroTs = gyroValues.getTimestampDevice()
            if baseTs is None:
                baseTs = acceleroTs if acceleroTs < gyroTs else gyroTs
            acceleroTs = timeDeltaToMilliS(acceleroTs - baseTs)
            gyroTs = timeDeltaToMilliS(gyroTs - baseTs)

            imuF = "{:.06f}"
            tsF  = "{:.03f}"
            imudatalist = [tsF.format(acceleroTs),
               imuF.format(acceleroValues.x),imuF.format(acceleroValues.y),imuF.format(acceleroValues.z),
               tsF.format(gyroTs),
               imuF.format(gyroValues.x),imuF.format(gyroValues.y),imuF.format(gyroValues.z)]
            csvwriter.writerow(imudatalist)

            if (SHOW_DATA):
                print(f"Accelerometer timestamp: {tsF.format(acceleroTs)} ms")
                print(f"Accelerometer [m/s^2]: x: {imuF.format(acceleroValues.x)} y: {imuF.format(acceleroValues.y)} z: {imuF.format(acceleroValues.z)}")
                print(f"Gyroscope timestamp: {tsF.format(gyroTs)} ms")
                print(f"Gyroscope [rad/s]: x: {imuF.format(gyroValues.x)} y: {imuF.format(gyroValues.y)} z: {imuF.format(gyroValues.z)} ")
