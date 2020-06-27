# -*- coding: utf-8 -*- 
# !/usr/bin/env python3

# Name: UI.py
# Author: https://github.com/536
# Create Time: 2020-06-01 20:49
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from sources import sources


class CommonHelper(object):
    @staticmethod
    def read(qss):
        try:
            with open(qss, mode='r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(e)
            return ''


class Welcome(QLabel):
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Welcome, self).__init__(parent)

        self.mouse_pressed = False
        self.mouse_position = None

        self.setPixmap(QPixmap(':welcome.png'))
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumSize(640, 360)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_pressed = True
            self.mouse_position = event.globalPos() - self.parent().pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if QtCore.Qt.LeftButton and self.mouse_pressed:
            self.parent().move(event.globalPos() - self.mouse_position)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.mouse_pressed = False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        self.double_clicked.emit()


class Slider(QSlider):
    signal_value_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Slider, self).__init__()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        pass

    def dragMoveEvent(self, a0: QtGui.QDragMoveEvent) -> None:
        pass

    def dragLeaveEvent(self, a0: QtGui.QDragLeaveEvent) -> None:
        print(self.value())

    # def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
    #     pass


class UI(QWidget):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent, flags=QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle('Video Player')
        self.setWindowIcon(QIcon(':logo.png'))

        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.main = Welcome(self)
        self.main.double_clicked.connect(self.action_double_clicked)

        self.play = QPushButton('', self)
        self.play.setIcon(QIcon(':play.svg'))
        self.play.clicked.connect(self.action_play)

        self.reset = QPushButton('', self)
        self.reset.setIcon(QIcon(':reset.svg'))
        self.reset.clicked.connect(self.action_reset)

        self.open = QPushButton('', self)
        self.open.setIcon(QIcon(':open.svg'))
        self.open.setObjectName('open')
        self.open.clicked.connect(self.action_open)

        self.progress = Slider(self)
        self.progress.setOrientation(QtCore.Qt.Horizontal)

        controller_layout = QHBoxLayout()
        controller_layout.addWidget(self.play)
        controller_layout.addWidget(self.reset)
        controller_layout.addWidget(self.progress, stretch=1)
        controller_layout.addWidget(self.open)

        controller_layout.setContentsMargins(0, 0, 0, 0)
        controller_layout.setSpacing(0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.main)
        main_layout.addLayout(controller_layout)
        self.setLayout(main_layout)

    def action_double_clicked(self):
        pass

    def action_play(self):
        pass

    def action_reset(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UI()
    style_sheet = CommonHelper.read('../sources/style.qss')
    win.setStyleSheet(style_sheet)
    win.show()
    sys.exit(app.exec_())
