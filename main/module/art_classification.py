import torch
import torch.nn as nn
from torchvision import transforms

import os

import numpy as np
from PIL import Image


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# define vgg network
classification_vgg = nn.Sequential(
    nn.Conv2d(3, 3, (1, 1)),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(3, 64, (3, 3)),
    nn.ReLU(), # relu1-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 64, (3, 3)),
    nn.ReLU(), # relu1-2
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(64, 128, (3, 3)),
    nn.ReLU(), # relu2-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 128, (3, 3)),
    nn.ReLU(), # relu2-2
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(128, 256, (3, 3)),
    nn.ReLU(), # relu3-1
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(), # relu3-2
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(), # relu3-3
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 256, (3, 3)),
    nn.ReLU(), # relu3-4
    nn.MaxPool2d((2, 2), (2, 2), (0, 0), ceil_mode=True),
    nn.ReflectionPad2d((1, 1, 1, 1)),
    nn.Conv2d(256, 512, (3, 3)),
    nn.ReLU(), # relu4-1
)

classification_vgg.eval()
classification_vgg.to(device)


# define Classification model
class Classification(nn.Module):
    def __init__(self):
        super(Classification, self).__init__()
        self.vgg = classification_vgg
        
        self.fc1 = nn.Linear(512 * 16 * 16, 100, bias=True)
        torch.nn.init.xavier_uniform_(self.fc1.weight)

        self.fc2 = nn.Linear(100, 30, bias=True)
        torch.nn.init.xavier_uniform_(self.fc2.weight)
        
        self.fc3 = nn.Linear(30, 5, bias=True)
        torch.nn.init.xavier_uniform_(self.fc3.weight)
        
        self.relu = nn.LeakyReLU(0.2)
        
    def forward(self, x):
        out = self.vgg(x)
        out = out.view(out.size(0), -1)
        out = self.fc1(out)
        out = self.fc2(out)
        out = self.fc3(out)
        out = self.relu(out)
        
        return out



art_model = Classification()
art_model.load_state_dict(torch.load(f"{os.getcwd()}\\main\\pre-trained\\art_classification.pkl"))
art_model.to(device)


# x shape of (128, 128)
def preprocessing(x):

    result = np.repeat(np.array(x), 3).reshape(128, 128, 3)
    
    result = Image.fromarray(np.uint8(result)).convert("RGB")
    result = transforms.Compose([transforms.ToTensor()])(result).unsqueeze(0)

    return result


# x shape of (1, 3, 128, 128)
def predict(x):
    label_dir = {0: "abstract", 1:"cityscape", 2:"landscape", 3:"portrait", 4:"still-life"}

    predict = torch.argmax(art_model(x)).item()
    predict_label = label_dir[predict]

    return predict_label
