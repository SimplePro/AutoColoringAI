import torch
import torch.nn as nn
from torchvision import transforms
import numpy as np
from PIL import Image

from get_abspath import main_abspath

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


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

        self.fc2 = nn.Linear(100, 50, bias=True)
        torch.nn.init.xavier_uniform_(self.fc2.weight)
        
        self.fc3 = nn.Linear(50, 3, bias=True)
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
art_model.load_state_dict(torch.load(f"{main_abspath()}/pre-trained/art_classification.pkl"))
art_model.to(device)


# x shape is (128, 128), input type is PIL.Image, x that is return type is torch.tensor
def preprocessing(x):

    result = np.repeat(np.array(x), 3).reshape((128, 128, 3))
    
    result = Image.fromarray(np.uint8(result)).convert("RGB")
    result = transforms.Compose([transforms.ToTensor()])(result).unsqueeze(0)

    return result


# x shape of (1, 3, 128, 128)
def predict(x):
    label_dir = {0: "cityscape", 1: "landscape", 2: "portrait"}

    pred = torch.argmax(art_model(x)).item()
    predict_label = label_dir[pred]

    return predict_label


# ????????? ????????? ???????????? predict ??? ????????????.
def result_(img_path):
    img = Image.open(img_path).convert("L").resize((128, 128))

    img = preprocessing(img).to(device)
    label = predict(img)

    return label


# ??? ???????????? ????????? ???????????? mse loss ?????? ????????????.
def mse_loss(img1_p, img2_p):
    img1 = Image.open(img1_p).convert("L").resize((128, 128))
    img2 = Image.open(img2_p).convert("L").resize((128, 128))

    img1 = preprocessing(img1).to(device)
    img2 = preprocessing(img2).to(device)

    img1_feature = art_model.vgg(img1).cpu().detach().numpy().reshape(-1)
    img2_feature = art_model.vgg(img2).cpu().detach().numpy().reshape(-1)

    loss = np.square(img1_feature - img2_feature).mean()

    return loss


if __name__ == '__main__':
    import get_abspath

    project_path = get_abspath.project_abspath()

    img_path = f"{project_path}/dataset/test/cityscape/(6001).jpg"

    test_label = result_(img_path)
    print(test_label)

    import time
    import os

    start_time = time.time()

    dir = os.listdir(f"{project_path}/dataset/test/cityscape/")
    print(len(dir))

    for path in dir:
        print(mse_loss(f"{project_path}/dataset/test/cityscape/(6001).jpg", f"{project_path}/dataset/test/cityscape/{path}"))

    print(time.time() - start_time)
