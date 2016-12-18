#!/usr/bin/python3

import sys, random
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame,)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt


class PLGMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setCentralWidget(PLGMainWidget())
        self.resize(1000, 600)
        self.center()
        self.setWindowTitle('多边形')
        self.statusBar()
        self.show()

    def center(self):
        """窗口居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class PLGMainWidget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        okButton = QPushButton("OK")
        cancelButton = QPushButton("Cancel")

        paintArea = PLGPaintArea()

        hbox = QHBoxLayout()
        hbox.addWidget(okButton)
        hbox.addWidget(cancelButton)
        hbox.addStretch(1)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(paintArea)
        self.setLayout(vbox)


class PLGPaintArea(QLabel):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFrameShadow(QFrame.Sunken)
        self.setFrameShape(QFrame.Panel)
        pass
        # self.resize(1000, 600)

    # def paintEvent(self, e):
    #     qp = QPainter()
    #     qp.begin(self)
    #     self.drawPolygon(qp)
    #     qp.end()

    # def drawPolygon(self, qp):
    #     qp.setPen(Qt.red)
    #     qp.setBrush(Qt.red)
    #     print(self.size())
    #     qp.drawPoint(0, 0)
    #     # qp.drawPoint(30, 40)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PLGMainWindow()
    sys.exit(app.exec_())
