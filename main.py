# -*- coding: utf-8 -*- 
# !/usr/bin/env python3

# Name: main.py
# Author: https://github.com/536
# Create Time: 2020-06-01 20:54
import sys
import time

import cv2
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QMutexLocker, QMutex, QThread, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QStyle, QFileDialog, QMessageBox

from interface.UI import UI
from settings import APP_NAME


class CommonHelper(object):
    @staticmethod
    def read(qss):
        try:
            with open(qss, mode='r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(e)
            return ''


class VideoTimer(QThread):
    update_frame_signal = pyqtSignal()

    def __init__(self):
        super(VideoTimer, self).__init__()
        self.playing = False
        self.fps = 0
        self.mutex = QMutex()

    def run(self):
        with QMutexLocker(self.mutex):
            self.playing = True
        while self.playing:
            self.update_frame_signal.emit()
            time.sleep(1 / self.fps)

    def pause(self):
        with QMutexLocker(self.mutex):
            self.playing = False


class MainWindow(UI):
    VIDEO_TYPE_OFFLINE = 0
    VIDEO_TYPE_REAL_TIME = 1

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle(APP_NAME)

        self.video_url = ''
        self.video_fps = 0
        self.video_total_frames = 0
        self.video_height = 0
        self.video_width = 0

        self.current_frame = None

        # timer 设置
        self.timer = VideoTimer()
        self.timer.update_frame_signal.connect(self.get_frame)
        # video 初始设置
        self.video_capture = cv2.VideoCapture()

        self.progress.valueChanged.connect(self.get_frame_)

    def action_double_clicked(self):
        if self.video_capture.isOpened():
            self.action_play()
        else:
            self.action_open()

    def action_dragged(self, video_url):
        self.video_url = video_url
        self.video_capture.open(filename=video_url)
        self.setWindowTitle(f'{video_url} - {APP_NAME}')
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.video_total_frames = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.video_width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.timer.fps = self.video_fps
        self.progress.setMaximum(self.video_total_frames)

        self.get_frame()
        self.cap_prop_pos_msec = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
        self.cap_prop_pos_frames = self.video_capture.get(cv2.CAP_PROP_POS_FRAMES)

    def action_open(self):
        video_url, _ = QFileDialog.getOpenFileName(self, 'Video Player', '', '*.mp4;;*.mkv;;*.rmvb')
        if video_url:
            self.action_dragged(video_url)

    def action_reset(self):
        pass

    def action_play(self):
        if self.video_capture.isOpened():
            self.play.setIcon(QIcon([':pause.svg', ':play.svg'][self.timer.playing]))
            [self.timer.start, self.timer.pause][self.timer.playing]()
        elif self.video_url:
            self.action_dragged(self.video_url)
            self.action_play()

    def get_appropriate_size(self):
        if (self.main.width() / self.main.height()) > (self.video_width / self.video_height):
            return self.main.height() * (self.video_width / self.video_height), self.main.height()
        else:
            return self.main.width(), self.main.width() / (self.video_width / self.video_height)

    def get_frame_(self, num=None):
        if not self.timer.playing:
            self.get_frame(num)

    def get_frame(self, num=None):
        if self.video_capture.isOpened():
            print(num, '/', self.video_capture.get(cv2.CAP_PROP_POS_FRAMES), '/', self.video_total_frames)
            if num is not None:
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, num)
                self.progress.setValue(num)
            else:
                self.progress.setValue(self.video_capture.get(cv2.CAP_PROP_POS_FRAMES) + 1)

            success, frame = self.video_capture.read()
            if success:
                self.current_frame = QImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).flatten(),
                                            self.video_width, self.video_height, QImage.Format_RGB888)
                self.main.setPixmap(QPixmap.fromImage(self.current_frame).scaled(*self.get_appropriate_size()))
            else:
                self.video_capture.release()
                self.timer.pause()
                self.play.setIcon(QIcon(':play.svg'))

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        if event.key() == QtCore.Qt.Key_Space:
            self.action_play()
        event.accept()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        if not self.timer.playing and self.current_frame:
            self.main.setPixmap(QPixmap.fromImage(self.current_frame).scaled(*self.get_appropriate_size()))
        event.accept()

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.timer.playing:
            self.timer.pause()
            close = QMessageBox.warning(self, APP_NAME,
                                        'Video playing, close app?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if close == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    style_sheet = CommonHelper.read('./sources/style.qss')
    win.setStyleSheet(style_sheet)
    win.show()
    sys.exit(app.exec_())
