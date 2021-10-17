# -*- coding: utf-8 -*-

import sys
import os

import matplotlib.pyplot as plt
import numpy as np

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QFileDialog, QMainWindow, QListWidget, QDesktopWidget, \
    QListWidgetItem, QDoubleSpinBox
from PyQt5.QtGui import QIcon, QCursor
from PyQt5 import QtCore

import get_abspath
import art_classification
from auto_coloring import AutoColoring
from bisect import bisect_left

import gc

project_path = get_abspath.project_abspath()
main_path = get_abspath.main_abspath()

sketch_path = ''  # 스케치의 경로
sketch_topic = ''  # 스케치 종류
recommend_art20 = []  # 추천 미술 작품 Top 20 파일 이름 (filename, loss)
user_img_path = []  # 사용자가 추가한 미술 작품 경로

coloring_art = []  # 적용할 미술 작품
coloring_weights = []  # 적용할 미술 작품들의 적용도

result = np.zeros((128, 128, 3))  # 채색 결과

selected_art_path = ''  # 사용자가 현재 선택한 미술작품 경로


class RecommendArtThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        global sketch_topic, recommend_art20

        # 종류 예측
        sketch_topic = art_classification.result_(sketch_path)

        # 같은 종류의 미술 작품들 리스트
        art_dir = os.listdir(f"{project_path}/dataset/art_recommend/{sketch_topic}/")

        # 유사도가 높은 상위 20개의 미술작품
        recommend_art20 = []

        # 먼저 20개 미술작품 추가.
        for i in range(20):
            filepath = f"{project_path}/dataset/art_recommend/{sketch_topic}/{art_dir[i]}"
            recommend_art20.append((filepath, art_classification.mse_loss(sketch_path, filepath)))

        # 유사도 오름차순 정렬
        recommend_art20.sort(key=lambda x: x[1])

        # 그 나머지들은 for 문을 돌며 수정
        for i in range(20, len(art_dir)):
            loss_list = [i[1] for i in recommend_art20]

            filepath = f"{project_path}/dataset/art_recommend/{sketch_topic}/{art_dir[i]}"

            loss = art_classification.mse_loss(sketch_path, filepath)

            if loss < loss_list[-1]:
                idx = bisect_left(loss_list, loss)
                recommend_art20.insert(idx, (art_dir[i], loss))
                recommend_art20.pop()

            self.parent.progress_label.setText(f"진행률: {round(i / 6, 2)}%")

        self.parent.progress_label.setText(f"진행률: 100%")

        gc.collect()

        self.parent.btn_enabled(True)

        for i in recommend_art20:
            filepath = f"{project_path}/dataset/art_recommend/{sketch_topic}/{i[0]}"
            icon = QIcon(filepath)
            self.parent.recommend_art_path_list.addItem(QListWidgetItem(icon, filepath))


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AutoColoringAI")
        self.setWindowIcon(QIcon(f"{main_path}/ui_imgs/auto_coloring_ai_ico.png"))
        self.setFixedSize(1000, 600)
        self.center()

        # 스케치 박스
        self.sketch_box = QLabel("", self)
        self.sketch_box.setStyleSheet(f"image : url({main_path}/ui_imgs/sketch_box_img.png);")
        self.sketch_box.move(10, 10)
        self.sketch_box.resize(330, 410)

        # 스케치 이미지
        self.sketch_img = QLabel("", self)
        self.sketch_img.setStyleSheet(f"border-radius: 5px; background-color: white")
        self.sketch_img.move(65, 100)
        self.sketch_img.resize(220, 220)

        # 스케치 찾아보기 버튼
        self.explorer_btn = QPushButton("", self)
        self.explorer_btn.setStyleSheet(f"image : url({main_path}/ui_imgs/explorer_btn_img);"
                                        "border-radius: 0px;" "background-color: #F8F8F8;")
        self.explorer_btn.move(100, 350)
        self.explorer_btn.resize(140, 40)
        self.explorer_btn.clicked.connect(self.clicked_explorer)
        self.explorer_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 미술 작품 추천 박스
        self.art_box = QLabel("", self)
        self.art_box.setStyleSheet(f"image : url({main_path}/ui_imgs/art_box_img.png);")
        self.art_box.move(350, 10)
        self.art_box.resize(620, 410)

        # 미술 작품 추천 진행률
        self.progress_label = QLabel("진행률: 0%", self)
        self.progress_label.move(385, 70)

        # 미술 작품 추천 파일명 리스트위젯
        self.recommend_art_path_list = QListWidget(self)
        self.recommend_art_path_list.resize(150, 220)
        self.recommend_art_path_list.move(385, 100)
        self.recommend_art_path_list.itemClicked.connect(self.clicked_recommend_art_path_item)

        # 미술 작품 사진 라벨
        self.art_img = QLabel("", self)
        self.art_img.resize(220, 220)
        self.art_img.move(550, 100)
        self.art_img.setStyleSheet(f"background-color: white;" "border-radius: 5px;")

        # 미술 작품 적용 파일명 리스트위젯
        self.coloring_art_path_list = QListWidget(self)
        self.coloring_art_path_list.resize(150, 220)
        self.coloring_art_path_list.move(790, 100)
        self.coloring_art_path_list.itemDoubleClicked.connect(self.double_clicked_coloring_art_path_item)

        # 미술 작품 남은 적용도
        self.remain_weight_label = QLabel("남은 적용도: 100%", self)
        self.remain_weight_label.move(790, 70)

        # 적용도 스핀박스
        self.coloring_weight_spinbox = QDoubleSpinBox(self)
        self.coloring_weight_spinbox.setRange(0, 100)
        self.coloring_weight_spinbox.setSingleStep(0.5)
        self.coloring_weight_spinbox.setPrefix("적용도 (%): ")
        self.coloring_weight_spinbox.move(720, 340)
        self.coloring_weight_spinbox.resize(130, 40)

        # 적용 버튼
        self.art_apply_btn = QPushButton("적용", self)
        self.art_apply_btn.resize(75, 50)
        self.art_apply_btn.move(860, 335)
        self.art_apply_btn.clicked.connect(self.clicked_art_apply)

        # 미술 작품 추가하기 버튼
        self.add_art_btn = QPushButton("", self)
        self.add_art_btn.setStyleSheet(f"image : url({main_path}/ui_imgs/add_art_btn_img.png);"
                                       "border-radius: 0px;" "background-color: #F8F8F8;")
        self.add_art_btn.move(400, 340)
        self.add_art_btn.resize(310, 50)
        self.add_art_btn.clicked.connect(self.clicked_add_art)
        self.add_art_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 채색 버튼
        self.coloring_btn = QPushButton("", self)
        self.coloring_btn.setStyleSheet(f"image : url({main_path}/ui_imgs/coloring_btn_img.png);"
                                        "border-radius: 0px;")
        self.coloring_btn.move(50, 430)
        self.coloring_btn.resize(140, 140)
        self.coloring_btn.clicked.connect(self.clicked_coloring)
        self.coloring_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 채색 결과 확인 버튼
        self.check_result_btn = QPushButton("", self)
        self.check_result_btn.setStyleSheet(f"image : url({main_path}/ui_imgs/check_result_btn_img.png);"
                                            "border-radius: 0px;")
        self.check_result_btn.move(295, 460)
        self.check_result_btn.resize(410, 90)
        self.check_result_btn.clicked.connect(self.clicked_check_result)
        self.check_result_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 저장 버튼
        self.save_btn = QPushButton("", self)
        self.save_btn.setStyleSheet(f"image : url({main_path}/ui_imgs/save_btn_img.png);"
                                    "border-radius: 0px;")
        self.save_btn.move(800, 430)
        self.save_btn.resize(120, 120)
        self.save_btn.clicked.connect(self.clicked_save)
        self.save_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 스케치 찾아보기 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_explorer(self):
        global sketch_path, sketch_topic, user_img_path, coloring_art, coloring_weights

        path = QFileDialog.getOpenFileName(self, "스케치 선택", "", "image file(*.png *jpg *jpeg)")[0]

        if path != '':

            sketch_path = path
            self.sketch_img.setStyleSheet(f"image : url({sketch_path});"
                                          "border-radius: 5px; background-color: white;")

            self.btn_enabled(False)
            self.recommend_art_path_list.clear()
            self.art_img.setStyleSheet(f"background-color: white;" "border-radius: 5px;")
            self.coloring_art_path_list.clear()
            coloring_art = []
            coloring_weights = []
            self.remain_weight_label.setText(f"남은 적용도: 100%")

            user_img_path = []

            recommend_art = RecommendArtThread(self)
            recommend_art.start()

    # 미술 작품 추가 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_add_art(self):
        if sketch_path != '':
            user_img = QFileDialog.getOpenFileName(self, "미술 작품 추가", "", "image file(*.png *jpg *jpeg)")[0]

            if user_img != '':
                icon = QIcon(user_img)
                self.recommend_art_path_list.addItem(QListWidgetItem(icon, user_img))

            user_img_path.append(user_img)

    # 추천 미술 작품 아이템이 클릭되었을 때 실행되는 메소드.
    def clicked_recommend_art_path_item(self, item):
        global selected_art_path

        selected_art_path = item.text()

        self.art_img.setStyleSheet(f"image : url({selected_art_path});")

    # 적용 버튼이 눌렸을 때 실행되는 메소드.
    def clicked_art_apply(self):
        if selected_art_path != '' and self.coloring_weight_spinbox.value() != 0:
            coloring_art.append(selected_art_path)
            coloring_weights.append(self.coloring_weight_spinbox.value() / 100)
            self.coloring_weight_spinbox.setValue(0)

            icon = QIcon(selected_art_path)
            self.coloring_art_path_list.addItem(QListWidgetItem(icon, selected_art_path))

            self.remain_weight_label.setText(f"남은 적용도: {round((1 - sum(coloring_weights)) * 100, 2)}%")

    # 적용하려는 미술 작품의 아이템이 더블클릭되었을 때 실행되는 메소드.
    def double_clicked_coloring_art_path_item(self, item):
        idx = coloring_art.index(item.text())
        del coloring_art[idx]
        del coloring_weights[idx]

        self.coloring_art_path_list.takeItem(idx)

        self.remain_weight_label.setText(f"남은 적용도: {round((1 - sum(coloring_weights)) * 100, 2)}%")

    # 채색 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_coloring(self):
        global result

        self.btn_enabled(False)

        if 0 < sum(coloring_weights) < 1:
            try:
                result = AutoColoring(content_path=sketch_path, style_paths=coloring_art, weights=coloring_weights).result_()
                result = (result - result.min()) / (result.max() - result.min())  # 정규화

            except Exception as err:
                print(err)
            
        self.btn_enabled(True)

    # 채색 결과 확인 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_check_result(self):
        plt.imshow(result)
        plt.show()

    # 저장 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_save(self):
        save_filepath = QFileDialog.getSaveFileName(self, "Save File", "./result.png", "image file(*.png *jpg *jpeg)")[0]

        if save_filepath != '':
            plt.imsave(save_filepath, result)

    # 모든 버튼 컨트롤
    def btn_enabled(self, boolean):
        self.explorer_btn.setEnabled(boolean)
        self.add_art_btn.setEnabled(boolean)
        self.coloring_btn.setEnabled(boolean)
        self.check_result_btn.setEnabled(boolean)
        self.save_btn.setEnabled(boolean)
        self.art_apply_btn.setEnabled(boolean)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
