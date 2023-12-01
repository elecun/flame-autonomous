'''
System Usage Monitoring
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''


import psutil
from PyQt6.QtCore import QObject, QThread, pyqtSignal
import time


# System Status Monitoring with QThread
class SystemStatusMonitor(QThread):
    
    usage_update_signal = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.usage = {}
    
    def run(self):
        while True:
            if self.isInterruptionRequested():
                break
            
            self.usage["cpu"] = psutil.cpu_percent()
            self.usage["memory"] = psutil.virtual_memory().percent
            self.usage["storage"] = psutil.disk_usage('/').percent
            self.usage["net_send"] = psutil.net_io_counters().bytes_sent
            self.usage["net_recv"] = psutil.net_io_counters().bytes_recv
            
            # emit signal
            self.usage_update_signal.emit(self.usage)
            
            time.sleep(1) # delay 1sec

    # close thread
    def close(self) -> None:
        self.requestInterruption()
        self.quit()
        self.wait(1000)