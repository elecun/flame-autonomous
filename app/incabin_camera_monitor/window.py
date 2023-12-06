'''
Incabin Cmaera Monitor Application Window class
@Author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import os
import cv2
import pathlib
import paho.mqtt.client as mqtt
from PyQt6.QtGui import QImage, QPixmap, QCloseEvent
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QMessageBox, QProgressBar
from PyQt6.uic import loadUi
from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
import json
import numpy as np

from vision.camera.uvc import Controller as IncabinCameraController
from util.logger.video import VideoRecorder
from util.monitor.system import SystemStatusMonitor
from util.monitor.gpu import GPUStatusMonitor
from util.logger.console import ConsoleLogger

'''
Main window
'''
class AppWindow(QMainWindow):
    def __init__(self, config:dict):
        super().__init__()
        
        self.console = ConsoleLogger.get_logger()

        try:            
            if "gui" in config:
                
                # load gui file
                ui_path = pathlib.Path(config["app_path"]) / config["gui"]
                if os.path.isfile(ui_path):
                    loadUi(ui_path, self)
                else:
                    raise Exception(f"Cannot found UI file : {ui_path}")
                
                # menu event callback function connection
                self.actionStartDataRecording.triggered.connect(self.on_select_start_data_recording)
                self.actionStopDataRecording.triggered.connect(self.on_select_stop_data_recording)
                self.actionCapture_Image.triggered.connect(self.on_select_capture_image)
                self.actionCapture_Image_with_Keypoints.triggered.connect(self.on_select_capture_with_keypoints)
                self.actionCaptureAfter10s.triggered.connect(self.on_select_capture_after_10s)
                self.actionCaptureAfter20s.triggered.connect(self.on_select_capture_after_20s)
                self.actionCaptureAfter30s.triggered.connect(self.on_select_capture_after_30s)
                self.actionConnect_All.triggered.connect(self.on_select_connect_all)
                self.actionEnable_HPE.triggered.connect(self.on_select_enable_hpe)

                #frame window mapping
                self.frame_window_map = {}
                for idx, id in enumerate(config["camera_id"]):
                    self.frame_window_map[id] = config["camera_window"][idx]
                    
                # apply monitoring
                self.sys_monitor = SystemStatusMonitor(interval_ms=1000)
                self.sys_monitor.usage_update_signal.connect(self.update_system_status)
                self.sys_monitor.start()
                
                # apply gpu monitoring
                try:
                    self.gpu_monitor = GPUStatusMonitor(interval_ms=1000)
                    self.gpu_monitor.usage_update_signal.connect(self.update_gpu_status)
                    self.gpu_monitor.start()
                except Exception as e:
                    self.console.critical("GPU may not be available")
                    pass

        except Exception as e:
            self.console.critical(f"Exception : {e}")
        
        # member variables
        self.configure = config   # configure parameters
        self.is_camera_connected = False    # camera connection flag
        self.camera_container = {}    # connected camera

    # menu event callback : all camera connection
    def on_select_connect_all(self):
        if self.is_camera_connected:
            QMessageBox.warning(self, "Warning", "All camera is already working..")
            return
        
        # create camera instance
        for id in self.configure["camera_id"]:
            camera = IncabinCameraController(id)
            if camera.open():
                self.camera_container[id] = camera
                self.camera_container[id].frame_update_signal.connect(self.show_updated_frame)    # connect to frame grab signal callback function
                self.camera_container[id].begin()
            else:
                QMessageBox.warning(self, "Camera connection fail", f"Failed to connect to camera {camera.uvc_camera.camera_id}")

    # enable/disable hpe
    def on_select_enable_hpe(self):
        self.console.info(f"check : {self.sender().isChecked()}")

    # show updated image frame on GUI window
    def show_updated_frame(self, image:np.ndarray, fps:float):
        
        #converting ndarray to qt image
        _h, _w, _ch = image.shape
        _bpl = _ch*_w # bytes per line
        qt_image = QImage(image.data, _w, _h, _bpl, QImage.Format.Format_RGB888)

        # converting qt image to QPixmap
        pixmap = QPixmap.fromImage(qt_image)
        id = self.sender().get_camera_id()

        # draw on window
        try:
            window = self.findChild(QLabel, self.frame_window_map[id])
            window.setPixmap(pixmap.scaled(window.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            self.console.critical(f"Exception : {e}")
            
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
        
            
    # close event callback function by user
    def closeEvent(self, a0: QCloseEvent) -> None:
        for camera in self.camera_container.values():
            camera.close()
        
        try:
            self.sys_monitor.close()
            self.gpu_monitor.close()
        except AttributeError as e:
            self.console.critical(f"Error : {e}")
            
        self.console.info("Terminated Successfully")
        
        return super().closeEvent(a0)






    # camera open after show this GUI
    def start_monitor(self):
        if self.is_machine_running:
            QMessageBox.critical(self, "Already Running", "This Machine is already working...")
            return
        
        # for camera monitoring
        for id in self.configure_param["camera_ids"]:
            camera = CameraController(id)
            if camera.open():
                self.opened_camera[id] = camera
                self.opened_camera[id].image_frame_slot.connect(self.update_frame)
            else:
                QMessageBox.critical(self, "No Camera", "No Camera device connection")

        for camera in self.opened_camera.values():
            camera.begin()
    
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

    def _api_capture_image_keypoints(self):
        for camera in self.opened_camera.values():
            camera.start_capturing(delay=0)
    
    # on_select event for starting record
    def on_select_start_data_recording(self):
        self._api_record_start()
    
    # on_select event for stopping record
    def on_select_stop_data_recording(self):
        self._api_record_stop()
        
    # on_select event for capturing to image
    def on_select_capture_image(self):
        self._api_capture_image(0)
    def on_select_capture_after_10s(self):
        self._api_capture_image(10)
    def on_select_capture_after_20s(self):
        self._api_capture_image(20)
    def on_select_capture_after_30s(self):
        self._api_capture_image(30)

    def on_select_capture_with_keypoints(self):
        self._api_capture_image_keypoints()

                
    # mapi : record start
    def mapi_record_start(self, payload):
        self._api_record_start()

    # mapi : record stop
    def mapi_record_stop(self, payload):
        self._api_record_stop()
                
    # show message on status bar
    def show_on_statusbar(self, text):
        self.statusBar().showMessage(text)
    

    # update image frame on label area
    def update_frame(self, image):
        id = self.sender().camera_id
        pixmap = QPixmap.fromImage(image)
        #window = self.findChild(QLabel, camera_windows[id])
        try:
            window = self.findChild(QLabel, self.configure_param["camera_windows_map"][id])
            window.setPixmap(pixmap.scaled(window.size(), Qt.AspectRatioMode.KeepAspectRatio))
        except Exception as e:
            self.console.warning(f"{e}")
    
    # gpu monitoring update
    def gpu_monitor_update(self, status:dict):
        gpu_usage_window = self.findChild(QProgressBar, "progress_gpu_usage")
        gpu_memory_usage_window = self.findChild(QProgressBar, "progress_gpu_mem_usage")
        gpu_usage_window.setValue(status["gpu_usage"])
        gpu_memory_usage_window.setValue(status["gpu_memory_usage"])


    
    # notification
    def mapi_notify_active(self):
        if self.mq_client.is_connected():
            msg = {"app":APP_NAME, "active":True}
            self.mq_client.publish(mqtt_topic_manager, json.dumps(msg), 0)
        else:
            self.show_on_statusbar("Notified")
    
    # mqtt connection callback function
    def on_mqtt_connect(self, mqttc, obj, flags, rc):
        self.mapi_notify_active()
        
        # subscribe message api
        for topic in self.message_api.keys():
            self.mq_client.subscribe(topic, 0)
        
        self.show_on_statusbar("Connected to Broker({})".format(str(rc)))
    
    # mqtt disconnection callback function
    def on_mqtt_disconnect(self, mqttc, userdata, rc):
        self.show_on_statusbar("Disconnected to Broker({})".format(str(rc)))
    
    # mqtt message receive callback function
    def on_mqtt_message(self, mqttc, userdata, msg):
        mapi = str(msg.topic)
        
        try:
            if mapi in self.message_api.keys():
                payload = json.loads(msg.payload)
                if "app" not in payload:
                    print("Message payload does not contain the app")
                    return
                
                if payload["app"] != APP_NAME:
                    self.message_api[mapi](payload)
            else:
                print("Unknown MAPI was called : {}".format(mapi))
        except json.JSONDecodeError as e:
            print("MAPI message payload connot be converted : {}".format(str(e)))
        