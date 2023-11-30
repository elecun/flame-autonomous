# flame-autonomous
Software Packages for Autonomous System


# Setup Environments
- Software Dependency
  * Ubuntu 22.04.3 LTS
  * Python==3.10
  * OpenCV==4.8
- Hardware Dependency
  * NVIDIA GPU x 1

```
$ python -m venv venv
$ source ./venv/bin/activate
(venv)$ pip install -r requirements.txt
```

# Execute Camera Monitoring Application (for AV Simulator)
```
$ make incabin_camera_monitor
or
$ python ./app/incabin_camera_monitor.py --config ./bin/camera.cfg
```