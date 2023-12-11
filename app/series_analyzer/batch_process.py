'''
Batch Process to create Spectogram
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''


from PyQt6.QtCore import QObject, QThread
from joblib import Parallel, delayed

class BatchProcessParallel:
    def __init__(self, files:list[str]) -> None:
        super().__init__()
        
        self.__file_container = files
    
    # run in parallel
    def do_process(self, process_func):
        Parallel(n_jobs=-1, prefer="threads")(delayed(process_func)(k) for k in self.__file_container)