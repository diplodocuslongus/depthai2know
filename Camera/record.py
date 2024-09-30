# see https://docs-old.luxonis.com/projects/sdk/en/latest/features/recording/

from depthai_sdk import OakCamera, RecordType

monoRes = '400p'
colorRes = '720p'

with OakCamera() as oak:
    color = oak.create_camera('color', resolution='1080P', fps=20, encode='H265')
    left = oak.create_camera('left', resolution=monoRes, fps=20, encode='H265')
    #left = oak.create_camera('left', resolution='800p', fps=20, encode='H265')
    right = oak.create_camera('right', resolution='800p', fps=20, encode='H265')

    # Synchronize & save all (encoded) streams
    oak.record([color.out.encoded, left.out.encoded, right.out.encoded], './', RecordType.VIDEO)
    # Show color stream
    oak.visualize([color.out.camera], scale=2/3, fps=True)
    print('recording')

    oak.start(blocking=True)
