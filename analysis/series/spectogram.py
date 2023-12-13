'''
Spectogram Generation with librosa
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''


from PIL import Image
import pandas as pd
import numpy as np
import librosa
import pathlib
import pyqtgraph as graph
import cv2
import os

from util.logger.console import ConsoleLogger


class Spectogram:
    def __init__(self) -> None:
        self.__console = ConsoleLogger.get_logger()
    
    
    # spectogram image generation
    def generate_to_image(self, csv_file_in:str, out_path:str, fs:int, opt_resize:bool):
        
        try:
            filename = pathlib.Path(csv_file_in).stem
            # read csv
            __csv_raw = pd.read_csv(csv_file_in)
            
            __csv_mean = __csv_raw.mean()
            __csv_normalized = __csv_raw - __csv_mean
            
            
            # create directory
            for idx, ch in enumerate(__csv_raw.columns):
                (pathlib.Path(out_path) / ch).mkdir(parents=True, exist_ok=True)
            
            # generate spectogram
            for idx, ch in enumerate(__csv_raw.columns):
                _data = np.transpose(__csv_normalized[ch])
                
                graph.setConfigOptions(imageAxisOrder='row-major')
                stft = librosa.stft(y=_data.to_numpy(), win_length=None, hop_length=1, window='hann', n_fft=fs)
                magnitude = np.abs(stft)
                
                db = librosa.amplitude_to_db(magnitude, ref=np.max)
                
                image = graph.ImageItem(image=magnitude)
                cmap = graph.colormap.getFromMatplotlib("jet")
                image.setColorMap(colorMap=cmap)
                
                # save image
                rawfile = pathlib.Path(out_path)/ch/f"{filename}_raw.png"
                image.save(rawfile.as_posix())
                
                outfile = pathlib.Path(out_path)/ch/f"{filename}.png"
                raw_image = cv2.imread(rawfile.as_posix())
                flipped = cv2.flip(raw_image, 0)
                
                # resize option
                if opt_resize:
                    resized = cv2.resize(flipped, (500, 500))
                    cv2.imwrite(outfile.as_posix(), resized)
                else:
                    cv2.imwrite(outfile.as_posix(), flipped)
                
                # remove temporary raw file
                try:
                    os.remove(rawfile.as_posix())
                    
                except FileNotFoundError:
                    self.__console.critical(f"Cannot found {rawfile.stem}")
                except Exception as e:
                    self.__console.critical(f"e")
            
        except Exception as e:
            self.__console.critical(f"{e}")