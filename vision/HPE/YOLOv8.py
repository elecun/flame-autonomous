'''
YOLOv8 Human Pose Estimation Process Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

from vision.iestimator import IVisionEstimator
from ultralytics import YOLO
import pathlib
from util.logger.console import ConsoleLogger

class Model(IVisionEstimator):
    def __init__(self, modelname:str) -> None:
        super().__init__(modelname)
        
        self.console = ConsoleLogger.get_logger()
        
        self.pretrained_model_path = pathlib.Path(__file__).parent / "pretrained"
        self.console.info(f"model path : {self.pretrained_model_path.as_posix()}")
        
        # self.hpe_model = YOLO(model="./model/yolov8x-pose.pt")
        
    def predict(self):
        pass
    
    