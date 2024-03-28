# get the imu part number
# (different OAK-D have different onboard IMU)
# example :
# $ py get_imu_part_number.py 
# IMU type: BNO086, firmware version: 3.9.9

import depthai as dai
import time
import math

device = dai.Device()

imuType = device.getConnectedIMU()
imuFirmwareVersion = device.getIMUFirmwareVersion()
print(f"IMU type: {imuType}, firmware version: {imuFirmwareVersion}")
