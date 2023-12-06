'''
General USB Interface Camera Controller Class
@author Byunghun Hwang <bh.hwang@iae.re.kr>
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


# camera device class
class UVC(ICamera):
    def __init__(self, camera_id: int) -> None:
        super().__init__(camera_id)
        
        self.camera_id = camera_id  # camera ID
        self.grabber = None         # device instance
        self.console = ConsoleLogger.get_logger()
    
    # open camera device    
    def open(self) -> bool:
        try:
            os_system = platform.system()
            if os_system == "Darwin": #MacOS
                self.grabber = cv2.VideoCapture(self.camera_id)
            elif os_system == "Linux": # Linux
                self.grabber = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2) # video capture instance with opencv
            elif os_system == "Windows":
                self.grabber = cv2.VideoCapture(self.camera_id)
            else:
                raise Exception("Unsupported Camera")

            if not self.grabber.isOpened():
                return False
        
            self.is_recording = False

        except Exception as e:
            self.console.critical(f"{e}")
            return False
        return True
    
    # close camera device
    def close(self) -> None:
        if self.grabber:
            self.grabber.release()
    
    # captrue image
    def grab(self):
        ret, frame = self.grabber.read() # grab

        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb
        return None

# camera controller class
class Controller(QThread):

    frame_update_signal = pyqtSignal(np.ndarray, float)

    def __init__(self, camera_id:int):
        super().__init__()
        
        self.console = ConsoleLogger.get_logger()   # console logger
        self.uvc_camera = UVC(camera_id)    # UVC camera device

        self.is_recording = False   # video recording status
        self.raw_video_writer = None    # raw video writer
        
    def get_camera_id(self) -> int:
        return self.uvc_camera.camera_id

    # camera device open
    def open(self) -> bool:
        try:
            os_system = platform.system()
            if os_system == "Darwin": #MacOS
                self.grabber = cv2.VideoCapture(self.uvc_camera.camera_id)
            elif os_system == "Linux": # Linux
                self.grabber = cv2.VideoCapture(self.uvc_camera.camera_id, cv2.CAP_V4L2) # video capture instance with opencv
            elif os_system == "Windows":
                self.grabber = cv2.VideoCapture(self.uvc_camera.camera_id)
            else:
                raise Exception("Unsupported Camera")

            if not self.grabber.isOpened():
                return False
        
            self.is_recording = False

        except Exception as e:
            print(f"Exception : {e}")
            return False
        return True
    
    # camera device close
    def close(self) -> None:
        self.requestInterruption() # to quit for thread
        self.quit()
        self.wait(1000)

        # release grabber
        self.uvc_camera.close()
        self.console.info(f"camera {self.uvc_camera.camera_id} controller is closed")

    # start thread
    def begin(self):
        if self.grabber.isOpened():
            self.start()
    
    # return camera id
    def __str__(self):
        return str(self.uvc_camera.camera_id)
    
    def grab(self):
        pass
    
    # image grab with thread
    def run(self):
        while True:
            if self.isInterruptionRequested():
                break
            
            t_start = datetime.now()
            _, frame = self.grabber.read() # grab

            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # warning! it should be converted from BGR to RGB. But each camera IR turns ON, grayscale is able to use. (grayscale is optional)
                # video recording
                # if self.raw_video_recorder != None:
                #     self.raw_video_recorder.write_frame(frame)
                
                t_end = datetime.now()
                framerate = float(1./(t_end - t_start).total_seconds())
                #cv2.putText(frame_rgb, f"Camera #{self.camera_id}(fps:{framerate}, processing time:{int(results[0].speed['preprocess']+results[0].speed['inference']+results[0].speed['postprocess'])}ms)", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
                #cv2.putText(frame_rgb, t_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], (10, 1070), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)

                _h, _w, _ch = frame_rgb.shape
                _bpl = _ch*_w # bytes per line
                qt_image = QImage(frame_rgb.data, _w, _h, _bpl, QImage.Format.Format_RGB888)
                #self.frame_update_signal.emit(qt_image, framerate) # emit frame signal
                self.frame_update_signal.emit(frame_rgb, framerate)

    # write raw video stream data
    def raw_video_record(self, frame):
        if self.raw_video_writer != None:
            self.raw_video_writer.write(frame)

    # ready to start video recording
    def start_recording(self):
        if not self.is_recording:
            #if self.raw_video_recorder!=None:
                # create video writer

                # camera_fps = int(self.grabber.get(cv2.CAP_PROP_FPS))
                # camera_w = int(self.grabber.get(cv2.CAP_PROP_FRAME_WIDTH))
                # camera_h = int(self.grabber.get(cv2.CAP_PROP_FRAME_HEIGHT))
                # fourcc = cv2.VideoWriter_fourcc(*'MJPG') # low compression but bigger (file extension : avi)

            # start working on thread
            self.is_recording = True # working on thread
        else:
            self.console.warning(f"Already raw video is recording...")
    
