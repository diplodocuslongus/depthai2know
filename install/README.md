# depthai-core

This is the c++ API.

    git clone git@github.com:luxonis/depthai-core.git
    git submodule update --init --recursive


Build and install where depthai-core has been cloned (ex: `$HOME/builds/depthai`):

    cmake -S. -Bbuild
    cmake --build build --parallel 4
    cmake --build build --target install

or to specific location:

    cmake -S. -Bbuild -D'CMAKE_INSTALL_PREFIX=[path/to/install/dir]'

Build and install to /usr/local:


To install specify optional prefix and build target install

    cmake -S. -Bbuild -D'CMAKE_INSTALL_PREFIX=[path/to/install/dir]'
    cmake --build build --target install

If CMAKE_INSTALL_PREFIX isn't specified, the library is installed under build folder install.
Using:

Using:

call cmake with the path to where depthai has been installed:

    cmake -D'depthai_DIR=/home/ludos7/builds/depthai/depthai-core/build' ..




https://github.com/luxonis/depthai-core

# python (depthai)



sudo apt install python3-venv

mkvirtualenv depthai

install depthai then depthai-viewer

mkvirtualenv depthai
sudo wget -qO- https://docs.luxonis.com/install_dependencies.sh | bash
sudo apt install python3.10-venv
python3 -m pip install depthai
python3 -m pip install depthai-viewer
depthai-viewer 

workon depthai
I also did `pip install virtualenv` but before apt install python3.10-venv and it didn't work, i didn't uninstall virtualenv so not sure if this is needed.

ref: https://github.com/pypa/build/issues/224


