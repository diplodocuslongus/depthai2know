Upon first run:

    $ depthai-viewer 

        Welcome to Rerun!

        This open source library collects anonymous usage data to
        help the Rerun team improve the library.

        Summary:
        - We only collect high level events about the features used within the Depthai Viewer.
        - The actual data you log to Rerun, such as point clouds, images, or text logs,
          will never be collected.
        - We don't log IP addresses.
        - We don't log your user name, file paths, or any personal identifiable data.
        - Usage data we do collect will be sent to and stored on servers within the EU.

        For more details and instructions on how to opt out, run the command:

          rerun analytics details

        As this is this your first session, _no_ usage data has been sent yet,
        giving you an opportunity to opt-out first if you wish.

        Happy Rerunning!

    Got exit status: Exited(0)
    Log output: The virtual environment was not created successfully because ensurepip is not
    available.  On Debian/Ubuntu systems, you need to install the python3-venv
    package using the following command.

        apt install python3.10-venv

    You may need to use sudo with that command.  After installing the python3-venv
    package, recreate your virtual environment.

    Failing command: /home/ludofw/.virtualenvs/ocv490_py310/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/bin/python

    Creating virtual environment...
    Error occurred during dependency installation: Command '['/home/ludofw/.virtualenvs/ocv490_py310/bin/python', '-m', 'venv', '/home/ludofw/.virtualenvs/ocv490_py310/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8']' returned non-zero exit status 1.
    Traceback (most recent call last):
      File "/home/ludofw/.virtualenvs/ocv490_py310/lib/python3.10/site-packages/depthai_viewer/install_requirements.py", line 83, in create_venv_and_install_dependencies
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
      File "/usr/lib/python3.10/subprocess.py", line 526, in run
        raise CalledProcessError(retcode, process.args,
    subprocess.CalledProcessError: Command '['/home/ludofw/.virtualenvs/ocv490_py310/bin/python', '-m', 'venv', '/home/ludofw/.virtualenvs/ocv490_py310/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8']' returned non-zero exit status 1.

    Deleting partially created virtual environment: /home/ludofw/.virtualenvs/ocv490_py310/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8

## log of install

This is the log of the full installation upon running `depthai_viewer`


    Requirement already satisfied: pip in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (22.0.2)
    Collecting pip
      Using cached pip-24.0-py3-none-any.whl (2.1 MB)
    Installing collected packages: pip
      Attempting uninstall: pip
        Found existing installation: pip 22.0.2
        Uninstalling pip-22.0.2:
          Successfully uninstalled pip-22.0.2
    Successfully installed pip-24.0
    Looking in indexes: https://pypi.org/simple, https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/
    Collecting depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475
      Downloading https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/depthai-sdk/depthai_sdk-1.13.1.dev0%2Bb0340e0c4ad869711d7d5fff48e41c46fe41f475-py3-none-any.whl (225 kB)
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 225.3/225.3 kB 173.1 kB/s eta 0:00:00
    Collecting opencv-contrib-python>4 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading opencv_contrib_python-4.9.0.80-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (20 kB)
    Collecting blobconverter>=1.4.1 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading blobconverter-1.4.3-py3-none-any.whl.metadata (7.8 kB)
    Collecting pytube>=12.1.0 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading pytube-15.0.0-py3-none-any.whl.metadata (5.0 kB)
    Collecting depthai==2.22.0 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading depthai-2.22.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (8.7 kB)
    Collecting PyTurboJPEG==1.6.4 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading PyTurboJPEG-1.6.4.tar.gz (11 kB)
      Installing build dependencies: started
      Installing build dependencies: finished with status 'done'
      Getting requirements to build wheel: started
      Getting requirements to build wheel: finished with status 'done'
      Installing backend dependencies: started
      Installing backend dependencies: finished with status 'done'
      Preparing metadata (pyproject.toml): started
      Preparing metadata (pyproject.toml): finished with status 'done'
    Collecting marshmallow==3.17.0 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading marshmallow-3.17.0-py3-none-any.whl.metadata (7.8 kB)
    Collecting xmltodict (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading xmltodict-0.13.0-py2.py3-none-any.whl.metadata (7.7 kB)
    Collecting sentry-sdk==1.21.0 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading sentry_sdk-1.21.0-py2.py3-none-any.whl.metadata (8.6 kB)
    Collecting depthai-pipeline-graph==0.0.5 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading depthai_pipeline_graph-0.0.5-py3-none-any.whl.metadata (8.8 kB)
    Collecting ahrs==0.3.1 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading AHRS-0.3.1-py3-none-any.whl.metadata (13 kB)
    Collecting numpy>=1.21 (from depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached numpy-1.26.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (61 kB)
    Collecting Qt.py>=1.3.0 (from depthai-pipeline-graph==0.0.5->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading Qt.py-1.3.10-py2.py3-none-any.whl.metadata (25 kB)
    Collecting packaging>=17.0 (from marshmallow==3.17.0->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached packaging-24.0-py3-none-any.whl.metadata (3.2 kB)
    Collecting certifi (from sentry-sdk==1.21.0->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached certifi-2024.2.2-py3-none-any.whl.metadata (2.2 kB)
    Collecting urllib3>=1.26.11 (from sentry-sdk==1.21.0->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached urllib3-2.2.1-py3-none-any.whl.metadata (6.4 kB)
    Collecting requests (from blobconverter>=1.4.1->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached requests-2.31.0-py3-none-any.whl.metadata (4.6 kB)
    Collecting PyYAML (from blobconverter>=1.4.1->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached PyYAML-6.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (2.1 kB)
    Collecting types-PySide2 (from Qt.py>=1.3.0->depthai-pipeline-graph==0.0.5->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Downloading types_pyside2-5.15.2.1.7-py2.py3-none-any.whl.metadata (8.1 kB)
    Collecting charset-normalizer<4,>=2 (from requests->blobconverter>=1.4.1->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached charset_normalizer-3.3.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (33 kB)
    Collecting idna<4,>=2.5 (from requests->blobconverter>=1.4.1->depthai-sdk==1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475)
      Using cached idna-3.6-py3-none-any.whl.metadata (9.9 kB)
    Downloading AHRS-0.3.1-py3-none-any.whl (197 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 197.9/197.9 kB 2.1 MB/s eta 0:00:00
    Downloading depthai-2.22.0.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (10.6 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 10.6/10.6 MB 28.6 MB/s eta 0:00:00
    Downloading depthai_pipeline_graph-0.0.5-py3-none-any.whl (123 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 123.5/123.5 kB 15.6 MB/s eta 0:00:00
    Downloading marshmallow-3.17.0-py3-none-any.whl (48 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 48.3/48.3 kB 5.8 MB/s eta 0:00:00
    Downloading sentry_sdk-1.21.0-py2.py3-none-any.whl (199 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 199.5/199.5 kB 20.1 MB/s eta 0:00:00
    Downloading blobconverter-1.4.3-py3-none-any.whl (10 kB)
    Using cached numpy-1.26.4-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (18.2 MB)
    Downloading opencv_contrib_python-4.9.0.80-cp37-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (68.3 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 68.3/68.3 MB 13.4 MB/s eta 0:00:00
    Downloading pytube-15.0.0-py3-none-any.whl (57 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 57.6/57.6 kB 8.1 MB/s eta 0:00:00
    Downloading xmltodict-0.13.0-py2.py3-none-any.whl (10.0 kB)
    Using cached packaging-24.0-py3-none-any.whl (53 kB)
    Downloading Qt.py-1.3.10-py2.py3-none-any.whl (34 kB)
    Using cached urllib3-2.2.1-py3-none-any.whl (121 kB)
    Using cached certifi-2024.2.2-py3-none-any.whl (163 kB)
    Using cached PyYAML-6.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (705 kB)
    Using cached requests-2.31.0-py3-none-any.whl (62 kB)
    Using cached charset_normalizer-3.3.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (142 kB)
    Using cached idna-3.6-py3-none-any.whl (61 kB)
    Downloading types_pyside2-5.15.2.1.7-py2.py3-none-any.whl (572 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 572.2/572.2 kB 14.2 MB/s eta 0:00:00
    Building wheels for collected packages: PyTurboJPEG
      Building wheel for PyTurboJPEG (pyproject.toml): started
      Building wheel for PyTurboJPEG (pyproject.toml): finished with status 'done'
      Created wheel for PyTurboJPEG: filename=PyTurboJPEG-1.6.4-py3-none-any.whl size=11207 sha256=9fa9e41a08614e86d97e603c9e3a51c5744aefa5f462db595ec5f80d86d4b68d
      Stored in directory: /home/ludofw/.cache/pip/wheels/5b/e5/e0/b4cc9ae5a7c0967487ddeb0ae922f3353e7bf0f36316ccd7f0
    Successfully built PyTurboJPEG
    Installing collected packages: types-PySide2, xmltodict, urllib3, Qt.py, PyYAML, pytube, packaging, numpy, idna, depthai, charset-normalizer, certifi, sentry-sdk, requests, PyTurboJPEG, opencv-contrib-python, marshmallow, depthai-pipeline-graph, ahrs, blobconverter, depthai-sdk
    Successfully installed PyTurboJPEG-1.6.4 PyYAML-6.0.1 Qt.py-1.3.10 ahrs-0.3.1 blobconverter-1.4.3 certifi-2024.2.2 charset-normalizer-3.3.2 depthai-2.22.0.0 depthai-pipeline-graph-0.0.5 depthai-sdk-1.13.1.dev0+b0340e0c4ad869711d7d5fff48e41c46fe41f475 idna-3.6 marshmallow-3.17.0 numpy-1.26.4 opencv-contrib-python-4.9.0.80 packaging-24.0 pytube-15.0.0 requests-2.31.0 sentry-sdk-1.21.0 types-PySide2-5.15.2.1.7 urllib3-2.2.1 xmltodict-0.13.0
    Looking in indexes: https://pypi.org/simple, https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local
    Requirement already satisfied: numpy>=1.23 in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 1)) (1.26.4)
    Collecting pyarrow==10.0.1 (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 2))
      Using cached pyarrow-10.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (3.0 kB)
    Requirement already satisfied: setuptools in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 3)) (59.6.0)
    Requirement already satisfied: ahrs in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 4)) (0.3.1)
    Collecting depthai==2.24.0.0.dev0+c014e27e224f7ef3f6407be6b3f05be6c2fffd13 (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 7))
      Downloading https://artifacts.luxonis.com/artifactory/luxonis-python-snapshot-local/depthai/depthai-2.24.0.0.dev0%2Bc014e27e224f7ef3f6407be6b3f05be6c2fffd13-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (11.0 MB)
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 11.0/11.0 MB 98.0 kB/s eta 0:00:00
    Collecting websockets (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 8))
      Downloading websockets-12.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
    Collecting pydantic==1.9 (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 9))
      Downloading pydantic-1.9.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (121 kB)
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 121.8/121.8 kB 1.1 MB/s eta 0:00:00
    Collecting deprecated (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 10))
      Using cached Deprecated-1.2.14-py2.py3-none-any.whl.metadata (5.4 kB)
    Requirement already satisfied: sentry-sdk in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from -r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 11)) (1.21.0)
    Collecting typing-extensions>=3.7.4.3 (from pydantic==1.9->-r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 9))
      Using cached typing_extensions-4.10.0-py3-none-any.whl.metadata (3.0 kB)
    Collecting wrapt<2,>=1.10 (from deprecated->-r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 10))
      Using cached wrapt-1.16.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl.metadata (6.6 kB)
    Requirement already satisfied: certifi in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from sentry-sdk->-r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 11)) (2024.2.2)
    Requirement already satisfied: urllib3>=1.26.11 in /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages (from sentry-sdk->-r /home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/requirements.txt (line 11)) (2.2.1)
    Using cached pyarrow-10.0.1-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (35.9 MB)
    Downloading pydantic-1.9.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl (12.3 MB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 12.3/12.3 MB 3.2 MB/s eta 0:00:00
    Downloading websockets-12.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (130 kB)
       ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 130.2/130.2 kB 4.4 MB/s eta 0:00:00
    Using cached Deprecated-1.2.14-py2.py3-none-any.whl (9.6 kB)
    Using cached typing_extensions-4.10.0-py3-none-any.whl (33 kB)
    Using cached wrapt-1.16.0-cp310-cp310-manylinux_2_5_x86_64.manylinux1_x86_64.manylinux_2_17_x86_64.manylinux2014_x86_64.whl (80 kB)
    Installing collected packages: wrapt, websockets, typing-extensions, pyarrow, depthai, pydantic, deprecated
      Attempting uninstall: depthai
        Found existing installation: depthai 2.22.0.0
        Uninstalling depthai-2.22.0.0:
          Successfully uninstalled depthai-2.22.0.0
    Successfully installed deprecated-1.2.14 depthai-2.24.0.0.dev0+c014e27e224f7ef3f6407be6b3f05be6c2fffd13 pyarrow-10.0.1 pydantic-1.9.0 typing-extensions-4.10.0 websockets-12.0 wrapt-1.16.0
    Creating virtual environment...
    Status Dump: {"venv_site_packages": "/home/ludofw/.virtualenvs/depthai/lib/python3.10/site-packages/depthai_viewer/venv-0.1.8/lib/python3.10/site-packages"}

