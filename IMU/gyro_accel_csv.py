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
# added system log TODO finish
# added: drone name (option), just set time as a string with any time unit (s,mn,hr), 
# check for directory, is not exisiting create it# adjust file name convention 

import os # for file manipulation
from pathlib import Path
import depthai as dai
import time
import math
import csv

def printSystemInformation(info):
    m = 1024 * 1024 # MiB
    print(f"Ddr used / total - {info.ddrMemoryUsage.used / m:.2f} / {info.ddrMemoryUsage.total / m:.2f} MiB")
    print(f"Cmx used / total - {info.cmxMemoryUsage.used / m:.2f} / {info.cmxMemoryUsage.total / m:.2f} MiB")
    print(f"LeonCss heap used / total - {info.leonCssMemoryUsage.used / m:.2f} / {info.leonCssMemoryUsage.total / m:.2f} MiB")
    print(f"LeonMss heap used / total - {info.leonMssMemoryUsage.used / m:.2f} / {info.leonMssMemoryUsage.total / m:.2f} MiB")
    t = info.chipTemperature
    print(f"Chip temperature - average: {t.average:.2f}, css: {t.css:.2f}, mss: {t.mss:.2f}, upa: {t.upa:.2f}, dss: {t.dss:.2f}")
    print(f"Cpu usage - Leon CSS: {info.leonCssCpuUsage.average * 100:.2f}%, Leon MSS: {info.leonMssCpuUsage.average * 100:.2f} %")
    print("----------------------------------------")

def logChipTemperature(info):
    t = info.chipTemperature
    print(f"Chip temperature - average: {t.average:.2f}, css: {t.css:.2f}, mss: {t.mss:.2f}, upa: {t.upa:.2f}, dss: {t.dss:.2f}")

#-----------------------------------
# parameters for the data collection
#-----------------------------------
# hardware / system setup information
hw_setup_idx = 0 # input idx corresponding to the current configuration below
HW_SETUP= {0:'Drone',1:'Cart',2:'Static',3:'BenchMotorOn',4:'Other',5:'',6:'',7:'',8:''}
# Drone / frame name (if applicable)
drone_frame_idx = 1
DRONE_FRAME= {0:'380mmFrame',1:'WarehouseFrame',2:'250mmFrame',3:'',4:'',5:'',6:'',7:'',8:''}
FLIGHT_MODE = 'Manual'
#FLIGHT_MODE = 'Loiter'
# imu orientation idx
# put in a dict for conveniently setting the output csv filename
# imuTK: for use with the imu Tool Kit (imu_tk)
# 'level' means the imu (or the frame in which the chip is mounted, e.g. the oak camera) is perfectly level; different from xDown where x points down but may not be perfectly level
imu_orient = 4
IMU_ORIENTATION = {0:'level',1:'xDown',2:'xUp',3:'xDown',4:'yUp',5:'yDown',6:'zUp',7:'zDown',8:'imuTK'}

if HW_SETUP[hw_setup_idx] == 'Drone':
    CONFIG_DESCRIPTION = f'{DRONE_FRAME[drone_frame_idx]}_Flight{FLIGHT_MODE}'
elif HW_SETUP[hw_setup_idx] == 'BenchMotorOn':
    CONFIG_DESCRIPTION = f'{DRONE_FRAME[drone_frame_idx]}_{IMU_ORIENTATION[imu_orient]}'
else:    
    CONFIG_DESCRIPTION = f'{HW_SETUP[hw_setup_idx]}_{IMU_ORIENTATION[imu_orient]}'

#OAK_NAME = 'OAKDPro'
OAK_NAME = 'OAKLight'
if OAK_NAME == 'OAKDPro':
    IMU_ACCEL_SR = 500 # frequency / sample rate of the accelerometer, in Hz
    #IMU_ACCEL_SR = 125 # frequency / sample rate of the accelerometer, in Hz
    IMU_GYRO_SR = 400 # frequency / sample rate of the gyro, in Hz
    #IMU_GYRO_SR = 100 # frequency / sample rate of the gyro, in Hz
    IMU_NAME = 'BNO086'
elif OAK_NAME == 'OAKLight':
    IMU_ACCEL_SR = 200 
    IMU_GYRO_SR = 200
    IMU_NAME = 'BMI270'

# total acquisition time
# new: simply write the time as a string, with units of s (seconds), mn (minute) or hr
# the proper total time in seconds will be automatically extracted from the string

TIME_STR = '2mn'
if 'hr' in TIME_STR:
    acq_time_hr = int(TIME_STR.split('hr')[0])
    ACQ_T = acq_time_hr*3600
    print(f'acquisition time in hour, that is {ACQ_T}s')
elif 'mn' in TIME_STR:
    acq_time_mn = int(TIME_STR.split('mn')[0])
    ACQ_T = acq_time_mn*60
    print(f'acquisition time in minute, that is {ACQ_T}s')
elif 's' in TIME_STR:
    acq_time_s = int(TIME_STR.split('s')[0])
    ACQ_T = acq_time_s
    print(f'acquisition time in second, that is {ACQ_T}s')

#ACQ_T_HR = 1.5 #0.1 #0.1 #1.5
#ACQ_T = ACQ_T_HR * 3600 # total acquisition time in seconds
#ACQ_T = 10 # total acquisition time in seconds
HOME = os.getenv("HOME")
N_SAMPLES = int(ACQ_T) * IMU_GYRO_SR
#N_SAMPLES = 10 #int(ACQ_T) * IMU_GYRO_SR
SHOW_DATA = False # show live data in terminal
LOG_CPU_TEMPERATURE = False
#if ACQ_T_HR > 1.0:
#    TIME_STR = f'{ACQ_T_HR}hr'
#else:
#    TIME_STR = f'{int(ACQ_T_HR*60)}mn'
#CSV_FILENAME = 'check'
# check if directory exists if not , create it.
if HW_SETUP[hw_setup_idx] == 'Drone':
    SUB_DIR = DRONE_FRAME[drone_frame_idx]
else:    
    SUB_DIR = HW_SETUP[hw_setup_idx]
DATA_PATH = f'{HOME}/Data/Drones/IMU/{SUB_DIR}'
Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
# built the full filename
if IMU_GYRO_SR == IMU_ACCEL_SR:
    CSV_FILENAME = f'{DATA_PATH}/{OAK_NAME}_{IMU_NAME}_{TIME_STR}_SR{IMU_GYRO_SR}_{CONFIG_DESCRIPTION}.csv'
else:
    CSV_FILENAME = f'{DATA_PATH}/{OAK_NAME}_{IMU_NAME}_{TIME_STR}_gyroSR{IMU_GYRO_SR}_accSR{IMU_ACCEL_SR}_{CONFIG_DESCRIPTION}.csv'
#CSV_FILENAME = f'{HOME}/Data/Drones/IMU/{OAK_NAME}_{IMU_NAME}_{TIME_STR}_gyroSR{IMU_GYRO_SR}_accSR{IMU_ACCEL_SR}_{IMU_ORIENTATION[imu_orient]}.csv'

print(f'saving csv to {CSV_FILENAME}')
pouet
# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
if LOG_CPU_TEMPERATURE:
    sysLog = pipeline.create(dai.node.SystemLogger)
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)

xlinkOut.setStreamName("imu")

# enable ACCELEROMETER_RAW at IMU_ACCEL_SR hz rate
if imu_orient == 8: # ('imuTK')
    ACQ_T = 20*4 # 50s idle, 40 orientation paused during at least 2s, 2s to move to new orientation
    #ACQ_T = 50+ 40*4 # 50s idle, 40 orientation paused during at least 2s, 2s to move to new orientation
    N_SAMPLES = int(ACQ_T) * IMU_GYRO_SR
    #print(N_SAMPLES)
    imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_ACCEL_SR)
    imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, IMU_GYRO_SR)
else:
    imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_ACCEL_SR)
    #imu.enableIMUSensor(dai.IMUSensor.LINEAR_ACCELERATION, IMU_ACCEL_SR)
    # enable GYROSCOPE_RAW at IMU_GYRO_SR hz rate
    imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, IMU_GYRO_SR)
    #imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_CALIBRATED, IMU_GYRO_SR)
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
    for k in range(N_SAMPLES):
    #for _ in range(N_SAMPLES):
        print(end=f"\r{(k+1)/N_SAMPLES*100:6.2f} %")
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
