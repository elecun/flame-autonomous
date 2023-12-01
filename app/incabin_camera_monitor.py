'''
In-Cabin Camera Monitoring and Recorder with Qt GUI
@auhtor Byunghun Hwang<bh.hwnag@iae.re.kr>
'''

import sys, os
from PyQt6 import QtGui
import pathlib
import json
from PyQt6.QtGui import QImage, QPixmap, QCloseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from datetime import datetime
import argparse
import time

# root directory registration on system environment
ROOT_PATH = pathlib.Path(__file__).parent.parent
sys.path.append(ROOT_PATH.as_posix())

from incabin_camera_monitor.window import AppWindow
from vision.camera.uvc import Controller as IncabinCameraController
from vision.HPE.YOLOv8 import Model as YOLOv8_model


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', required=True, help="Configuration File(*.cfg)", default="default.cfg")
    parser.add_argument('--verbose', nargs='?', required=False, help="Enable/Disable verbose", default=True)
    args = parser.parse_args()

    app = None
    try:
        with open(args.config, "r") as cfile:
            configure = json.load(cfile)

            configure["root_path"] = ROOT_PATH
            configure["app_path"] = (pathlib.Path(__file__).parent / "incabin_camera_monitor")
            configure["verbose"] = args.verbose
            video_out_dir = (ROOT_PATH / configure["video_out_path"])

            if args.verbose:
                print(f"* Root Directory : {configure['root_path']}")
                print(f"* Application Directory : {configure['app_path']}")
                print(f"* Video Out Directory : {video_out_dir}")

            # check required parameters
            if not all(key in configure for key in ["hpe_model", "camera_id", "camera_fps", "camera_width", "camera_height", "video_extension"]):
                raise Exception(f"some parameters does not set in the {args.config}configuration file")

            app = QApplication(sys.argv)
            app_window = AppWindow(config=configure)
            
            if "app_window_title" in configure:
                app_window.setWindowTitle(configure["app_window_title"])
            app_window.show()
            sys.exit(app.exec())

    except json.JSONDecodeError as e:
        print(f"Configuration File Load Error : {e}")
    except Exception as e:
        print(f"-Exception : {e}")
        
    
        
    