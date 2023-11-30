'''
General USB Interface Camera Controller Class
@author Byunghun Hwang <bh.hwang@iae.re.kr>
'''

from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage
import cv2
from datetime import datetime
from util.logger.video import VideoRecorder

class Controller(QThread):

    def __init__(self, camera_id:int, recorder:VideoRecorder=None):
        super().__init__()

        self.camera_id = camera_id  # camera ID
        self.grabber = None         # device instance
        self.is_recording = False   # video recording status
        self.raw_video_recorder = recorder
        self.raw_video_writer = None    # raw video writer

    # camera device open
    def open(self) -> bool:
        try:
            self.grabber = cv2.VideoCapture(self.camera_id, cv2.CAP_V4L2) # video capture instance with opencv
            if not self.grabber.isOpened():
                return False
            
            print(f"Camera {self.camera_id} is now connected")
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
        self.grabber.release()
        print(f"camera {self.camera_id} controller is terminated successfully")

    # start thread
    def begin(self):
        if self.grabber.isOpened():
            self.start()
    
    # return camera id
    def __str__(self):
        return str(self.camera_id)
    

    # image grab with thread
    def run(self):
        while True:
            if self.isInterruptionRequested():
                print(f"camera {self.camera_id} controller worker is interrupted")
                break
            
            t_start = datetime.now()
            _, frame = self.grabber.read() # grab

            if frame is not None:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # warning! it should be converted from BGR to RGB. But each camera IR turns ON, grayscale is able to use. (grayscale is optional)
                
                # video recording
                if self.raw_video_recorder != None:
                    self.raw_video_recorder.write_frame(frame)
                
                t_end = datetime.now()
                framerate = int(1./(t_end - t_start).total_seconds())
                #cv2.putText(frame_rgb, f"Camera #{self.camera_id}(fps:{framerate}, processing time:{int(results[0].speed['preprocess']+results[0].speed['inference']+results[0].speed['postprocess'])}ms)", (10,50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)
                #cv2.putText(frame_rgb, t_start.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], (10, 1070), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,255,0), 2, cv2.LINE_AA)

                _h, _w, _ch = frame_rgb.shape
                _bpl = _ch*_w # bytes per line
                qt_image = QImage(frame_rgb.data, _w, _h, _bpl, QImage.Format.Format_RGB888)
                self.image_frame_slot.emit(qt_image)

    # write raw video stream data
    def raw_video_record(self, frame):
        if self.raw_video_writer != None:
            self.raw_video_writer.write(frame)

    # ready to start video recording
    def start_recording(self):
        if not self.is_recording:
            
            # create video writer

            # start working on thread
            self.is_recording = True # working on thread
        else:
            print("Exception : Already raw video is recording...")
    
