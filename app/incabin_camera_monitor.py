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
from vision.camera.USB_General import Controller as IncabinCamController
from vision.HPE.YOLOv8 import Model as YOLOv8_model
from util.logger.video import VideoRecorder

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', required=True, help="Configuration File(*.cfg)", default="default.cfg")
    parser.add_argument('--broker', nargs='?', required=False, help="Broker IP Address", default="127.0.0.1")
    args = parser.parse_args()

    app = None
    try:
        with open(args.config, "r") as cfile:
            configure = json.load(cfile)

            configure["root_path"] = ROOT_PATH.as_posix()
            configure["app_path"] = (pathlib.Path(__file__).parent / "incabin_camera_monitor").as_posix()
            video_out_dir = (ROOT_PATH / configure["video_out_path"])

            print(f"* Root Directory : {configure['root_path']}")
            print(f"* Application Directory : {configure['app_path']}")
            print(f"* Video Out Directory : {video_out_dir}")

            # check required parameters
            if not all(key in configure for key in ["hpe_model", "camera_id"]):
                raise Exception(f"some parameters does not set in the {args.config}configuration file")

            app = QApplication(sys.argv)
            app_window = AppWindow(config=configure, 
                                   camera=[IncabinCamController(id, recorder=VideoRecorder(video_out_dir, f"camera_{id}")) for idx, id in enumerate(configure["camera_id"])], 
                                   postprocess=[YOLOv8_model(str(configure["hpe_model"]).lower()) for idx, id in enumerate(configure["camera_id"])])
            
            if "app_window_title" in configure:
                app_window.setWindowTitle(configure["app_window_title"])
            app_window.show()
            sys.exit(app.exec())

    except json.JSONDecodeError as e:
        print(f"Configuration File Load Error : {e}")
    except Exception as e:
        print(f"Exception : {e}")
        
    
        
    