import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/pi/Programs/mygitrepos/depthai2know/ROS2/simple_vdo_pubsub/install/simple_mono_pubsub'
