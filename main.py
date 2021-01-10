# -*- coding: utf-8 -*- 
# !/usr/bin/env python3
import sys
import time

import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QMutexLocker, QMutex, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox

from interface.UI import UI
from settings import APP_NAME


class VideoTimer(QThread):
    signal_update_frame = pyqtSignal()
    signal_finished = pyqtSignal()

    def __init__(self):
        super(VideoTimer, self).__init__()
        self.playing = False
        self.fps = 0
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.playing = True
        while self.playing:
            self.signal_update_frame.emit()
            time.sleep(1 / self.fps)
        self.signal_finished.emit()

    def pause(self):
        with QMutexLocker(self.mutex):
            self.playing = False


class MainWindow(UI):
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    def __init__(self):
        super(MainWindow, self).__init__()

        self.timer = VideoTimer()

        self.action_reset()

        self.player.double_clicked.connect(self.action_double_clicked)

        self.button_play.clicked.connect(self.action_play)
        self.button_reset.clicked.connect(self.action_reset)
        self.button_open.clicked.connect(self.action_open)

        self.timer.signal_update_frame.connect(self.video_play)
        self.timer.signal_finished.connect(self.video_pause)

        self.widget_slider.signal_valueChanged.connect(self.video_jump)

    def action_reset(self):
        self.setWindowTitle(APP_NAME)

        self.player.setPixmap(QPixmap(':welcome.png'))

        self.video_url = ''
        self.video_fps = 0
        self.video_total_frames = 0
        self.video_height = 0
        self.video_width = 0
        self.num = 0

        self.current_frame = None

        self.widget_slider.setValue(0)
        self.widget_spin.setHidden(True)

        # timer 设置
        self.timer.pause()

        # video 初始设置
        self.video_capture = cv2.VideoCapture()

    def video_jump(self, num):
        self.num = num
        self.widget_slider.setValue(num)
        self.widget_spin.setValue(num)
        self.get_frame(num)

    def video_pause(self):
        if self.num >= self.video_total_frames:
            self.action_reset()

    def video_play(self):
        if self.num is None:
            self.num = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES) + 1
        else:
            self.num += 1
        self.widget_slider.setValue(self.num)
        self.widget_spin.setValue(self.num)
        self.get_frame()

    def action_double_clicked(self):
        [self.action_open, self.action_play][self.video_capture.isOpened()]()

    def action_open(self):
        video_url, _ = QFileDialog.getOpenFileName(self, 'Video Player', '', '*.mp4;*.mkv;*.rmvb')
        if video_url:
            self.action_reset()

            self.video_url = video_url
            self.video_capture.open(filename=self.video_url)
            self.setWindowTitle(f'{APP_NAME} - {self.video_url}')
            self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
            self.video_total_frames = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
            self.video_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.video_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.num = 0
            self.timer.fps = self.video_fps
            self.widget_slider.setMaximum(self.video_total_frames)
            self.widget_spin.setSuffix(f'/{int(self.video_total_frames)}')
            self.widget_spin.setMaximum(self.video_total_frames)
            self.widget_spin.setHidden(False)

            self.action_play()

    def action_play(self):
        if self.video_capture.isOpened():
            self.button_play.setIcon(QIcon([':pause.svg', ':play.svg'][self.timer.playing]))
            [self.timer.start, self.timer.pause][self.timer.playing]()
        elif self.video_url:
            self.video_play()

    def get_appropriate_size(self):
        if (self.player.width() / self.player.height()) > (self.video_width / self.video_height):
            return self.player.height() * (self.video_width / self.video_height), self.player.height()
        else:
            return self.player.width(), self.player.width() / (self.video_width / self.video_height)

    def get_frame(self, num=None):
        if self.video_capture.isOpened():
            if num is not None:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, num)
            success, frame = self.video_capture.read()
            if success:
                self.current_frame = QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).flatten(),
                                            self.video_width, self.video_height, QImage.Format_RGB888)
                self.player.setPixmap(QPixmap.fromImage(self.current_frame).scaled(*self.get_appropriate_size()))
            else:
                if self.num >= self.video_total_frames:
                    self.timer.pause()
                    self.button_play.setIcon(QIcon(':play.svg'))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            self.action_play()
        event.accept()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if not self.timer.playing and self.current_frame:
            self.player.setPixmap(QPixmap.fromImage(self.current_frame).scaled(*self.get_appropriate_size()))

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.timer.playing:
            self.timer.pause()
            close = QMessageBox.warning(self, APP_NAME,
                                        'Video playing, close app?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if close == QMessageBox.No:
                event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    style_sheet = open(r'./sources/style.qss', mode='r', encoding='utf-8').read()
    win.setStyleSheet(style_sheet)
    win.show()
    sys.exit(app.exec_())
