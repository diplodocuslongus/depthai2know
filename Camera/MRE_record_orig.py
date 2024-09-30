import os

from depthai_sdk import OakCamera, RecordType
monoRes = '400p'
colorRes = '720p'

if __name__ == '__main__':
  record_dir = 'record_outputs'
  record_dir = os.path.abspath(record_dir)
  if not os.path.exists(record_dir):
    os.makedirs(record_dir, exist_ok=True)

  with OakCamera() as oak:
    color = oak.create_camera('color',
                              resolution=colorRes,
                              fps=30,
                              encode='H264')
    left = oak.create_camera('left', resolution=monoRes, fps=30, encode='H264')
    right = oak.create_camera('right',
                              resolution=monoRes,
                              fps=30,
                              encode='H264')
    depth = oak.create_stereo(resolution=colorRes,
                              fps=30,
                              left=left,
                              right=right)
    # Synchronize & save all (encoded) streams
    oak.record([
        color.out.encoded, left.out.encoded, right.out.encoded,
        # depth.out.encoded
    ], record_dir, RecordType.VIDEO)
    # Show color stream
    oak.visualize([color.out.camera, depth.out.main], scale=2 / 3, fps=True)
    print('recording')
    # Blocking is necessary
    oak.start(blocking=True)
