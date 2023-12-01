'''
Camera Controller Class
@author Byunghun Hwang <bh.hwang@iae.re.kr>
'''

from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QImage

from util.logger.video import VideoRecorder


class Controller(QThread):
    def __init__(self):
        super().__init__()

    def run(self):
        pass