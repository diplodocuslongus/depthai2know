#!/bin/bash

trap 'RET=$? ; echo -e >&2 "\n\x1b[31mFailed installing dependencies. Could be a bug in the installer or unsupported platform. Open a bug report over at https://github.com/luxonis/depthai - exited with status $RET at line $LINENO \x1b[0m\n" ;
exit $RET' ERR

readonly linux_pkgs=(
    python3
    python3-pip
    udev
    cmake
    git
    python3-numpy
)

readonly debian_pkgs=(
    ${linux_pkgs[@]}
    # https://docs.opencv.org/master/d7/d9f/tutorial_linux_install.html
    build-essential
    libgtk2.0-dev
    pkg-config
    libavcodec-dev
    libavformat-dev
    libswscale-dev
    python3-dev
    libtbb-dev
    libjpeg-dev
    libpng-dev
    libtiff-dev
    # https://stackoverflow.com/questions/55313610
    ffmpeg
    python3-venv
    libsm6
    libxext6
    python3-pyqt5
    python3-pyqt5.qtquick
    qml-module-qtquick-controls2
    qml-module-qt-labs-platform
    qtdeclarative5-dev
    qml-module-qtquick2
    qtbase5-dev
    qtchooser
    qt5-qmake
    qtbase5-dev-tools
    qml-module-qtquick-layouts
    qml-module-qtquick-window2
)

readonly debian_arm_pkgs=(
    ${linux_pkgs[@]}
    # https://docs.opencv.org/master/d7/d9f/tutorial_linux_install.html
    build-essential
    libgtk2.0-dev
    pkg-config
    libavcodec-dev
    libavformat-dev
    libswscale-dev
    python3-dev
    libtbb-dev
    libjpeg-dev
    libpng-dev
    libtiff-dev
    # https://stackoverflow.com/questions/55313610
    ffmpeg
    libsm6
    libxext6
    python3-pyqt5
    python3-pyqt5.qtquick
    qml-module-qtquick-controls2
    qml-module-qt-labs-platform
    qtdeclarative5-dev
    qml-module-qtquick2
    qtbase5-dev
    qtchooser
    qt5-qmake
    qtbase5-dev-tools
    qml-module-qtquick-layouts
    qml-module-qtquick-window2
    # https://stackoverflow.com/a/53402396/5494277
    libhdf5-dev
    libhdf5-dev
    libatlas-base-dev
    # https://github.com/EdjeElectronics/TensorFlow-Object-Detection-on-the-Raspberry-Pi/issues/18#issuecomment-433953426
    libilmbase-dev
    libopenexr-dev
    libgstreamer1.0-dev
)

readonly debian_pkgs_pre22_04=(
    libdc1394-dev
    libgl1-mesa-glx
    libtbb2malloc

)
readonly debian_pkgs_post22_04=(
    libdc1394-dev
    libgl1-mesa-glx
    libtbbmalloc2

)
readonly debian_pkgs_23=(
    libdc1394-dev
    libgl1-mesa-dev
    libtbbmalloc2
)


print_action () {
    green="\e[0;32m"
    reset="\e[0;0m"
    printf "\n$green >>$reset $*\n"
}
print_and_exec () {
    print_action $*
    $*
}

version_lte() {
    [[ "$1" == "$(echo -e "$1\n$2" | sort -V | head -n1)" ]]
}



# Function to lookup and print Debian version number
lookup_debian_version_number() {

  declare -A debian_versions=(
  ["trixie/sid"]="13"
  ["bookworm/sid"]="12"
  ["bullseye/sid"]="11"
  ["buster/sid"]="10"
)
debian_version_string="$1"
  version_number="${debian_versions[$debian_version_string]}"
  
  if [ -n "$version_number" ]; then
    echo "$version_number"
  else
    echo "None"
  fi
}

if [ -f /etc/os-release ]; then
    source /etc/os-release
    if [ -f /etc/debian_version ]; then
        output=$(cat /etc/debian_version)
        echo $output
        if [[ $output == *sid ]]; then
            version=$(lookup_debian_version_number $output)
        else 
            version=$output
        fi

        # Correctly determine if the architecture is ARM or aarch64
        IS_ARM=false
        if [[ $(uname -m) =~ ^arm* || $(uname -m) == "aarch64" ]]; then
            IS_ARM=true
        fi

        echo "$version"
        echo "$IS_ARM"

        if [ $IS_ARM ]; then
            sudo DEBIAN_FRONTEND=noninteractive apt install -y "${debian_arm_pkgs[@]}"
            if [[ $version == 13* ]]; then
                echo "Detected ARM Debian 13"
                sudo apt install -y "${debian_pkgs_23[@]}"
            elif version_lte "$version" "11.99"; then
                echo "Using pre-22.04 ARM package list"
                sudo apt install -y ${debian_pkgs_pre22_04[@]}

                # Check for uvcdynctrl package and recommend removal if found
                if dpkg -s uvcdynctrl &> /dev/null; then
                    echo -e "\033[33mWe detected 'uvcdynctrl' installed on your system.\033[0m"
                    # Instructions for removal
                    echo -e "\033[33m$ sudo apt remove uvcdynctrl uvcdynctrl-data\033[0m"
                    echo -e "\033[33m$ sudo rm -f /var/log/uvcdynctrl-udev.log\033[0m"
                fi


            else
                echo "Using post-22.04 ARM package list"
                sudo apt install -y ${debian_pkgs_post22_04[@]}
            fi

            # Add libjasper-dev for ARM but not aarch64
            [[ $(uname -m) =~ ^arm* ]] && { sudo apt install -y libjasper-dev; }

        else
            sudo DEBIAN_FRONTEND=noninteractive apt install -y "${debian_pkgs[@]}"
            if [[ $version == 13* ]]; then
                echo "Detected Debian 13"
                sudo apt install -y "${debian_pkgs_23[@]}"
            elif version_lte "$version" "11.99"; then
                echo "Using pre-22.04 package list"
                sudo apt install -y "${debian_pkgs_pre22_04[@]}"
                
            else
                echo "Using post-22.04 package list"
                sudo apt install -y "${debian_pkgs_post22_04[@]}"
            fi
        fi

        # Check for uvcdynctrl package and recommend removal if found
        if dpkg -s uvcdynctrl &> /dev/null; then
            echo -e "\033[33mWe detected 'uvcdynctrl' installed on your system.\033[0m"
            # Instructions for removal
            echo -e "\033[33m$ sudo apt remove uvcdynctrl uvcdynctrl-data\033[0m"
            echo -e "\033[33m$ sudo rm -f /var/log/uvcdynctrl-udev.log\033[0m"
        fi

        
            
        if [ "$VERSION_ID" == "21.04" ]; then
            echo -e "\033[33mThere are known issues with running our demo script on Ubuntu 21.04, due to package \"python3-pyqt5.sip\" not being in a correct version (>=12.9)\033[0m"
            echo -e "\033[33mWe recommend installing the updated version manually using the following commands\033[0m"
            echo -e "\033[33m$ wget http://mirrors.kernel.org/ubuntu/pool/universe/p/pyqt5-sip/python3-pyqt5.sip_12.9.0-1_amd64.deb\033[0m"
            echo -e "\033[33m$ sudo dpkg -i python3-pyqt5.sip_12.9.0-1_amd64.deb\033[0m"
            echo ""
        fi


    else
        echo "ERROR: Distribution not supported"
        exit 99
    fi
    # Allow all users to read and write to Myriad X devices
    echo "Installing udev rules..."
    echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | sudo tee /etc/udev/rules.d/80-movidius.rules > /dev/null
    sudo udevadm control --reload-rules && sudo udevadm trigger
else
    echo "ERROR: Host not supported"
    exit 99
fi

echo "Finished installing global libraries."
