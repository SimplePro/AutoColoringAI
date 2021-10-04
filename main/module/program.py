import sys
import os

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QPushButton, QLabel, QFileDialog, QMainWindow
from PyQt5.QtGui import QIcon, QCursor
from PyQt5 import QtCore

import get_abspath
import art_classification
from bisect import bisect_left

import time

import gc

project_path = get_abspath.project_abspath()
main_path = get_abspath.main_abspath()

sketch_path = ''
sketch_topic = ''
recommend_art20 = []


class RecommendArtThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        global sketch_topic, recommend_art20

        self.parent.btn_enabled(False)

        # 종류 예측
        sketch_topic = art_classification.result_(sketch_path)

        # 같은 종류의 미술 작품들 리스트
        art_dir = os.listdir(f"{project_path}/dataset/{sketch_topic}/")

        print(sketch_topic)

        # 유사도가 높은 상위 20개의 미술작품
        recommend_art20 = []

        # 먼저 20개 미술작품 추가.
        for i in range(20):
            recommend_art20.append((art_dir[i], art_classification.mse_loss(sketch_path,
                                                                            f"{project_path}/dataset/{sketch_topic}/{art_dir[i]}")))

        recommend_art20.sort(key=lambda x: x[1])

        print(recommend_art20)

        # 그 나머지들은 for 문을 돌며 수정
        for i in range(20, len(art_dir)):
            loss_list = [i[1] for i in recommend_art20]

            loss = art_classification.mse_loss(sketch_path, f"{project_path}/dataset/{sketch_topic}/{art_dir[i]}")

            if loss < loss_list[-1]:
                idx = bisect_left(loss_list, loss)
                recommend_art20.insert(idx, (art_dir[i], loss))
                recommend_art20.pop()

        print(recommend_art20)

        gc.collect()

        self.parent.btn_enabled(True)


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AutoColoringAI")
        self.setWindowIcon(QIcon(f"{main_path}/ui_imgs/auto_coloring_ai_ico.png"))
        self.setStyleSheet("background-color: #DDECCA;")
        self.setFixedSize(1000, 600)
        self.center()

        # 스케치 박스
        self.sketch_box = QLabel("", self)
        self.sketch_box.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                      "/sketch_box_img.png);")
        self.sketch_box.move(10, 10)
        self.sketch_box.resize(330, 410)

        # 스케치 이미지
        self.sketch_img = QLabel("", self)
        self.sketch_img.setStyleSheet(f"border-radius: 10px; background-color: white")
        self.sketch_img.move(65, 100)
        self.sketch_img.resize(220, 220)

        # 스케치 찾아보기 버튼
        self.explorer_btn = QPushButton("", self)
        self.explorer_btn.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                        "/explorer_btn_img);" "border-radius: 30px;" "background-color: #F8F8F8;")
        self.explorer_btn.move(100, 350)
        self.explorer_btn.resize(140, 40)
        self.explorer_btn.clicked.connect(self.clicked_explorer)
        self.explorer_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 미술 작품 추천 박스
        self.art_box = QLabel("", self)
        self.art_box.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                   "/art_box_img.png);")
        self.art_box.move(350, 10)
        self.art_box.resize(620, 410)

        # 미술 작품 추가하기 버튼
        self.add_art_btn = QPushButton("", self)
        self.add_art_btn.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                       "/add_art_btn_img.png);" "border-radius: 0px;" "background-color: #F8F8F8;")
        self.add_art_btn.move(505, 350)
        self.add_art_btn.resize(310, 50)
        self.add_art_btn.clicked.connect(self.clicked_add_art)
        self.add_art_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 채색 버튼
        self.painting_btn = QPushButton("", self)
        self.painting_btn.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                        "/painting_btn_img.png);" "border-radius: 0px;")
        self.painting_btn.move(50, 430)
        self.painting_btn.resize(140, 140)
        self.painting_btn.clicked.connect(self.clicked_painting)
        self.painting_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 채색 결과 확인 버튼
        self.check_result_btn = QPushButton("", self)
        self.check_result_btn.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                            "/check_result_btn_img.png);" "border-radius: 0px;")
        self.check_result_btn.move(295, 460)
        self.check_result_btn.resize(410, 90)
        self.check_result_btn.clicked.connect(self.clicked_check_result)
        self.check_result_btn.setCursor(QCursor(QtCore.Qt.PointingHandCursor))

        # 저장 버튼
        self.save_btn = QPushButton("", self)
        self.save_btn.setStyleSheet(f"image : url({main_path}/ui_imgs"
                                    "/save_btn_img.png);" "border-radius: 0px;")
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
        global sketch_path, sketch_topic

        sketch_path = QFileDialog.getOpenFileName(self, "스케치 선택", )[0]

        if sketch_path != '':
            self.sketch_img.setStyleSheet(f"image : url({sketch_path});"
                                          "border-radius: 10px; background-color: white;")

            recommend_art = RecommendArtThread(self)
            recommend_art.start()

    # 미술 작품 추가 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_add_art(self):
        print("clicked add art btn")

    # 채색 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_painting(self):
        print("clicked painting btn")

    # 채색 결과 확인 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_check_result(self):
        print("clicked check result btn")

    # 저장 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_save(self):
        print("clicked save btn")

    # 모든 버튼 컨트롤
    def btn_enabled(self, boolean):
        self.explorer_btn.setEnabled(boolean)
        self.add_art_btn.setEnabled(boolean)
        self.painting_btn.setEnabled(boolean)
        self.check_result_btn.setEnabled(boolean)
        self.save_btn.setEnabled(boolean)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
