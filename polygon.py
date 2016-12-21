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
        self.main_widget = PLGMainWidget(self)
        self.setCentralWidget(self.main_widget)
        self.resize_and_center()
        self.setWindowTitle('Polygon')
        self.statusBar().showMessage('Ready.')
        self.show()

    def resize_and_center(self):
        """调整窗口大小并居中"""
        self.setFixedSize(int(QDesktopWidget().width() * 0.618),
                          int(QDesktopWidget().height() * 0.618))
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)


class PLGState(object):
    NORMAL = 0  # 正常
    INPUT_MAIN_OUTER = 10  # 输入多边形（主多边形）
    INPUT_MAIN_INNER = 11  # 输入内环（主多边形）
    INPUT_CUTTER_OUTER = 20  # 输入多边形（裁剪多边形）
    INPUT_CUTTER_INNER = 21  # 输入内环（裁剪多边形）


class PLGMainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.parent()
        self.main_polygon = None
        self.cutter_polygon = None
        self.state = PLGState.NORMAL
        self.initUI()

    def initUI(self):
        self.paint_area = PLGPaintArea(self)
        container_frame = QFrame()
        container_frame.setFrameShape(QFrame.StyledPanel)
        container_box = QHBoxLayout()
        container_box.addWidget(self.paint_area)
        container_box.setContentsMargins(0, 0, 0, 0)
        container_frame.setLayout(container_box)

        label1_1 = QLabel('主多边形：')
        label1_1.setMinimumWidth(100)
        self.btn_main_outer = QPushButton('输入多边形')
        self.btn_main_outer.clicked.connect(self.input_main_outer)
        self.btn_main_inner = QPushButton('输入内环')
        self.btn_main_inner.clicked.connect(self.input_main_inner)
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

    def showMessage(self, message):
        self.main_window.statusBar().showMessage(message)

    def input_main_outer(self):
        if self.state != PLGState.NORMAL:
            raise
        self.state = PLGState.INPUT_MAIN_OUTER
        self.main_polygon = Polygon()
        self.paint_area.repaint()

    def input_main_inner(self):
        if self.state != PLGState.NORMAL:
            raise
        self.state = PLGState.INPUT_MAIN_INNER
        self.main_polygon.insert_inner(PlainPolygon())
        # self.paint_area.repaint()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.paint_area.current_color = color
            self.paint_area.repaint()

    def keyPressEvent(self, event):
        key = event.key()
        print(key)
        if key in [Qt.Key_Enter, Qt.Key_Return]:
            if self.state == PLGState.INPUT_MAIN_OUTER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.is_valid():
                    self.main_polygon = None
            elif self.state == PLGState.INPUT_MAIN_INNER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.inners[-1].is_valid():
                    self.main_polygon.inners.pop()
            self.paint_area.repaint()
        super().keyPressEvent(event)


class PLGPaintArea(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.parent().parent()
        self.main_widget = self.parent()
        self.current_color = Qt.black
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white")
        self.setCursor(Qt.CrossCursor)

        # point1 = Point(254, 379)
        # point2 = Point(527, 309)
        # point3 = Point(508, 430)
        # plain_polygon1 = PlainPolygon([point1, point2, point3])
        # self.main_polygon = Polygon(plain_polygon1)

    @property
    def main_polygon(self):
        return self.main_widget.main_polygon

    @main_polygon.setter
    def main_polygon(self, polygon):
        self.main_widget.main_polygon = polygon

    @property
    def cutter_polygon(self):
        return self.main_widget.cutter_polygon

    @cutter_polygon.setter
    def cutter_polygon(self, polygon):
        self.main_widget.cutter_polygon = polygon

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.draw_polygon(painter)
        painter.end()
        super().paintEvent(event)

    def draw_polygon(self, painter):
        if self.main_polygon:
            fill_polygon(self, self.main_polygon, painter=painter, color=self.current_color)
        if self.cutter_polygon:
            self.cutter_polygon.draw(painter=painter, color=Qt.black)
        print('-------------------------------------------------')

    def showMessage(self, message):
        self.main_window.statusBar().showMessage(message)

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        print(x, y)
        if self.main_widget.state == PLGState.INPUT_MAIN_OUTER:
            success, message = self.main_polygon.outer.insert(-1, Point(x, y))
            self.showMessage(message)
            self.repaint()
        elif self.main_widget.state == PLGState.INPUT_MAIN_INNER:
            success, message = self.main_polygon.inners[-1].insert(-1, Point(x, y))
            self.showMessage(message)
            self.repaint()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if self.main_widget.state == PLGState.INPUT_MAIN_OUTER:
            pass
        elif self.main_widget.state == PLGState.INPUT_MAIN_INNER:
            pass
        super().mouseReleaseEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PLGMainWindow()
    sys.exit(app.exec_())
