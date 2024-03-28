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


