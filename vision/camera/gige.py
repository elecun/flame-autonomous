'''
Gigabit Ethernet interface camera device class
@Author <bh.hwang@iae.re.kr>
'''

from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage
import cv2
from datetime import datetime
from util.logger.video import VideoRecorder
import platform
from util.logger.console import ConsoleLogger
from vision.camera.interface import ICamera
import numpy as np
from pypylon import genicam
from pypylon import pylon

#(Note) acA1300-60gc = 125MHz(PTP disabled), 1 Tick = 8ns
#(Note) a2A1920-51gmPRO = 1GHZ, 1 Tick = 1ns
CAMERA_TICK_TIME = 8 

# global variable for camera array
_camera_array_container = None

# camera device class
class GigE_Basler(ICamera):
    def __init__(self, camera_id: int) -> None:
        super().__init__(camera_id)
        
        self.camera_id = camera_id  # camera ID
        self.__grabber = None         # device instance
        self.__console = ConsoleLogger.get_logger()
        
    # open device
    def open(self) -> bool:
        try:
            
            # open camera
            
            if not self.__grabber.isOpened():
                    return False
            
        except Exception as e:
            self.__console.critical(f"{e}")
            return False
        return True
    
    # close camera
    def close(self) -> None:
        if self.__grabber:
            self.__grabber.release()
            
        return super().close()
    
    # captrue image
    def grab(self):
        return self.__grabber.read() # grab
    
    # check device open
    def is_opened(self) -> bool:
        return self.__grabber.isOpened()

    
# camera controller class
class Controller(QThread):
    
    frame_update_signal = pyqtSignal(np.ndarray, float) # to gui and process
    
    def __init__(self, camera_id:int):
        super().__init__()
        
        self.__console = ConsoleLogger.get_logger()
        self.__camera = GigE_Basler(camera_id)
        self.__container = None
        
    # getting camera id
    def get_camera_id(self) -> int:
        return self.__camera.camera_id
    
    # camera open
    def open(self) -> bool:
        try:
            return self.__camera.open()
        except Exception as e:
            self.__console.critical(f"{e}")
            
        return False
    
    # camera close
    def close(self) -> None:
        self.requestInterruption() # to quit for thread
        self.quit()
        self.wait(1000)

        # release grabber
        self.__camera.close()
        self.__console.info(f"camera {self.__camera.camera_id} controller is closed")
        
     # start thread
    def begin(self):
        if self.__camera.is_opened():
            self.start()
        else:
            self.__console.warning("Camera is not ready")
            
    # return camera id
    def __str__(self):
        return str(self.__camera.camera_id)
    
    def grab(self):
        return self.__camera.grab()
    
    # image grab with thread
    def run(self):
        while True:
            if self.isInterruptionRequested():
                break
            
            t_start = datetime.now()
            ret, frame = self.__camera.grab()

            if ret:                
                t_end = datetime.now()
                framerate = float(1./(t_end - t_start).total_seconds())

                self.frame_update_signal.emit(frame, framerate)
    
    # find cameraes
    @staticmethod
    def discovery():
        _tlf = pylon.TlFactory.GetInstance()
        _devices = _tlf.EnumerateDevices()
        print(f"Found {len(_devices)} Camera(s)")
        if len(_devices)==0:
            raise pylon.RuntimeException("No cameras present")
        
        # setup camera array
        Controller.__container = pylon.InstantCameraArray(len(_devices))
        
        for idx, camera in enumerate(_camera_container):
            if not camera.IsPylonDeviceAttached():
                camera.Attach(_tlf.CreateDevice(_devices[idx]))
                # camera.Open()
                print("Found device ", camera.GetDeviceInfo().GetFullName())
                
        # select one
        _camera_container.StartGrabbing(pylon.GrabStrategy_LatestImageOnly, pylon.GrabLoop_ProvidedByUser)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByUser)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_UpcomingImage, pylon.GrabLoop_ProvidedByUser)
        #_camera_container.StartGrabbing(pylon.GrabStrategy_LatestImages)

        # convert pylon image to opencv BGR format
        _converter = pylon.ImageFormatConverter()
        _converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        _converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        
        return len(_devices) 
        
'''
Camera Finder to discover GigE Cameras
'''   
def gige_camera_discovery() -> list:
    
    _cam_array = []
    
    # reset camera array
    global _camera_array_container
    if _camera_array_container != None:
        _camera_array_container.StopGrabbing()
        _camera_array_container.Close()
    
    try:
        # find camera
        _tlf = pylon.TlFactory.GetInstance()
        _devices = _tlf.EnumerateDevices()
        
        if len(_devices)==0:
            raise pylon.RuntimeException("No cameras present")
        
        _camera_array_container = pylon.InstantCameraArray(len(_devices))
        
        for idx, camera in enumerate(_camera_array_container):
            if not camera.IsPylonDeviceAttached():
                _cam_array.append(tuple(idx, camera.GetFullName(), camera.GetIpAddress()))
                camera.Attach(_tlf.CreateDevice(_devices[idx]))
        
    except Exception as e:
        print(f"{e}")
        
    return _cam_array
    
        