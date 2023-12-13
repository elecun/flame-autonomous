'''
Time-series Data Analyzer Application Window Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import sys, os
import pathlib
from PyQt6.QtGui import QImage, QPixmap, QCloseEvent, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QFileDialog, QFrame, QVBoxLayout, QComboBox, QLineEdit, QCheckBox
from PyQt6.uic import loadUi
from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from datetime import datetime
import pandas as pd
import numpy as np
from PIL import ImageQt, Image
from sys import platform
import paho.mqtt.client as mqtt
import pyqtgraph as graph
import librosa
from joblib import Parallel, delayed, parallel_backend
from typing import Union

from util.logger.console import ConsoleLogger
from analysis.series.spectogram import Spectogram
from app.series_analyzer.model import FaultDetection_Resnet

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
        
        # local variables
        self.__current_csv_file = None
        
        try:            
            if "gui" in config:
                
                # load gui file
                ui_path = pathlib.Path(config["app_path"]) / config["gui"]
                if os.path.isfile(ui_path):
                    loadUi(ui_path, self)
                else:
                    raise Exception(f"Cannot found UI file : {ui_path}")
                
                # frame window components preparation
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
                self.__frame_win_spectogram.setLayout(self.__frame_win_spectorgram_layout)
                
                # other GUI components
                self.__spectogram_channels = self.findChild(QComboBox, name="dropdown_channels")
                self.__spectogram_channels.currentIndexChanged.connect(self.on_changed_spectogram_channel_index)
                
                self.__model_selection = self.findChild(QComboBox, name="dropdown_model_selection")
                self.__model_selection.currentIndexChanged.connect(self.on_changed_model_selection_index)
                self.__model_selection.addItems(["purgefan fault classification"])
                
                # connection gui event callback functions
                self.actionOpen_CSV_File.triggered.connect(self.on_select_csv_open)
                self.btn_parameter_apply.clicked.connect(self.on_click_parameter_apply)
                self.btn_batch_start_spectogram.clicked.connect(self.on_click_batch_start_spectogram)
                self.btn_working_dir_selection.clicked.connect(self.on_click_working_dir_selection)
                self.btn_batch_output_dir_selection.clicked.connect(self.on_click_batch_output_dir_selection)
                self.btn_run_model_test.clicked.connect(self.on_click_run_model_test)
                
                # variables
                self.__spectogram_result = {}
                
        except Exception as e:
            self.__console.critical(f"{e}")
            
        # member variables
        self.__configure = config   # configure parameters
        
    # clear all guis
    def clear_all(self):
        try:
            self.__frame_win_series_plot.clear()
            self.__frame_win_fft_plot.clear()
            self.__frame_win_spectogram_plot.clear()
            
            self.__spectogram_channels.disconnect()
            self.__spectogram_channels.clear()
            
        except Exception as e:
            self.__console.critical(f"{e}")
            
    # data analysis
    def csv_analysis_perform(self, csv_file:Union[str, None]):
        
        try:
            # update current working csv file
            if csv_file is not None:
                self.__current_csv_file = csv_file
            
            self.__console.info(f"Load CSV File : {self.__current_csv_file}")
            
            # clear all plots and components
            self.clear_all()
            
            # reconnect with combobox event callback (if not, it will be raised an exception)
            self.__spectogram_channels.currentIndexChanged.connect(self.on_changed_spectogram_channel_index)
        
            # read csv file
            __csv_raw = pd.read_csv(self.__current_csv_file)
            
            # read parameters
            __sampling_time = 1.0/float(self.edit_sampling_freq.text())
            __sampling_freq = float(self.edit_sampling_freq.text())
            
            # show info
            self.statusBar().showMessage(f"{self.__current_csv_file} {__csv_raw.shape}")
            
            # draw graph
            self.__frame_win_series_plot.setTitle(f"{pathlib.Path(self.__current_csv_file).stem} Data", color="k", size="25pt")
            styles = {"color": "#000", "font-size": "15px"}
            self.__frame_win_series_plot.setLabel("left", "Value", **styles)
            self.__frame_win_series_plot.setLabel("bottom", "Time(sec)", **styles)
            self.__frame_win_series_plot.addLegend()
            
            # display opened series data
            x = np.linspace(0, __csv_raw.shape[0]*__sampling_time, __csv_raw.shape[0])
            colorlist = ['r', 'c', 'g', 'b', 'm', 'y', 'k', 'w']
            for idx, ch in enumerate(__csv_raw.columns):
                y = __csv_raw.loc[:,ch].to_list()
                self.__frame_win_series_plot.plot(x, y, name=ch, pen=graph.mkPen(color=colorlist[idx], width=2))
                
            # for fft
            self.__frame_win_fft_plot.setTitle(f"{pathlib.Path(self.__current_csv_file).stem} FFT", color="k", size="25pt")
            styles = {"color": "#000", "font-size": "15px"}
            self.__frame_win_fft_plot.setLabel("left", "Amplitude", **styles)
            self.__frame_win_fft_plot.setLabel("bottom", "Frequency", **styles)
            self.__frame_win_fft_plot.addLegend()

            __csv_mean = __csv_raw.mean()
            __csv_normalized = __csv_raw - __csv_mean # note : make signal mean value to zero(=remove DC elements)
            
            for idx, ch in enumerate(__csv_raw.columns):
                _data = np.transpose(__csv_normalized[ch])
                
                # do fft
                fx = np.fft.fft(_data, n=None, axis=-1, norm=None)
                amplitude = abs(fx)
                frequency = np.fft.fftfreq(len(fx), __sampling_time)
                
                # remove half of fft data
                half = len(frequency)//2
                frequency = frequency[:half]
                amplitude = amplitude[:half]
                
                # find max freq
                peak_frequency = frequency[amplitude.argmax()]
                
                # peak
                text = graph.TextItem(text=f'{peak_frequency:.2f}Hz', color=(0,0,0))
                text.setPos(peak_frequency, amplitude[amplitude.argmax()])
                self.__frame_win_fft_plot.addItem(text)
                
                # plot
                self.__frame_win_fft_plot.plot(frequency, amplitude, name=ch, pen=graph.mkPen(color=colorlist[idx], width=2))
                
                # calc spectogram
                graph.setConfigOptions(imageAxisOrder='row-major') # axis rotate
                stft = librosa.stft(y=_data.to_numpy(), win_length=None, hop_length=1, window='hann', n_fft=int(__sampling_freq))
                magnitude = np.abs(stft)
                
                # amplitude to db
                db = librosa.amplitude_to_db(magnitude, ref=np.max)

                self.__spectogram_result[ch] = magnitude
                
                # add spectogram item
                self.__spectogram_channels.addItem(ch)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}")
        
    
    # open single csv file
    def on_select_csv_open(self):
        selected = QFileDialog.getOpenFileName(self, 'Open CSV file', './')
        
        if selected[0]: # 0 = abs path
            self.csv_analysis_perform(selected[0])
    
    # redraw and calculation by update
    def on_click_parameter_apply(self):
        self.csv_analysis_perform(None)
    
    # spectogram generation batch processing start
    def on_click_batch_start_spectogram(self):
        _working_path = self.findChild(QLineEdit, name="edit_working_dir").text()
        _output_path = self.findChild(QLineEdit, name="edit_batch_output_dir").text()
        _sampling_freq = int(self.edit_sampling_freq.text())
        
        _opt_resize = self.findChild(QCheckBox, name="chk_output_resize").isChecked()
    
        _spectogram = Spectogram()
        if _working_path and _output_path:
            
            # read files under working directory without subdirectory
            files = [(pathlib.Path(_working_path)/f).as_posix() for f in os.listdir(_working_path) if f.endswith('.csv')]
            
            # with sequential with single thread
            # for f in files:
            #     _spectogram.generate_to_image(csv_file_in=f, out_path=_output_path, fs=_sampling_freq, opt_resize=_opt_resize)
            
            # work in parallel
            Parallel(n_jobs=-1, prefer="threads", verbose=10)(delayed(_spectogram.generate_to_image)(f, _output_path, _sampling_freq, _opt_resize) for f in files)
            
            QMessageBox.information(self, "Done", f"Batch Processing is Done.")
        else:
            self.__console.warning("No batch processing working path or output path")
    
    
    # select working directory
    def on_click_working_dir_selection(self):
        # open directory selection
        directory = QFileDialog.getExistingDirectory(None, "Choose Working Directory")
        if directory:
            self.__console.info(f"Batch working directory : {directory}")
                
            # show on editbox
            _edit_working = self.findChild(QLineEdit, name="edit_working_dir")
            _edit_working.setText(directory)
    
    
    # select output directory
    def on_click_batch_output_dir_selection(self):
        
        # open directory selection
        directory = QFileDialog.getExistingDirectory(None, "Choose Output Directory")
        if directory:
            self.__console.info(f"Batch output directory : {directory}")
                
            # show on editbox
            _edit_output = self.findChild(QLineEdit, name="edit_batch_output_dir")
            _edit_output.setText(directory)
    
    # model run
    def on_click_run_model_test(self):
        selected_model = self.__model_selection.currentText()
        self.__console.info(f"{selected_model} model is working..")
        _result = "-"
        
        _label_result = self.findChild(QLabel, "label_model_result")
        
        if selected_model.lower() == "anomaly detection":
            # model load
            _model = FaultDetection_Resnet()
            if _model.predict():
                # show results
                _label_result.setStyleSheet("color: red;")
                _result = "Abnormal\n(Fault)"
            else:
                _label_result.setStyleSheet("color: green;")
                _result = "Normal"
                
        elif selected_model.lower() == "fault prediction":
            _label_result.setStyleSheet("color: yellow;")
            _result = "Class 1"
        
        
        _label_result.setText(_result)
        
        
        
    # changed channel index by user
    def on_changed_spectogram_channel_index(self, index):
        try:
            ch = self.__spectogram_channels.currentText()
            image = graph.ImageItem(image=self.__spectogram_result[ch])
            cmap = graph.colormap.getFromMatplotlib("jet")
            
            self.__frame_win_spectogram_plot.setTitle(f"{ch} Spectogram(Linear)", color="k", size="25pt")
            styles = {"color": "#000", "font-size": "15px"}
            self.__frame_win_spectogram_plot.setLabel("left", "Frequency(Hz)", **styles)
            self.__frame_win_spectogram_plot.setLabel("bottom", "Time(ms)", **styles)
            self.__frame_win_spectogram_plot.addItem(image)
            image.setColorMap(colorMap=cmap)
            
        except Exception as e:
            self.__console.critical(f"{e}")
            
    # model selection
    def on_changed_model_selection_index(self, index):
        try:
            model = self.__model_selection.currentText()
            self.__console.info(f"Selected Model : {model}")
        except Exception as e:
            self.__console.critical(f"{e}")
                
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