#!/usr/bin/env python3
# modif: simply removed the dependencie on depthai_sdk
# and removed all rgb frames
# from: https://github.com/luxonis/depthai-experiments/tree/master/gen2-syncing#imu--rgb--depth-timestamp-syncing
import cv2
import numpy as np
import depthai as dai
from datetime import timedelta

# Second slowest msg stream is stereo disparity, 45FPS -> ~22ms / 2 -> ~11ms
MS_THRESHOLD = 11

msgs = dict()

def add_msg(msg, name, ts = None):
    if ts is None:
        ts = msg.getTimestamp()

    if not name in msgs:
        msgs[name] = []

    msgs[name].append((ts, msg))

    synced = {}
    for name, arr in msgs.items():
        # Go through all stored messages and calculate the time difference to the target msg.
        # Then sort these msgs to find a msg that's closest to the target time, and check
        # whether it's below 17ms which is considered in-sync.
        diffs = []
        for i, (msg_ts, msg) in enumerate(arr):
            diffs.append(abs(msg_ts - ts))
        if len(diffs) == 0: break
        diffsSorted = diffs.copy()
        diffsSorted.sort()
        dif = diffsSorted[0]

        if dif < timedelta(milliseconds=MS_THRESHOLD):
            # print(f'Found synced {name} with ts {msg_ts}, target ts {ts}, diff {dif}, location {diffs.index(dif)}')
            # print(diffs)
            synced[name] = diffs.index(dif)


    if len(synced) == 2: # We have 2 synced msgs (IMU packet + disp )
        # print('--------\Synced msgs! Target ts', ts, )
        # Remove older msgs
        for name, i in synced.items():
            msgs[name] = msgs[name][i:]
        ret = {}
        for name, arr in msgs.items():
            ret[name] = arr.pop(0)
            # print(f'{name} msg ts: {ret[name][0]}, diff {abs(ts - ret[name][0]).microseconds / 1000}ms')
        return ret
    return False



# The disparity is computed at this resolution, then upscaled to RGB resolution
monoResolution = dai.MonoCameraProperties.SensorResolution.THE_720_P

def create_pipeline(device):
    pipeline = dai.Pipeline()

    calibData = device.readCalibration2()
    left = pipeline.create(dai.node.MonoCamera)
    left.setResolution(monoResolution)
    left.setBoardSocket(dai.CameraBoardSocket.LEFT)
    left.setFps(45)

    right = pipeline.create(dai.node.MonoCamera)
    right.setResolution(monoResolution)
    right.setBoardSocket(dai.CameraBoardSocket.RIGHT)
    right.setFps(45)

    stereo = pipeline.create(dai.node.StereoDepth)
    stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
    # LR-check is required for depth alignment
    stereo.setLeftRightCheck(True)
    #stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
    left.out.link(stereo.left)
    right.out.link(stereo.right)

    # Linking

    disparityOut = pipeline.create(dai.node.XLinkOut)
    disparityOut.setStreamName("disp")
    stereo.disparity.link(disparityOut.input)

    imu = pipeline.create(dai.node.IMU)
    imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, 360)
    imu.enableIMUSensor(dai.IMUSensor.GYROSCOPE_RAW, 360)
    imu.setBatchReportThreshold(10)
    imu.setMaxBatchReports(10)

    imuOut = pipeline.create(dai.node.XLinkOut)
    imuOut.setStreamName("imu")
    imu.out.link(imuOut.input)

    return pipeline


def td2ms(td) -> int:
    # Convert timedelta to milliseconds
    return int(td / timedelta(milliseconds=1))

# Connect to device and start pipeline
with dai.Device() as device:
    device.startPipeline(create_pipeline(device))

    def timeDeltaToMilliS(delta) -> float:
        return delta.total_seconds()*1000
    
    def new_msg(msg, name, ts=None):
        synced = add_msg(msg, name, ts)

        if not synced: return

        stereo_ts, disp = synced['disp']
        imuTs, imu = synced['imu']
        print(f"[Seq {disp.getSequenceNum()}] Mid of Stereo exposure ts: {td2ms(stereo_ts)}ms, Disparity ts: {td2ms(disp.getTimestampDevice())}ms, Stereo exposure time: {td2ms(disp.getExposureTime())}ms")
        print(f"[Seq {imu.acceleroMeter.sequence}] IMU ts: {td2ms(imuTs)}ms")
        print('-----------')


        frameDisp = disp.getFrame()
        maxDisparity = 95
        frameDisp = (frameDisp * 255. / maxDisparity).astype(np.uint8)

    imuF = "{:.06f}"
    tsF  = "{:.03f}"


    baseTs = None
    while True:
        for name in ['disp', 'imu']:
            msg = device.getOutputQueue(name).tryGet()
            if msg is not None:
                if name == 'imu':
                    for imuPacket in msg.packets:
                        imuPacket: dai.IMUPacket
                        acceleroValues = imuPacket.acceleroMeter
                        gyroValues = imuPacket.gyroscope

                        acceleroTs = acceleroValues.getTimestampDevice()
                        gyroTs = gyroValues.getTimestampDevice()
                        ts = imuPacket.acceleroMeter.getTimestampDevice()
                        new_msg(imuPacket, name, ts)
                        # change from gyro_accel_csv.py to match the synced ts format and order of magnitude
                        #if baseTs is None:
                        #    baseTs = acceleroTs if acceleroTs < gyroTs else gyroTs
                        acceleroTs = td2ms(acceleroTs)
                        gyroTs = td2ms(gyroTs)
                        #acceleroTs = timeDeltaToMilliS(acceleroTs - baseTs)
                        #gyroTs = timeDeltaToMilliS(gyroTs - baseTs)
                        print(f"Accelerometer timestamp: {tsF.format(acceleroTs)} ms")
                        print(f"Accelerometer [m/s^2]: x: {imuF.format(acceleroValues.x)} y: {imuF.format(acceleroValues.y)} z: {imuF.format(acceleroValues.z)}")
                        print(f"Gyroscope timestamp: {tsF.format(gyroTs)} ms")
                        print(f"Gyroscope [rad/s]: x: {imuF.format(gyroValues.x)} y: {imuF.format(gyroValues.y)} z: {imuF.format(gyroValues.z)} ")
                else:
                    msg: dai.ImgFrame
                    ts = msg.getTimestampDevice(dai.CameraExposureOffset.MIDDLE)
                    print(f"features  timestamp: {tsF.format(td2ms(ts))} ms")
                    #new_msg(msg, name, ts)
