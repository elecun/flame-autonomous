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
from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from datetime import datetime
import argparse
import time

WORKING_PATH = pathlib.Path(__file__).parent.parent

if __name__ == "__main__":
    print(WORKING_PATH)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--broker', nargs='?', required=False, help="Broker IP Address", default="127.0.0.1")
    parser.add_argument('--config', nargs='?', required=True, help="Configuration File(*.json)", default="default.json")
    args = parser.parse_args()
    
    configure = None
    print(args.config)
    try:
        with open("./bin/camera.json", "r") as cfile:
            configure = json.load(cfile)
        print(configure)
    except Exception as e:
        print(f"Error : {e}")
    
    # app = QApplication(sys.argv)
    # window = CameraWindow(broker_ip_address=broker_ip_address, config=configure)
    # window.show()
    # sys.exit(app.exec())