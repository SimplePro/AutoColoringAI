import torch
from auto_coloring import AutoColoring
import art_classification
import numpy as np

from PIL import Image

import os

import matplotlib.pyplot as plt


auto_coloring = AutoColoring(content_path=f"{os.getcwd()}\\test_image\\content.jpg", 
                            style_paths=[f"{os.getcwd()}\\test_image\\style_house.jpg"], weights=[1.0])

coloring_result = auto_coloring.result_()

plt.imshow((coloring_result * 255.).astype(np.uint8))
plt.show()


test_image = Image.open(f"{os.getcwd()}\\dataset\\abstract\\ (1).jpg").convert("L").resize((128, 128))

plt.imshow(test_image, cmap="gray")
plt.show()

device = torch.device("cuda")

test_image = art_classification.preprocessing(test_image)
test_label = art_classification.predict(torch.tensor(test_image).to(device))

print(test_label)
