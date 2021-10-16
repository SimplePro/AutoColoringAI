# Guide

AutoColoring
----------------------
```python
1. AutoColoring(content_path: str, style_paths: list, weights: list)
# content_path: 채색할 스케치 이미지의 경로.
# style_paths: 채색되는 미술작품들의 경로.
# weights: 각 미술작품들의 스타일 적용도.  

2. AutoColoring().result_()
# 결과는 np.array 형태로 반환된다.
# 이미지의 비율은 보존하되, 맥스픽셀을 256으로 조정한다.
# content shape = (a, b, 3)
# output shape = (256, 256b/a, 3) (a > b)  or  (256a/b, 256, 3) (b > a)
```
  
art_classification
----------------
```python
1. preprocessing(x: PIL.Image)
# input x의 shape은 (128, 128)이여야 한다.
# output의 shape은 (1, 3, 128, 128)이고, type은 torch.tensor이다.

2. predict(x: torch.tensor)
# input x는 preprocessing된 결과에 .to(device)를 해주어야 한다.
# output은 ["cityscape", "landscape", "portrait"] 중에 하나이다.
```
