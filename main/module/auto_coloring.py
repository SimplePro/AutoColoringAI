import torch
import gc
from torchvision import transforms
import numpy as np
from PIL import Image
import load_vgg_decoder
import os


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
vgg, decoder = load_vgg_decoder.load(vgg_path=f"{os.getcwd()}\\main\\pre-trained\\vgg_normalised.pth",
                                    decoder_path=f"{os.getcwd()}\\main\\pre-trained\\decoder.pth", device=device)


class AutoColoring:
    def __init__(self, content_path, style_paths, weights):
        self.content_img = Image.open(content_path).convert("RGB").resize((128, 128))
        self.style_imgs = [Image.open(style_path).convert("RGB").resize((128, 128)) for style_path in style_paths]

        self.weights = weights
        
        
    # this method return result after preprocess
    # shape of (1, 3, 128, 128) -> shape of (128, 128, 3)
    def decode3shape(self, coloring_result):
        coloring_result = coloring_result[0]
        
        result = np.zeros((128, 128, 3))
        
        for i in range(128):
            for j in range(128):
                result[i, j] = coloring_result[:, i, j]
                
        return result
    
    
    # this method return the transform object
    def transform(self):
        return transforms.Compose([transforms.ToTensor()])
    
    
    # this method return the features statistics of mean and standard-deviation.
    def style_(self, feature, eps=1e-5):
        N, C = feature.size()[:2]

        feature = feature.reshape(N, C, -1)

        mean = feature.mean(dim=2).reshape(N, C, 1, 1)
        std = (feature.var(dim=2) + eps).sqrt().reshape(N, C, 1, 1)

        return mean, std
    
    
    # adain_normalization
    # style transfer
    def adain_normalization(self, content_f, style_f):
        size = content_f.size()

        style_mean, style_std = self.style_(style_f)
        content_mean, content_std = self.style_(content_f)

        style_mean, style_std = style_mean.expand(size), style_std.expand(size)
        content_mean, content_std = content_mean.expand(size), content_std.expand(size)

        normalized_f = (content_f - content_mean) / content_std
        normalized_f = style_std * normalized_f + style_mean

        return normalized_f
    
    
    # multiple style transfer
    def interpolation(self, content, styles):
        content_f = vgg(content)
        style_fs = [vgg(style) for style in styles]

        feature = sum([self.weights[i] * self.adain_normalization(content_f, style_fs[i]) for i in range(len(style_fs))])

        return decoder(feature)
    
    
    # this method return the result after AutoColoring
    def result_(self):
        content = self.transform()(self.content_img).to(device).unsqueeze(0)
        styles = []
        for i in range(len(self.style_imgs)):
            styles.append(self.transform()(self.style_imgs[i]).to(device).unsqueeze(0))
            
        coloring_result = self.interpolation(content, styles)
                            
        torch.cuda.empty_cache()
        gc.collect()
                                        
        coloring_result = coloring_result.cpu().detach().numpy()
        
        coloring_result = self.decode3shape(coloring_result)
        
        return coloring_result