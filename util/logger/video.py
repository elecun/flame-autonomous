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
    def __init__(self, dirname:pathlib.Path, filename:str):
        super().__init__()

        self.raw_video_writer = cv2.VideoWriter(str(self.data_out_path/f'cam_{self.camera_id}.{VIDEO_FILE_EXT}'), fourcc, CAMERA_RECORD_FPS, (camera_w, camera_h))

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