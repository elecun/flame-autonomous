'''
Video Recorder Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import cv2
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
import pathlib
from abc import *

class AbstractVideoRecorder(metaclass=ABCMeta):
    @abstractmethod
    def write(self):
        pass

class VideoRecorder(QObject):
    def __init__(self, dirpath:pathlib.Path, filename:str):
        super().__init__()

        # camera_fps = int(self.grabber.get(cv2.CAP_PROP_FPS))
        # camera_w = int(self.grabber.get(cv2.CAP_PROP_FRAME_WIDTH))
        # camera_h = int(self.grabber.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # fourcc = cv2.VideoWriter_fourcc(*'MJPG') # low compression but bigger (file extension : avi)

        #self.raw_video_writer = cv2.VideoWriter(str(dirpath/filename)), fourcc, CAMERA_RECORD_FPS, (camera_w, camera_h))

    # set frame rate
    def set_fps(self, fps:int):
        pass

    # set frame widht, height
    def set_frame_size(self, widht:int, height:int):
        pass

    def start(self):
        pass
    
    def pause(self):
        pass
    
    def stop(self):
        pass
    
    # write a frame
    def write_frame(self, frame):
        if self.raw_video_writer != None:
            self.raw_video_writer.write(frame)