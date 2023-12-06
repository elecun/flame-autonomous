'''
Vision Estimator Abstract Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''

from abc import ABC, abstractmethod

class IVisionEstimator(ABC):
    def __init__(self, name:str) -> None:
        super().__init__()
        
        self.name = name
    
    @abstractmethod
    def predict(self):
        pass