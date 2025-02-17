# note when working with a virtual environment

Ex, with the raspberrypi

Situation:
ros2 jazzy system wide installed (with apt)
depthai in a virtual environment.

ros2 run will complain python doesn't find depthai.

The solution is to add this line to setup.cfg file of your package
[build_scripts]
executable = /usr/bin/env python3

Source:
https://medium.com/ros2-tips-and-tricks/running-ros2-nodes-in-a-python-virtual-environment-b31c1b863cdb

Example can be seen in ./ROS2/simple_vdo_pubsub/src/simple_mono_pubsub
