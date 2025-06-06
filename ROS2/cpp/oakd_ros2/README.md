chobit's ros2 publisher 
publish mono and imu for kimera

build in build directory:

    $ cmake -Ddepthai_DIR=/home/rpikim/libs/depthai_core/lib/cmake/depthai ..

Run:

    $ ./oakd_ros2 ../q250_imu_cali.yml 

Check ros2 topics:

    ros2 topic list
