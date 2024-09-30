import os

from depthai_sdk import OakCamera

if __name__ == '__main__':
  record_dir = 'record_outputs/1-19443010A1E7792700'
  record_dir = os.path.abspath(record_dir)

  with OakCamera(replay=record_dir) as oak:
    # Created CameraComponent/StereoComponent will use streams from the recording
    color = oak.create_camera('color',
                              resolution='1080P',
                              fps=30,
                              encode='H264')
    left = oak.create_camera('left', resolution='480P', fps=30, encode='H264')
    right = oak.create_camera('right',
                              resolution='480P',
                              fps=30,
                              encode='H264')
    depth = oak.create_stereo(resolution='480p',
                              fps=30,
                              left=left,
                              right=right)
    # Show color stream
    oak.visualize([color.out.camera, depth.out.main], scale=1 / 3, fps=True)
    # Blocking is necessary
    oak.start(blocking=True)
