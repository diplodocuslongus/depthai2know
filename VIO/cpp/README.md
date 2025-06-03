An utility record oak-d camera image and imu data in EuRoC dataset format

## 1. Prerequisites
### 1.1. **depthai-core**
Tested with 2.25.0
```
    git clone https://github.com/luxonis/depthai-core
    git submodule update --init --recursive
    cmake -S. -Bbuild
    cmake --build build --target install
```

### 1.2. **OpenCV**
Tested with 4.6
```
    sudo apt install libopencv-dev
```

## 2. Build
```
    cmake -D'depthai_DIR=../depthai-core/build/install/lib/cmake/depthai' .
    make
```

## 3. Run
```
    ./oakd_euroc IMU_TK_CALI.yml
