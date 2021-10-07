import torch
import gc
from torchvision import transforms
import numpy as np
from PIL import Image
import load_vgg_decoder

import warnings

warnings.filterwarnings("ignore", category=UserWarning)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class AutoColoring:

    def __init__(self, content_path, style_paths, size, weights):
        self.content_img = Image.open(content_path).convert("RGB").resize(size)
        self.style_imgs = [Image.open(style_path).convert("RGB").resize(size) for style_path in style_paths]

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.vgg, self.decoder = load_vgg_decoder.load(vgg_path="../pre-trained/vgg_normalised.pth",
                                                       decoder_path="../pre-trained/decoder.pth",
                                                       device=device)

        self.size = size
        self.weights = weights

    def decode3shape(self, coloring_result):
        coloring_result = coloring_result[0]

        result = np.zeros((*self.size, 3))

        for i in range(self.size[0]):
            for j in range(self.size[0]):
                result[i, j] = coloring_result[:, i, j]

        return result

    def transform(self):
        return transforms.Compose([transforms.ToTensor()])

    def style_(self, feature, eps=1e-5):
        N, C = feature.size()[:2]

        feature = feature.reshape(N, C, -1)

        mean = feature.mean(dim=2).reshape(N, C, 1, 1)
        std = (feature.var(dim=2) + eps).sqrt().reshape(N, C, 1, 1)

        return mean, std

    def adain_normalization(self, content_f, style_f):
        size = content_f.size()

        style_mean, style_std = self.style_(style_f)
        content_mean, content_std = self.style_(content_f)

        style_mean, style_std = style_mean.expand(size), style_std.expand(size)
        content_mean, content_std = content_mean.expand(size), content_std.expand(size)

        normalized_f = (content_f - content_mean) / content_std
        normalized_f = style_std * normalized_f + style_mean

        return normalized_f

    def interpolation(self, content, styles):
        content_f = self.vgg(content)
        style_fs = [self.vgg(style) for style in styles]

        feature = sum(
            [self.weights[i] * self.adain_normalization(content_f, style_fs[i]) for i in range(len(style_fs))])

        return self.decoder(feature)

    def result_(self):
        content = self.transform()(self.content_img).to(self.device).unsqueeze(0)
        styles = []
        for i in range(len(self.style_imgs)):
            styles.append(self.transform()(self.style_imgs[i]).to(self.device).unsqueeze(0))

        coloring_result = self.interpolation(content, styles)

        torch.cuda.empty_cache()
        gc.collect()

        coloring_result = coloring_result.cpu().detach().numpy()

        coloring_result = self.decode3shape(coloring_result)

        return coloring_result


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import get_abspath

    project_path = get_abspath.project_abspath()

    auto_coloring = AutoColoring(content_path=f"{project_path}/test_image/content.jpg",
                                 style_paths=[f"{project_path}/test_image/style_house.jpg"],
                                 size=(128, 128), weights=[1.0])

    coloring_result = auto_coloring.result_()

    plt.imshow(coloring_result)
    plt.show()
