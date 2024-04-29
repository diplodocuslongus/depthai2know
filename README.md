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

## IMU

### calibration


https://docs.luxonis.com/projects/api/en/latest/components/nodes/imu/


