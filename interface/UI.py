# -*- coding: utf-8 -*- 
# !/usr/bin/env python3
import sys

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from sources import sources


class Player(QLabel):
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super(Player, self).__init__(parent)

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
    signal_valueChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Slider, self).__init__()

    def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
        pass

    def dragMoveEvent(self, a0: QtGui.QDragMoveEvent) -> None:
        pass

    def dragLeaveEvent(self, a0: QtGui.QDragLeaveEvent) -> None:
        print(self.value())

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        current_x = event.pos().x()
        per = current_x * 1.0 / self.width()
        value = per * (self.maximum() - self.minimum()) + self.minimum()
        self.signal_valueChanged.emit(value)


class UI(QWidget):
    def __init__(self, parent=None):
        super(UI, self).__init__(parent, flags=QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowIcon(QIcon(':logo.png'))

        self.setFocusPolicy(QtCore.Qt.NoFocus)

        self.player = Player(self)

        self.button_play = QPushButton('', self)
        self.button_play.setIcon(QIcon(':play.svg'))

        self.button_reset = QPushButton('', self)
        self.button_reset.setIcon(QIcon(':reset.svg'))

        self.button_open = QPushButton('', self)
        self.button_open.setIcon(QIcon(':open.svg'))
        self.button_open.setObjectName('open')

        self.widget_spin = QSpinBox(self)
        self.widget_spin.setAlignment(QtCore.Qt.AlignRight)

        self.widget_slider = Slider(self)
        self.widget_slider.setOrientation(QtCore.Qt.Horizontal)

        controller_layout = QHBoxLayout()
        controller_layout.addWidget(self.button_play)
        controller_layout.addWidget(self.button_reset)
        controller_layout.addWidget(self.widget_slider, stretch=1)
        controller_layout.addWidget(self.widget_spin)
        controller_layout.addWidget(self.button_open)

        controller_layout.setContentsMargins(0, 0, 0, 0)
        controller_layout.setSpacing(0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.player)
        main_layout.addLayout(controller_layout)
        self.setLayout(main_layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = UI()
    style_sheet = open(r'../sources/style.qss', mode='r', encoding='utf-8').read()
    win.setStyleSheet(style_sheet)
    win.show()
    sys.exit(app.exec_())
