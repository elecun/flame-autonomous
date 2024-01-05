'''
Steel Surface Defect Detectpr Application Window class
@Author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import os, sys
import cv2
import pathlib
try:
    # using PyQt5
    from PyQt5.QtGui import QImage, QPixmap, QCloseEvent, QStandardItem, QStandardItemModel
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QProgressBar, QFileDialog
    from PyQt5.uic import loadUi
    from PyQt5.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
except ImportError:
    # using PyQt6
    from PyQt6.QtGui import QImage, QPixmap, QCloseEvent, QStandardItem, QStandardItemModel
    from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QProgressBar, QFileDialog
    from PyQt6.uic import loadUi
    from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
    
import numpy as np
from datetime import datetime
from pypylon import genicam
from pypylon import pylon

from vision.camera.gige import Controller as GigECameraController
from vision.camera.gige import gige_camera_discovery
from util.logger.video import VideoRecorder
from util.monitor.system import SystemStatusMonitor
from util.monitor.gpu import GPUStatusMonitor
from util.logger.console import ConsoleLogger
from vision.SDD.ResNet import ResNet9 as SDDModel

'''
Main window
'''
class AppWindow(QMainWindow):
    def __init__(self, config:dict):
        super().__init__()
        
        self.__console = ConsoleLogger.get_logger()

        try:            
            if "gui" in config:
                
                # load gui file
                ui_path = pathlib.Path(config["app_path"]) / config["gui"]
                if os.path.isfile(ui_path):
                    loadUi(ui_path, self)
                else:
                    raise Exception(f"Cannot found UI file : {ui_path}")
                
                # menu event callback function connection
                self.actionOpen.triggered.connect(self.on_select_camera_open)
                self.actionDiscovery.triggered.connect(self.on_select_camera_discovery)
                self.actionStartStopDataRecording.triggered.connect(self.on_select_start_stop_data_recording)
                self.actionCapture_to_Image_png.triggered.connect(self.on_select_capture_image)
                
                # GUI component event callback function connection
                self.btn_camera_discovery.clicked.connect(self.on_click_camera_discovery)
                self.table_camera_list.doubleClicked.connect(self.on_dbclick_camera_list)
                
                # define camera list table model
                _talbe_camera_columns = ["ID", "Camera Name", "Address"]
                self.__table_camlist_model = QStandardItemModel()
                self.__table_camlist_model.setColumnCount(len(_talbe_camera_columns))
                self.__table_camlist_model.setHorizontalHeaderLabels(_talbe_camera_columns)
                self.table_camera_list.setModel(self.__table_camlist_model)
                self.table_camera_list.resizeColumnsToContents()
                
                # frame window mapping
                self.__frame_window_map = {}
                for idx, id in enumerate(config["camera_id"]):
                    self.__frame_window_map[id] = config["camera_window"][idx]

                # apply monitoring
                self.__sys_monitor = SystemStatusMonitor(interval_ms=1000)
                self.__sys_monitor.usage_update_signal.connect(self.update_system_status)
                self.__sys_monitor.start()
                
                # apply gpu monitoring
                try:
                    self.__gpu_monitor = GPUStatusMonitor(interval_ms=1000)
                    self.__gpu_monitor.usage_update_signal.connect(self.update_gpu_status)
                    self.__gpu_monitor.start()
                except Exception as e:
                    self.__console.critical("GPU may not be available")
                    pass
            else:
                raise Exception("GUI definition must be contained in the configuration file.")

        except Exception as e:
            self.__console.critical(f"{e}")
        
        # member variables
        self.__configure = config   # configure parameters
        self.__sdd_model_container = {}   # SDD classification model container
        self.__camera_container = {}
        self.__recorder_container = {}
        
        self.__camera:GigECameraController = None # camera device controller
        self.__recorder:VideoRecorder = None # video recorder
        
        # find GigE Cameras & update camera list
        __cam_found = gige_camera_discovery()
        print(__cam_found)
        #__cam_found = [("0", "GigE Cam", "192.168.0.1")] # for test
        self.__update_camera_list(__cam_found)
        
    
    '''
    Private Member functions
    '''    
    def __update_camera_list(self, cameras:list):
        label_n_cam = self.findChild(QLabel, "label_num_camera")
        label_n_cam.setText(str(len(cameras)))
        
        # clear tableview
        self.__table_camlist_model.setRowCount(0)
        
        # add row
        for idx, (id, name, address) in enumerate(cameras):
            self.__table_camlist_model.appendRow([QStandardItem(str(id)), QStandardItem(str(name)), QStandardItem(str(address))])
        self.table_camera_list.resizeColumnsToContents()
        
    '''
    GUI Event Callback functions
    '''
    # selected camera to open
    def on_select_camera_open(self):
        # open camera array
        if len(self.__camera_container)>0:
            QMessageBox.warning(self, "Warning", "All camera is already working..")
            return
        
        # create camera instance
        for id in self.__configure["camera_id"]:
            camera = GigECameraController(id)
            if camera.open():
                self.__camera_container[id] = camera
                self.__camera_container[id].frame_update_signal.connect(self.show_updated_frame) # connect to frame grab signal
                
                resol = self.__camera_container[id].get_pixel_resolution()
        
        # previous
        row = self.table_camera_list.currentIndex().row()
        col = self.table_camera_list.currentIndex().column()
        self.__console.info(f"selected {row}, {col}")
    
    # re-discover all gige network camera
    def on_select_camera_discovery(self):
        __cam_found = gige_camera_discovery()
        self.__update_camera_list(__cam_found)
    
    # data recording
    def on_select_start_stop_data_recording(self):
        if self.sender().isChecked(): #start recording
            self.__recorder.start()
        else:   # stop recording
            self.__recorder.stop()
    
    # start image capture
    def on_select_capture_image(self):
        pass
    
    # re-discover cameras
    def on_click_camera_discovery(self):
        # clear camera table
        self.__table_camlist_model.setRowCount(0)
        
        # find & update
        __cam_found = gige_camera_discovery()
        self.__update_camera_list(__cam_found)
        
    # double clicked on camera list
    def on_dbclick_camera_list(self):
        row = self.table_camera_list.currentIndex().row()
        col = self.table_camera_list.currentIndex().column()
        
        # get camera id from tableview
        id = self.__table_camlist_model.index(row, 0).data()
        
        self.__console.info(f"Selected camera ID : {id}")
        
        # if camera is working, close it
        if self.__camera!=None:
            self.__camera.close()
        
        # set camera controller with id
        self.__camera = GigECameraController(id)
        if self.__camera.open():
            self.__camera.frame_update_signal.connect(self.show_updated_frame)
            self.__camera.begin()
        else:
            self.__camera.close()
            self.__camera = None
            QMessageBox.warning(self, "Camera open failed", "Failed to open camera device")
            

        
    # show message on status bar
    def show_on_statusbar(self, text):
        self.statusBar().showMessage(text)
        
    # show updated image frame on GUI window
    def show_updated_frame(self, image:np.ndarray, fps:float):
        # converting color format
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # draw information
        t_start = datetime.now()
        id = self.sender().get_camera_id()
        
        cv2.putText(rgb_image, f"Camera #{id}(fps:{int(fps)})", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
        cv2.putText(rgb_image, t_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], (10, 1070), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
        
        #converting ndarray to qt image
        _h, _w, _ch = rgb_image.shape
        _bpl = _ch*_w # bytes per line
        qt_image = QImage(rgb_image.data, _w, _h, _bpl, QImage.Format.Format_RGB888)

        # converting qt image to QPixmap
        pixmap = QPixmap.fromImage(qt_image)

        # draw on window
        try:
            window = self.findChild(QLabel, FRAME_WINDOW_NAME)
            window.setPixmap(pixmap.scaled(window.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            self.__console.critical(f"{e}")
        
        
    # close event callback function by user
    def closeEvent(self, a0: QCloseEvent) -> None:
        
        # if recording.. stop working
        if self.__recorder!=None:
            self.__recorder.stop()
            
        if self.__camera!=None:
            self.__camera.close()
        
        # close monitoring thread
        try:
            self.__sys_monitor.close()
            self.__gpu_monitor.close()
        except AttributeError as e:
            self.__console.critical(f"{e}")
            
        self.__console.info("Terminated Successfully")
        
        return super().closeEvent(a0)    
    
    # show update system monitoring on GUI window
    def update_system_status(self, status:dict):
        cpu_usage_window = self.findChild(QProgressBar, "progress_cpu_usage")
        mem_usage_window = self.findChild(QProgressBar, "progress_mem_usage")
        storage_usage_window = self.findChild(QProgressBar, "progress_storage_usage")
        cpu_usage_window.setValue(int(status["cpu"]))
        mem_usage_window.setValue(int(status["memory"]))
        storage_usage_window.setValue(int(status["storage"]))
        
    # show update gpu monitoring on GUI window
    def update_gpu_status(self, status:dict):
        if "gpu_count" in status:
            if status["gpu_count"]>0:
                gpu_usage_window = self.findChild(QProgressBar, "progress_gpu_usage")
                gpu_mem_usage_window = self.findChild(QProgressBar, "progress_gpu_mem_usage")
                gpu_usage_window.setValue(int(status["gpu_0"]))
                gpu_mem_usage_window.setValue(int(status["memory_0"]))
        
            
   
        
        
        
        
        
        
        

    # menu event callback : all camera connection
    def on_select_connect_all(self):

        
        # create camera instance
        for id in self.__configure["camera_id"]:
            camera = GigECameraController(id)
            if camera.open():
                self.__camera_container[id] = camera
                self.__camera_container[id].frame_update_signal.connect(self.show_updated_frame)    # connect to frame grab signal callback function
                
                resol = self.__camera_container[id].get_pixel_resolution()
                # create video recorder
                self.__recorder_container[id] = VideoRecorder(dirpath=(self.__configure["app_path"] / self.__configure["video_out_path"]), 
                                                              filename=f"camera_{id}",
                                                              ext=self.__configure["video_extension"],
                                                              resolution=(int(self.__configure["camera_width"]), int(self.__configure["camera_height"])),
                                                              fps=float(self.__configure["camera_fps"]))
                self.__camera_container[id].frame_update_signal.connect(self.__recorder_container[id].write_frame)
                
                # create SDD estimator
                self.__sdd_container[id] = SDDModel(modelname=self.__configure["hpe_model"], id=id)
                self.__camera_container[id].frame_update_signal.connect(self.__hpe_container[id].predict)
                # self.__hpe_container[id].estimated_result_image.connect(self.show_estimated_frame) # draw key points
                
                # start grab thread
                self.__camera_container[id].begin()
            else:
                QMessageBox.warning(self, "Camera connection fail", f"Failed to connect to camera {camera.uvc_camera.get_camera_id()}")

    
            
     

    # camera discovery
    # def on_click_camera_discovery(self):
    #     try:
    #         _tlf = pylon.TlFactory.GetInstance()
    #         _devices = _tlf.EnumerateDevices()
    #         print(f"Found {len(_devices)} Camera(s)")
            
    #         if len(_devices)==0:
    #             raise pylon.RuntimeException("No cameras present")
            
    #         # setup camera array
    #         _camera_container = pylon.InstantCameraArray(len(_devices))
            
    #     except Exception as e:
    #         self.__console.warning(f"{len(_devices)} camera found")
    #         QMessageBox.warning(self, f"{e}")




    
    # internal api for starting record
    def _api_record_start(self):
        for camera in self.opened_camera.values():
            print(f"Recording start...({camera.camera_id})")
            camera.start_recording()
        self.show_on_statusbar("Start Recording...")
    
    # internal api for stopping record
    def _api_record_stop(self):
        for camera in self.opened_camera.values():
            print(f"Recording stop...({camera.camera_id})")
            camera.stop_recording()
        self.show_on_statusbar("Stopped Recording...")
        
    # capture image
    def _api_capture_image(self, delay_s:int):
        for camera in self.opened_camera.values():
            camera.start_capturing(delay_s)
        self.show_on_statusbar(f"Captured image after {delay_s} second(s)")



    # update image frame on label area
    def update_frame(self, image):
        id = self.sender().camera_id
        pixmap = QPixmap.fromImage(image)
        #window = self.findChild(QLabel, camera_windows[id])
        try:
            window = self.findChild(QLabel, self.configure_param["camera_windows_map"][id])
            window.setPixmap(pixmap.scaled(window.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            self.__console.warning(f"{e}")
    