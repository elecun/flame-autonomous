'''
Defect Classification Mdoel with Residual Network
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

import pathlib
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
import cv2

from util.logger.console import ConsoleLogger
from vision.iestimator import IVisionEstimator

class ResNet9(QObject):
    
    def __init__(self, modelname:str, id:int) -> None:
        super().__init__()
        
        self.__console = ConsoleLogger.get_logger()