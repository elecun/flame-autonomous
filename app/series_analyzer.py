'''
Time-Series Data Analyzer
@author Byunghun Hwang<bh.hwang@iae.re.kr>
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

from series_analyzer.window import AppWindow
from util.logger.console import ConsoleLogger


if __name__ == "__main__":
    
    console = ConsoleLogger.get_logger()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', nargs='?', required=True, help="Configuration File(*.cfg)", default="mro.cfg")
    parser.add_argument('--verbose', nargs='?', required=False, help="Enable/Disable verbose", default=True)
    args = parser.parse_args()
    
    # get filename
    current_file_name = os.path.basename(__file__).split('.')[0]
    
    app = None
    try:
        with open(args.config, "r") as cfile: 
            configure = json.load(cfile)
            
            configure["root_path"] = ROOT_PATH
            configure["app_path"] = (pathlib.Path(__file__).parent / current_file_name)
            configure["verbose"] = args.verbose
            
            if not all(key in configure for key in ["model"]):
                raise Exception(f"some parameters does not set in the {args.config} configuration file")
            
            app = QApplication(sys.argv)
            app_window = AppWindow(config=configure)
            
            if "app_window_title" in configure:
                app_window.setWindowTitle(configure["app_window_title"])
            app_window.show()
            sys.exit(app.exec())
            
            
    except json.JSONDecodeError as e:
        console.critical(f"Configuration File Load Error : {e}")
    except Exception as e:
        console.critical(f"{e}")