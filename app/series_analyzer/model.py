'''
Deep Learning Models
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''
import torch
import torchvision.models as models
import pathlib
import os

from util.logger.console import ConsoleLogger



# Resnet-9 model (light model)
class FaultDetection_Resnet:
    def __init__(self) -> None:
        
        self.__console = ConsoleLogger.get_logger()
        
        self.__model = None # torch model instance
        self.__pretrained_path = pathlib.Path(__file__).parent / "pretrained"
        modelfiles = [(self.__pretrained_path/f).as_posix() for f in os.listdir(self.__pretrained_path) if f.endswith('.pt')]
        self.__console.info(f"Pretrained Model Path : {self.__pretrained_path.as_posix()}")
        
        # if method.lower == "resnet":
        #     if "ad_resnet18.pt" in modelfiles:
        #         self.__model = models.resnet18()
        #         self.__model.load_state_dict(torch.load((self.__pretrained_path/"ad_resnet18.pt").as_posix()))
        #         self.__model.eval() # evaluation mode
        #     else:
        #         self.__console.critical("No model found")
    
        
    # model prediction (True=Abnormal, False=Normal)
    def predict(self) -> bool:
        
        return True