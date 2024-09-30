order TODO

pip install depthai-sdk[record]

To record:
https://discuss.luxonis.com/d/1572-process-recorded-data-from-oak-d-without-access-to-oak-d/12
Go to depthai-sdk examples, the depthai -experiment example doesn't work

# depthai

## install on raspberry pi

Doc: https://docs.luxonis.com/projects/hardware/en/latest/pages/guides/raspberrypi/
Use the image with pre-installed depthai.

Download from this [google drive](https://drive.google.com/drive/folders/1O50jPpGj_82jkAokdrsG--k9OBQfMXK5)

File: RPi_64bit_OS.xz

    lsblk
    sudo umount /dev/sXXnb
    xzcat RPi_64bit_OS.xz | sudo dd of=/dev/sde status=progress bs=4M

Set up the wifi access:

in the rootfs partition, 

    sudo vi /media/$USER/rootfs/etc/wpa_supplicant/wpa_supplicant.conf

Add WLAN name and pwd.

Eject boot and rootfs, put the card in the pi, fire raspi-config, change the locals (keyboard, I used US international),  update, upgrade.


### To install on bare os:
https://docs.luxonis.com/projects/api/en/latest/install/#raspberry-pi-os

sudo curl -fL https://docs.luxonis.com/install_dependencies.sh | bash





## install on desktop

Install the python API.

Create a virtualenvironment.

then: 
python3 -m pip install --extra-index-url https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/ depthai

See:

https://pypi.org/project/depthai/

Note that the depthai_sdk from pip will uninstall the current depthai (2.25 for me) and install 2.22 instead.

Install depthai_sdk from source may work.

# OAK-D pro

## Camera

### Calibration

Clone depthai and cd inside.

(For example to a path at `othersgitrepos/ComputerVision/Luxonis_DepthAI/depthai`)

Then add the submodule, [info here](https://github.com/luxonis/depthai-calibration?tab=readme-ov-file) by running:

    git submodule update --init

Some info on the process [here](https://docs.luxonis.com/hardware/platform/calibration), see also [this](https://docs.luxonis.com/software/depthai/examples/calibration_load#calibration-load).

In particular, If you want to re-run the calibration process on the captured images, use the -m process argument:
Command Line

python3 calibrate.py -s [SQUARE_SIZE_IN_CM] --board [BOARD] -nx [squaresX] -ny [squaresY] -m process

Calibration results are stored inside the resources/ folder and can be used later for testing/debugging purposes. You can also load/flash this local calibration file to the device - see example for more details.
## IMU

### calibration


https://docs.luxonis.com/projects/api/en/latest/components/nodes/imu/

# OAK module aka OAK FFC (multiple camera)

Tested 20092024

    cd /$HOME/Programs/othersgitrepos/ComputerVision/Luxonis_DepthAI/depthai-python
    py utilities/cam_test.py

output:

Enabled cameras:
   camb : mono
   camc : mono
CAM:  camb
CAM:  camc
Connected cameras:
 -socket CAM_B : OV9282 1280 x  800 focus:fixed - MONO COLOR
 -socket CAM_C : OV9282 1280 x  800 focus:fixed - MONO COLOR
USB speed: SUPER
IR drivers: []


Plug 2 mono on CAMB2L and CAMC 2L
The 2L means 2 lanes, it's for mono camera.
If plug a mono cam on 4L port it will show in color but single color, red for the test I did.

Links:

https://github.com/luxonis/depthai-python/blob/main/utilities/cam_test.py

https://shop.luxonis.com/products/oak-ffc-4p

https://docs.luxonis.com/hardware/platform/deploy/ffc/
https://discuss.luxonis.com/d/2664-getting-started-with-oak-ffc-4p

