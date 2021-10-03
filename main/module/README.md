# Guide

AutoColoring
----------------------
```python
1. AutoColoring(content_path: str, style_paths: list, size: tuple, weights: list)
# content_path: 채색할 스케치 이미지의 경로.
# style_paths: 채색되는 미술작품들의 경로.
# size: 이미지의 크기.
# weights: 각 미술작품들의 스타일 적용도.  

2. AutoColoring().result_()
# 결과는 np.array 형태로 반환된다.
# shape은 (*size, 3) 이다.  
```
  
art_classification
----------------
```python
1. preprocessing(x: PIL.Image)
# input x의 shape은 (128, 128)이여야 한다.
# output의 shape은 (1, 3, 128, 128)이고, type은 torch.tensor이다.

2. predict(x: torch.tensor)
# input x는 preprocessing된 결과에 .to(device)를 해주어야 한다.
# output은 ["abstract", "cityscape", "landscape", "portrait", "still-life"] 중에 하나이다.
```
