'''
Time-series Data Analyzer Application Window Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import sys, os
import pathlib
from PyQt6.QtGui import QImage, QPixmap, QCloseEvent, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QFileDialog, QFrame, QVBoxLayout
from PyQt6.uic import loadUi
from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import signal as scisignal
from PIL import ImageQt, Image
from sys import platform
import paho.mqtt.client as mqtt
import pyqtgraph as graph

from util.logger.console import ConsoleLogger

'''
Main Window
'''

class AppWindow(QMainWindow):
    def __init__(self, config:dict):
        super().__init__()
        
        self.__console = ConsoleLogger.get_logger()
        
        self.__frame_win_series_layout = QVBoxLayout()
        self.__frame_win_series_plot = graph.PlotWidget()
        self.__frame_win_fft_layout = QVBoxLayout()
        self.__frame_win_fft_plot = graph.PlotWidget()
        self.__frame_win_spectorgram_layout = QVBoxLayout()
        self.__frame_win_spectogram_plot = graph.PlotWidget()
        
        try:            
            if "gui" in config:
                
                # load gui file
                ui_path = pathlib.Path(config["app_path"]) / config["gui"]
                if os.path.isfile(ui_path):
                    loadUi(ui_path, self)
                else:
                    raise Exception(f"Cannot found UI file : {ui_path}")
                
                # frame components preparation
                self.__frame_win_series = self.findChild(QFrame, name="frame_series_view")
                self.__frame_win_series_layout.addWidget(self.__frame_win_series_plot)
                self.__frame_win_series_layout.setContentsMargins(0, 0, 0, 0)
                self.__frame_win_series_plot.setBackground('w')
                self.__frame_win_series_plot.showGrid(x=True, y=True)
                self.__frame_win_series.setLayout(self.__frame_win_series_layout)
                
                self.__frame_win_fft = self.findChild(QFrame, name="frame_fft_view")
                self.__frame_win_fft_layout.addWidget(self.__frame_win_fft_plot)
                self.__frame_win_fft_layout.setContentsMargins(0, 0, 0, 0)
                self.__frame_win_fft_plot.setBackground('w')
                self.__frame_win_fft_plot.showGrid(x=True, y=True)
                self.__frame_win_fft.setLayout(self.__frame_win_fft_layout)
                
                self.__frame_win_spectogram = self.findChild(QFrame, name="frame_spectogram_view")
                self.__frame_win_spectorgram_layout.addWidget(self.__frame_win_spectogram_plot)
                self.__frame_win_spectorgram_layout.setContentsMargins(0, 0, 0, 0)
                self.__frame_win_spectogram_plot.setBackground('w')
                self.__frame_win_spectogram_plot.showGrid(x=True, y=True)
                self.__frame_win_spectogram.setLayout(self.__frame_win_spectorgram_layout)
                
                # connection gui event callback functions
                self.actionOpen_CSV_File.triggered.connect(self.on_select_csv_open)
                self.btn_update.clicked.connect(self.on_click_update)
                
                # menu event callback function connection
                #self.actionBatch_Process.triggered.connect(self.on_select_batch_process)
                
        except Exception as e:
            self.__console.critical(f"{e}")
            
        # member variables
        self.__configure = config   # configure parameters
    
    
    # open single csv file
    def on_select_csv_open(self):
        selected = QFileDialog.getOpenFileName(self, 'Open CSV file', './')
        
        if selected[0]: # 0 = abs path
            self.__console.info(f"Load CSV File : {selected[0]}")
            
            try:
                # read csv file
                __csv_raw = pd.read_csv(selected[0])
                __csv_data = __csv_raw.iloc[1:]
                __csv_header = __csv_raw.columns
                
                # read parameters
                __sampling_time = 1.0/float(self.edit_sampling_freq.text())
                
                # show info
                self.statusBar().showMessage(f"{selected[0]} {__csv_data.shape}")
                
                # draw graph
                self.__frame_win_series_plot.setTitle(f"{pathlib.Path(selected[0]).stem} Data", color="k", size="25pt")
                styles = {"color": "#000", "font-size": "15px"}
                self.__frame_win_series_plot.setLabel("left", "Value", **styles)
                self.__frame_win_series_plot.setLabel("bottom", "Time(sec)", **styles)
                self.__frame_win_series_plot.addLegend()
                
                
                # display opened series data
                x = np.linspace(0, __csv_data.shape[0]*__sampling_time, __csv_data.shape[0])
                colorlist = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
                for idx, ch in enumerate(__csv_header):
                    y = __csv_raw.loc[:,ch].iloc[1:].to_list()
                    self.__frame_win_series_plot.plot(x, y, name=ch, pen=graph.mkPen(color=colorlist[idx], width=2))
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"{e}")
    
    # redraw and calculation by update
    def on_click_update(self):
        pass
    
    
                
    # batch processing menu callback
    def on_select_batch_process(self):
        
        # open file dialog to select target directory
        directory = QFileDialog.getExistingDirectory(None, "Select Directory")
        
        if directory:
            # listup sub-directory
            path = pathlib.Path(directory)
            subdirectories = [str(subdir) for subdir in path.iterdir() if subdir.is_dir()]
        
            self.__console.info(f"{len(subdirectories)}")

        
    def closeEvent(self, a0: QCloseEvent | None) -> None:
        
        self.__console.info("Terminated Successfully")
        
        return super().closeEvent(a0)