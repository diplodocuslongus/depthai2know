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

I also installed depthai_sdk from pip, after installing the latest depthai with the method above.

    pip install depthai_sdk

Note that the depthai_sdk from pip had uninstalled my current depthai (2.25 for me) and install 2.22 instead, but upon upgrade (uninstall and reinstall with the method above) there didn't seem to have been any uninstall of the just installed depthai.

Upgrade:

    workon depthai
    pip list # depthai 2.28
    pip install --upgrade pip
    pip uninstall depthai
    python3 -m pip install --extra-index-url https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/ depthai # this installed 2.29
    pip install depthai_sdk # installed 1.15 on the sys76



Install depthai_sdk from source may work.

build the library locally (from depthai repo for depthai_sdk and depthai-python repo for depthai library)

(ref this post: https://discuss.luxonis.com/d/2030)
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

## bootloader update

Upon running the utility cam_test.py I had:

    [14442C10F13EE7D600] [1.2] Flashed bootloader version 0.0.22, less than 0.0.28 is susceptible to bootup/restart failure. Upgrading is advised, flashing main/factory 

So I flashed the bootloader using the py device_manager.py utility (in depthai-python/utilities)

- run py device_manager.py
- select the device from the drop down menu
- go to "danger zone"
- flash factory bootloader (select AUTO)

Bootloader correctly updated to 0.0.28

But i had a problem right after the upload:

     py cam_test.py
    DepthAI version: 2.29.0.0
    DepthAI path: /home/ludos7/.virtualenvs/depthai/lib/python3.10/site-packages/depthai.cpython-310-x86_64-linux-gnu.so
    Traceback (most recent call last):
      File "/home/ludos7/Programs/othergitrepos/ComputerVision/Luxonis_depthai/depthai-python/utilities/cam_test.py", line 257, in <module>
        with dai.Device(*dai_device_args) as device:
    RuntimeError: Device already closed or disconnected: Input/output error

I reflashed the bootloader, pressed the button closest to the usb connector and it seem to work.

May be a USB cable issue, or camera cable issue... as it worked then stopped with:

    Cam:      camb          camc     [host | capture timestamp]
    FPS:  19.37| 19.56  19.64| 19.56 Communication exception - possible device error/misconfiguration. Original message 'Couldn't read data from stream: 'camb' (X_LINK_ERROR)'
    Exiting cleanly


then crashed...

Also had to install PySimpleGUI to be able to run the device_manager:

    python -m pip uninstall PySimpleGUI
    python -m pip cache purge
    (depthai) gonze:utilities/ (main) $  pip install --upgrade --extra-index-url https://PySimpleGUI.net/install PySimpleGUI


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

