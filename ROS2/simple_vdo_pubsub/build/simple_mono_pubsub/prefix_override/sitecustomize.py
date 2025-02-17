import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/ludofw/mygitrepos/depthai2know/ROS2/simple_vdo_pubsub/install/simple_mono_pubsub'
