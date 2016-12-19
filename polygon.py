#!/usr/bin/python3

import sys, random
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame, QColorDialog,)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

from figures import Polygon, PlainPolygon, Line, Point
from scanline import fill_polygon


class PLGMainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initUI()

    def initUI(self):
        self.main_widget = PLGMainWidget()
        self.setCentralWidget(self.main_widget)
        self.resize_and_center()
        self.setWindowTitle('Polygon')
        self.statusBar().showMessage('Ready.')
        self.show()

    def resize_and_center(self):
        """调整窗口大小并居中"""
        self.resize(int(QDesktopWidget().width() * 0.618),
                    int(QDesktopWidget().height() * 0.618))
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class PLGState(object):
    NORMAL = 0  # 正常
    INPUT_MAIN_OUTER = 10  # 输入多边形（主多边形）
    INPUT_MAIN_INNER = 11  # 输入内环（主多边形）
    INPUT_CUTTER_OUTER = 20  # 输入多边形（裁剪多边形）
    INPUT_CUTTER_INNER = 21  # 输入内环（裁剪多边形）


class PLGMainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_polygon = None
        self.cutter_polygon = None
        self.state = PLGState.NORMAL
        self.initUI()

    def initUI(self):
        self.paint_area = PLGPaintArea(main_widget=self)
        container_frame = QFrame()
        container_frame.setFrameShape(QFrame.StyledPanel)
        container_box = QHBoxLayout()
        container_box.addWidget(self.paint_area)
        container_box.setContentsMargins(0, 0, 0, 0)
        container_frame.setLayout(container_box)

        label1_1 = QLabel('主多边形：')
        label1_1.setMinimumWidth(100)
        self.btn_main_outer = QPushButton('输入多边形')
        self.btn_main_outer.setCheckable(True)
        self.btn_main_outer.clicked[bool].connect(self.input_main_outer)
        self.btn_main_inner = QPushButton('输入内环')
        self.btn_main_inner.setCheckable(True)
        self.btn_main_inner.clicked[bool].connect(self.input_main_inner)
        self.btn_main_color = QPushButton('选择颜色')
        self.btn_main_color.clicked.connect(self.select_color)

        label1_2 = QLabel('裁剪多边形：')
        label1_2.setMinimumWidth(100)
        self.btn_cutter_outer = QPushButton('输入多边形')
        self.btn_cutter_inner = QPushButton('输入内环')

        label2 = QLabel('其它操作：')
        label2.setMinimumWidth(100)
        self.btn_move = QPushButton('平移')
        self.btn_rotate = QPushButton('旋转')
        self.btn_zoom = QPushButton('缩放')
        self.btn_flip = QPushButton('翻转')

        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1_1)
        hbox1.addWidget(self.btn_main_outer)
        hbox1.addWidget(self.btn_main_inner)
        hbox1.addWidget(self.btn_main_color)
        hbox1.addStretch(1)
        hbox1.addSpacing(100)
        hbox1.addWidget(label1_2)
        hbox1.addWidget(self.btn_cutter_outer)
        hbox1.addWidget(self.btn_cutter_inner)
        hbox1.addSpacing(100)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label2)
        hbox2.addWidget(self.btn_move)
        hbox2.addWidget(self.btn_rotate)
        hbox2.addWidget(self.btn_zoom)
        hbox2.addWidget(self.btn_flip)
        hbox2.addStretch(1)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addWidget(container_frame)
        self.setLayout(vbox)

    def input_main_outer(self, pressed):
        if pressed:
            if self.state == PLGState.NORMAL:
                self.state = PLGState.INPUT_MAIN_OUTER
                self.main_polygon = Polygon()
                self.paint_area.repaint()
            else:
                raise
        else:
            if self.state == PLGState.INPUT_MAIN_OUTER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.is_valid():
                    self.main_polygon = None
            else:
                raise

    def input_main_inner(self, pressed):
        if pressed:
            if self.state == PLGState.NORMAL:
                self.state = PLGState.INPUT_MAIN_INNER
                self.main_polygon.insert_inner(PlainPolygon())
                # self.paint_area.repaint()
            else:
                raise
        else:
            if self.state == PLGState.INPUT_MAIN_INNER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.inners[-1].is_valid():
                    self.main_polygon.inners.pop()
            else:
                raise

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.paint_area.current_color = color
            self.paint_area.repaint()


class PLGPaintArea(QLabel):

    def __init__(self, main_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_widget = main_widget
        self.current_color = Qt.black
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white")
        self.setCursor(Qt.CrossCursor)

    @property
    def main_polygon(self):
        return self.main_widget.main_polygon

    @property
    def cutter_polygon(self):
        return self.main_widget.cutter_polygon

    def paintEvent(self, e):
        painter = QPainter()
        painter.begin(self)
        self.draw_polygon(painter)
        painter.end()

    def draw_polygon(self, painter):
        # point1 = Point(20, 20)
        # point2 = Point(20, 200)
        # point3 = Point(200, 200)
        # point4 = Point(200, 20)
        # point5 = Point(110, 40)
        # point6 = Point(180, 120)
        # point7 = Point(40, 180)
        # plain_polygon1 = PlainPolygon([point1, point2, point3, point4])
        # plain_polygon2 = PlainPolygon([point5, point6, point7])
        # polygon = Polygon(plain_polygon1)
        # polygon.insert_inner(plain_polygon2)
        # fill_polygon(self, polygon, painter=painter, color=self.current_color)

        if self.main_polygon:
            fill_polygon(self, self.main_polygon, painter=painter, color=self.current_color)

        if self.cutter_polygon:
            self.cutter_polygon.draw(painter=painter, color=self.current_color)

        print('-------------------------------------------------')

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if self.main_widget.state == PLGState.INPUT_MAIN_OUTER:
            self.main_polygon.outer.insert(-1, Point(x, y))
            self.repaint()
        elif self.main_widget.state == PLGState.INPUT_MAIN_INNER:
            self.main_polygon.inners[-1].insert(-1, Point(x, y))
            self.repaint()

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if self.main_widget.state == PLGState.INPUT_MAIN_OUTER:
            print(x, y)
        elif self.main_widget.state == PLGState.INPUT_MAIN_INNER:
            print(x, y)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PLGMainWindow()
    sys.exit(app.exec_())
