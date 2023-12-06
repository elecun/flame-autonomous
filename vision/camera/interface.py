'''
Camera Device Interface Class
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''


from abc import ABC, abstractmethod

class ICamera(ABC):
    def __init__(self, camera_id:int) -> None:
        super().__init__()
        
        self.camera_id = camera_id
        
    @abstractmethod
    def open(self) -> bool:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass
    
    @abstractmethod
    def grab(self):
        pass