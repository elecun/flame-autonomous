'''
General USB Interface Camera Controller Class
@author Byunghun Hwang <bh.hwang@iae.re.kr>
'''

from PyQt6.QtCore import QObject, Qt, QTimer, QThread, pyqtSignal

class Controller(QThread):

    def __init__(self, camera_id):
        super().__init__()