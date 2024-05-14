import socket
import cv2
import torch
import argparse
from io import BytesIO
import numpy as np
from PIL import Image
from train_transunet import TransUNetSeg
import time

from inference import SegInference

from config import cfg

class TCPServer:
    def __init__(self, host, port, model_path, device):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(1)
        self.model_path = model_path
        self.device = device

    def serve(self):
        print("서버가 시작되었습니다.")
        while True:
            client, address = self.server.accept()
            print(f"{address}에서 연결되었습니다.")
            
            # 이미지 데이터 수신
            data = b""
            while len(data) < 307200:
                packet = client.recv(1024)
                if not packet:
                    break
                data += packet
            
            #print(f"받은 데이터 크기: {len(data)} 바이트")
            
            if len(data) == 307200:
                image_array = np.frombuffer(data, dtype=np.uint8)
                image_array = image_array.reshape((480, 640))
                image_array = np.array(image_array)
                image_array = np.stack((image_array,) * 3, axis=-1)
                #print(image_array)
                #filename = f'test.png'
                #cv2.imwrite(filename, image_array)
            # 추론
                inference = SegInference(self.model_path, self.device)
                pred_mask = inference.infer_image(image_array)
                pred_mask = pred_mask * 255
                pred_mask = pred_mask.astype(np.uint8)
                # pred_mask에서 불필요한 차원 제거
                pred_mask_squeezed = np.squeeze(pred_mask)

                # 2D 배열을 1D 배열로 변환
                pred_mask_flattened = pred_mask_squeezed.flatten()
            
            # 추론 결과 전송
                response = pred_mask_flattened.tobytes()
                #print(len(response))
                #print(pred_mask_flattened.shape)
                #print(pred_mask_flattened.dtype)
                client.sendall(response)

class SegInference:
    # 기존 __init__, read_and_preprocess 메소드 생략...
    def __init__(self, model_path, device):
        self.device = device
        self.transunet = TransUNetSeg(device)  # 여기서 모델 초기화가 이루어져야 합니다.
        self.transunet.load_model(model_path)  # 모델 가중치를 불러오는 부분
        
        
        
        self.transunet = TransUNetSeg(device)
        self.transunet.load_model(model_path)
        
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
            print(f"Inference took {formatted_time} milliseconds")
            
            pred_mask = pred_mask.detach().cpu().numpy().transpose((0, 2, 3, 1))
        
        return pred_mask

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, default='./model/model_02.pth')
    parser.add_argument('--port', type=int, default=52525)
    args = parser.parse_args()

    device = 'cuda:0' if torch.cuda.is_available() else 'cpu:0'
    server = TCPServer('192.168.20.2', args.port, args.model_path, device)
    server.serve()