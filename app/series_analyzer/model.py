'''
Purge Fan Fault Classification(Binary) Model using Residual Network with Pytorch
@author Byunghun Hwang<bh.hwang@iae.re.kr>
'''
import torch
import torchvision
import torchvision.models as models
import pathlib
import os
from typing import Union
import argparse

from util.logger.console import ConsoleLogger


ROOT_PATH = pathlib.Path(__file__).parent


# Model Base Class
class ClassificationBase(torch.nn.Module):
    def accuracy(outputs, labels):
        _, preds = torch.max(outputs, dim=1)
        return torch.tensor(torch.sum(preds == labels).item() / len(preds))

    def training_step(self, batch):
        images, labels = batch 
        out = self(images)                  # Generate predictions
        loss = torch.nn.functional.cross_entropy(out, labels) # Calculate loss
        acc = self.accuracy(out, labels)  
        return loss,acc
    
    def validation_step(self, batch):
        images, labels = batch 
        out = self(images)                    # Generate predictions
        loss = torch.nn.functional.cross_entropy(out, labels)   # Calculate loss
        acc = self.accuracy(out, labels)           # Calculate accuracy
        return {'val_loss': loss.detach(), 'val_acc': acc}
        
    def validation_epoch_end(self, outputs):
        batch_losses = [x['val_loss'] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()   # Combine losses
        batch_accs = [x['val_acc'] for x in outputs]
        epoch_acc = torch.stack(batch_accs).mean()      # Combine accuracies
        return {'val_loss': epoch_loss.item(), 'val_acc': epoch_acc.item()}

# Resnet model
class ResNet9(ClassificationBase):
    def __init__(self, in_channels, num_classes):
        super().__init__()
        
        self.conv1 = self.conv_block(in_channels, 64)
        self.conv2 = self.conv_block(64, 128, pool=True)
        self.res1 = torch.nn.Sequential(self.conv_block(128, 128), self.conv_block(128, 128))
        
        self.conv3 = self.conv_block(128, 256, pool=True)
        self.conv4 = self.conv_block(256, 512, pool=True)
        self.res2 = torch.nn.Sequential(self.conv_block(512, 512), self.conv_block(512, 512))
        
        self.classifier = torch.nn.Sequential(self.torch.nn.AdaptiveMaxPool2d((1,1)), 
                                        torch.nn.Flatten(), 
                                        torch.nn.Dropout(0.2),
                                        torch.nn.Linear(512, num_classes))
        
    # design residual model
    def conv_block(in_channels, out_channels, pool=False):
        layers = [torch.nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1), 
                torch.nn.BatchNorm2d(out_channels), 
                torch.nn.ReLU(inplace=True)]
        if pool: layers.append(torch.nn.MaxPool2d(2))
        return torch.nn.Sequential(*layers)
    
    # feed forward    
    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.res1(out) + out
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.res2(out) + out
        out = self.classifier(out)
        return out
    

# ResNet
class PurgeFanFaultClassification_Resnet:
    def __init__(self) -> None:
        
        # for logging
        self.__console = ConsoleLogger.get_logger()
        
        self.__model = None # torch model instance
        self.__device = None # device to perform
        self.__model_path = pathlib.Path(__file__).parent / "model" / "resnet9_pfc_v1.pth"
        self.__console.info(f"Model : {self.__model_path.as_posix()}")
        
        if os.path.isfile(self.__model_path.as_posix()):
            self.__device = self.get_default_device()
            self.__model = self.to_device(ResNet9(3, 2), self.__device)
            self.__console.info("PurgeFan Fault Classification Model(ResNet-9) is now loaded")
        
        else:
            self.__console.critical("PurgeFan Fault Classification Model is not exist")
    
    # device to perform        
    def get_default_device(self):
        if torch.cuda.is_available():
            self.__console.info("CUDA Device is selected")
            return torch.device('cuda')
        elif torch.backends.mps.is_available():
            self.__console.info("MPS Device is selected")
            return torch.device('mps')
        else:
            self.__console.info("CPU Device is selected")
            return torch.device('cpu')
            
    def to_device(self, data, device):
        if isinstance(data, (list, tuple)):
            return [self.to_device(x, device) for x in data]
        return data.to(device, non_blocking=True)
            
    # model inference (True=Fault, False=Normal)
    def predict(self, image_path:Union[pathlib.Path, str, None]) -> bool:
        print(image_path)
        print(self.__model)
        if self.__model is not None:
            if image_path == None:
                self.__console.info("read tmo image")
            return False
            #xb = self.to_device(image.unsqueeze(0), self.__device)
        return False
    
    
    def predict_image(img, model):
        # Convert to a batch of 1
        xb = to_device(img.unsqueeze(0), device)
        # Get predictions from model
        model.eval()
        with torch.no_grad():
            yb = model(xb)
        # Pick index with highest probability
        _, preds  = torch.max(yb, dim=1)
        # Retrieve the class label
        return train_ds.classes[preds[0].item()]
    

# entry point    
if __name__ ==" __main__":
    console = ConsoleLogger.get_logger()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', nargs='?', required=False, help="Dataset Path", default=f"{(ROOT_PATH/'dataset').as_posix()}")
    parser.add_argument('--epoch', nargs='?', required=False, help="Epoch", default="10")
    args = parser.parse_args()
    
    try:
        pass
    
    except Exception as e:
        console.critical(f"{e}")