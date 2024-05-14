import sys
import torch
import argparse

# Additional Scripts
from train import TrainTestPipe
from inference import SegInference


def main_pipeline(parser):
    device = 'cpu:0'
    if torch.cuda.is_available():
        device = 'cuda:0'

    if parser.mode == 'train':
        ttp = TrainTestPipe(train_path=parser.train_path,
                            test_path=parser.test_path,
                            model_path=parser.model_path,
                            device=device)

        ttp.train()

    elif parser.mode == 'inference':
        inf = SegInference(model_path=parser.model_path,
                           device=device)
        
        #_ = inf.infer(parser.image_path)
        _ = inf.infer_folder(parser.image_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', type=str, choices=['train', 'inference'], default='train')
    parser.add_argument('--model_path', type=str, default='./model/model_irt_01.pth')
    parser.add_argument('--train_path', type=str, default='./dataset_IRT2/train')
    parser.add_argument('--test_path', type=str, default='./dataset_IRT2/val')
    parser.add_argument('--image_path', type=str, default=None)
    
    parser = parser.parse_args()

    main_pipeline(parser)
