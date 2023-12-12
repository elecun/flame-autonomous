'''
Spectogram Generation with librosa
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''


from PIL import Image
import pandas as pd
import numpy as np
import librosa
import pathlib

from util.logger.console import ConsoleLogger


class Spectogram:
    def __init__(self) -> None:
        self.__console = ConsoleLogger.get_logger()
    
    
    # spectogram image generation
    def generate_to_image(self, csv_file_in:str, out_path:str, fs:int):
        
        try:
            filename = pathlib.Path(csv_file_in).stem
            # read csv
            __csv_raw = pd.read_csv(csv_file_in)
            
            __csv_mean = __csv_raw.mean()
            __csv_normalized = __csv_raw - __csv_mean
            
            for idx, ch in enumerate(__csv_raw.columns):
                _data = np.transpose(__csv_normalized[ch])
                
                stft = librosa.stft(y=_data.to_numpy(), win_length=fs, hop_length=1, window='hann', n_fft=fs)
                magnitude = np.abs(stft)
                
                scaled_data = np.round(255 * ((magnitude - np.min(magnitude)) / (np.max(magnitude) - np.min(magnitude))))
                
                
                print(scaled_data)
                image = Image.fromarray(scaled_data)
                outfile = pathlib.Path(out_path)/f"{filename}_{ch}.tiff"
                image.save(outfile)
            
        except Exception as e:
            self.__console.critical(f"{e}")