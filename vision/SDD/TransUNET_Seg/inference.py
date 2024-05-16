import os
import cv2
import torch
import numpy as np
import datetime

# Additional Scripts
from .train_transunet import TransUNetSeg
from .utils import thresh_func
from .config import cfg
import time


class SegInference:
    def __init__(self, model_path, device):
        self.device = device
        self.transunet = TransUNetSeg(device)
        self.transunet.load_model(model_path)

        if not os.path.exists('./results'):
            os.mkdir('./results')

    def read_and_preprocess(self, p):
        img = cv2.imread(p)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(p)
        img_torch = cv2.resize(img, (cfg.transunet.img_dim, cfg.transunet.img_dim))
        img_torch = img_torch / 255.
        img_torch = img_torch.transpose((2, 0, 1))
        img_torch = np.expand_dims(img_torch, axis=0)
        img_torch = torch.from_numpy(img_torch.astype('float32')).to(self.device)

        return img, img_torch

    def save_preds(self, preds):
        folder_path = './results/' #+ str(datetime.datetime.utcnow()).replace(':', '_')

        #os.mkdir(folder_path)
        #print(folder_path)
        for name, pred_mask in preds.items():
            cv2.imwrite(f'{folder_path}/{name}', pred_mask)
        print(f'{folder_path}/{name}')

    def infer(self, path, merged=False, save=True):
        path = [path] if isinstance(path, str) else path

        preds = {}
        for p in path:
            file_name = p.split('/')[-1]
            img, img_torch = self.read_and_preprocess(p)
            with torch.no_grad():
                pred_mask = self.transunet.model(img_torch)
                pred_mask = torch.sigmoid(pred_mask)
                pred_mask = pred_mask.detach().cpu().numpy().transpose((0, 2, 3, 1))

            orig_h, orig_w = img.shape[:2]
            pred_mask = cv2.resize(pred_mask[0, ...], (orig_w, orig_h))
            pred_mask = thresh_func(pred_mask, thresh=cfg.inference_threshold)
            pred_mask *= 255

            if merged:
                pred_mask = cv2.bitwise_and(img, img, mask=pred_mask.astype('uint8'))

            preds[file_name] = pred_mask

        if save:
            self.save_preds(preds)

        return preds
        
    def infer_folder(self, folder_path, merged=False, save=True):
    # 폴더 내의 모든 파일을 가져옵니다.
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

        preds = {}
        for file_path in files:
            file_name = os.path.basename(file_path)
            img, img_torch = self.read_and_preprocess(file_path)
            with torch.no_grad():
                pred_mask = self.transunet.model(img_torch)
                pred_mask = torch.sigmoid(pred_mask)
                pred_mask = pred_mask.detach().cpu().numpy().transpose((0, 2, 3, 1))

            orig_h, orig_w = img.shape[:2]
            pred_mask = cv2.resize(pred_mask[0, ...], (orig_w, orig_h))
            pred_mask = thresh_func(pred_mask, thresh=cfg.inference_threshold)
            pred_mask *= 255

            if merged:
                pred_mask = cv2.bitwise_and(img, img, mask=pred_mask.astype('uint8'))

            preds[file_name] = pred_mask

        if save:
            self.save_preds(preds)

        return preds

    def infer_image(self, img):
        # 이미지 전처리
        img_torch = cv2.resize(img, (cfg.transunet.img_dim, cfg.transunet.img_dim))
        img_torch = img_torch / 255.
        img_torch = img_torch.transpose((2, 0, 1))
        img_torch = np.expand_dims(img_torch, axis=0)
        img_torch = torch.from_numpy(img_torch.astype('float32')).to(self.device)
        
        # 추론
        with torch.no_grad():
            start_time = time.perf_counter()
            pred_mask = self.transunet.model(img_torch)
            pred_mask = torch.sigmoid(pred_mask)
            end_time = time.perf_counter()
            elapsed_time = (end_time - start_time) * 1000  # 밀리초로 변환

            formatted_time = "{:.2f}".format(elapsed_time)
            #print(f"Inference took {formatted_time} milliseconds")
            
            pred_mask = pred_mask.detach().cpu().numpy().transpose((0, 2, 3, 1))
        
        return pred_mask