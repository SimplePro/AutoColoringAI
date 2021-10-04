import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QPushButton, QLabel
from PyQt5.QtGui import QIcon, QCursor
from PyQt5 import QtCore

from module import get_abspath

main_path = get_abspath.main_abspath()


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Application")
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

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # 스케치 찾아보기 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_explorer(self):
        print("clicked explorer btn")

    # 채색 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_painting(self):
        print("clicked painting btn")

    # 미술 작품 추가 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_add_art(self):
        print("clicked add art btn")

    # 채색 결과 확인 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_check_result(self):
        print("clicked check result btn")

    # 저장 버튼이 클릭됐을 때 실행되는 메소드.
    def clicked_save(self):
        print("clicked save btn")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
