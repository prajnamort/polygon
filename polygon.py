#!/usr/bin/python3

import sys, random
import math
from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QApplication, QDesktopWidget, QHBoxLayout, QVBoxLayout,
    QGridLayout, QPushButton, QLabel, QFrame, QColorDialog, QMessageBox,)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt

from figures import Polygon, PlainPolygon, Line, Point
from scanline import fill_polygon, fill_matrix
from utils import angle_between


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


class PLGPaintArea(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.parent().parent()
        self.main_widget = self.parent()
        self.setFocusPolicy(Qt.StrongFocus)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: white")
        self.setCursor(Qt.CrossCursor)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        self.main_widget.draw_polygon(painter)
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event):
        self.main_widget.paint_area_mousePressEvent(event)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.main_widget.paint_area_mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.main_widget.paint_area_mouseMoveEvent(event)
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        self.main_widget.paint_area_wheelEvent(event)
        super().wheelEvent(event)

    def keyPressEvent(self, event):
        self.main_widget.paint_area_keyPressEvent(event)
        super().keyPressEvent(event)


class PLGState(object):
    NORMAL = 0  # 正常
    INPUT_MAIN_OUTER = 10  # 输入多边形（主多边形）
    INPUT_MAIN_INNER = 11  # 输入内环（主多边形）
    INPUT_CUTTER_OUTER = 20  # 输入多边形（裁剪多边形）
    INPUT_CUTTER_INNER = 21  # 输入内环（裁剪多边形）
    MOVE = 50  # 移动
    ROTATE = 60  # 旋转


class PLGMainWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = self.parent()
        self.main_polygon = None
        self.cutter_polygon = None
        self.cutted = False
        self.state = PLGState.NORMAL
        self.current_color = QColor('#ebc9ff')
        self.center_point = None
        self.initUI()

        # 帮用户点下“输入多边形”按钮
        self.btn_main_outer.clicked.emit()

        # TEST CASE 1
        # p1 = Point(200, 200)
        # p2 = Point(300, 200)
        # p3 = Point(200, 300)
        # p4 = Point(300, 300)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 2
        # p1 = Point(200, 200)
        # p2 = Point(300, 200)
        # p3 = Point(400, 100)
        # p4 = Point(500, 300)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 3
        # p1 = Point(200, 200)
        # p2 = Point(300, 200)
        # p3 = Point(400, 100)
        # p4 = Point(500, 300)
        # p5 = Point(600, 200)
        # p6 = Point(700, 200)
        # p7 = Point(700, 400)
        # p8 = Point(200, 400)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4, p5, p6, p7, p8])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 4
        # p1 = Point(200, 400)
        # p2 = Point(300, 400)
        # p3 = Point(200, 200)
        # p4 = Point(100, 400)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 5
        # p1 = Point(200, 400)
        # p2 = Point(100, 400)
        # p3 = Point(400, 400)
        # p4 = Point(300, 200)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 5
        # p1 = Point(200, 300)
        # p2 = Point(100, 300)
        # p3 = Point(400, 300)
        # p4 = Point(350, 500)
        # p5 = Point(300, 300)
        # p6 = Point(250, 100)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4, p5, p6])
        # self.main_polygon = Polygon(plain_polygon)

        # TEST CASE 6
        # p1 = Point(200, 300)
        # p2 = Point(100, 300)
        # p3 = Point(400, 300)
        # p4 = Point(250, 500)
        # p5 = Point(300, 300)
        # p6 = Point(250, 100)
        # plain_polygon = PlainPolygon([p1, p2, p3, p4, p5, p6])
        # self.main_polygon = Polygon(plain_polygon)

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
        self.btn_main_inner = QPushButton('增加内环')
        self.btn_main_inner.clicked.connect(self.input_main_inner)

        label2_1 = QLabel('裁剪多边形：')
        label2_1.setMinimumWidth(100)
        self.btn_cutter_outer = QPushButton('输入多边形')
        self.btn_cutter_outer.clicked.connect(self.input_cutter_outer)
        self.btn_cutter_inner = QPushButton('增加内环')
        self.btn_cutter_inner.clicked.connect(self.input_cutter_inner)
        self.btn_cut = QPushButton('开始裁剪')
        self.btn_cut.clicked.connect(self.cut)

        label3_1 = QLabel('其它操作：')
        label3_1.setMinimumWidth(100)
        self.btn_move = QPushButton('平移')
        self.btn_move.clicked.connect(self.move)
        self.btn_rotate = QPushButton('旋转')
        self.btn_rotate.clicked.connect(self.rotate)
        self.btn_zoom = QPushButton('缩放')
        self.btn_zoom.clicked.connect(self.zoom)
        self.btn_flip_y = QPushButton('左右翻转')
        self.btn_flip_y.clicked.connect(self.flip_y)
        self.btn_flip_x = QPushButton('上下翻转')
        self.btn_flip_x.clicked.connect(self.flip_x)

        label3_2 = QLabel('设置：')
        label3_2.setMinimumWidth(60)
        self.btn_main_color = QPushButton('选择颜色')
        self.btn_main_color.clicked.connect(self.select_color)
        self.btn_select_center = QPushButton('选择中心点')
        self.btn_select_center.clicked.connect(self.select_center)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1_1)
        hbox1.addWidget(self.btn_main_outer)
        hbox1.addWidget(self.btn_main_inner)
        hbox1.addStretch(1)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(label2_1)
        hbox2.addWidget(self.btn_cutter_outer)
        hbox2.addWidget(self.btn_cutter_inner)
        hbox2.addWidget(self.btn_cut)
        hbox2.addStretch(1)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(label3_1)
        hbox3.addWidget(self.btn_move)
        hbox3.addWidget(self.btn_rotate)
        hbox3.addWidget(self.btn_zoom)
        hbox3.addWidget(self.btn_flip_y)
        hbox3.addWidget(self.btn_flip_x)
        hbox3.addStretch(1)
        hbox3.addSpacing(100)
        hbox3.addWidget(label3_2)
        hbox3.addWidget(self.btn_main_color)
        hbox3.addWidget(self.btn_select_center)
        hbox3.addSpacing(100)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addWidget(container_frame)
        self.setLayout(vbox)

    def showMessage(self, message):
        self.main_window.statusBar().showMessage(message)

    def showMessageBox(self, message):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle('提示')
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.show()
        return None

    def draw_polygon(self, painter):
        if self.cutted:
            matrix1 = fill_polygon(self, self.main_polygon, to_matrix=True)
            matrix2 = fill_polygon(self, self.cutter_polygon, to_matrix=True)
            cutted_matrix = matrix1 & matrix2
            fill_matrix(self.paint_area, cutted_matrix,
                        painter=painter, color=self.current_color)
        else:
            if self.main_polygon is not None:
                fill_polygon(self.paint_area, self.main_polygon,
                             painter=painter, color=self.current_color)
            if self.cutter_polygon is not None:
                self.cutter_polygon.draw(painter=painter, color=Qt.black)
        if self.center_point is None:
            self.center_point = Point(self.paint_area.width()/2, self.paint_area.height()/2)
        pen = QPen(Qt.red)
        pen.setWidth(8)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPoint(self.center_point)

    def reset_cutted(self):
        if self.cutted:
            self.main_polygon = None
            self.cutter_polygon = None
            self.cutted = False
            self.paint_area.repaint()

    def input_main_outer(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.reset_cutted()
        self.state = PLGState.INPUT_MAIN_OUTER
        self.main_polygon = Polygon()
        self.paint_area.repaint()

    def input_main_inner(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.reset_cutted()
        if not self.main_polygon:
            return self.showMessageBox('请先输入主多边形外环')
        self.state = PLGState.INPUT_MAIN_INNER
        self.main_polygon.insert_inner(PlainPolygon())
        self.paint_area.repaint()

    def input_cutter_outer(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.reset_cutted()
        if not self.main_polygon:
            return self.showMessageBox('请先输入主多边形')
        self.state = PLGState.INPUT_CUTTER_OUTER
        self.cutter_polygon = Polygon()
        self.paint_area.repaint()

    def input_cutter_inner(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.reset_cutted()
        if not self.main_polygon:
            return self.showMessageBox('请先输入主多边形')
        if not self.cutter_polygon:
            return self.showMessageBox('请先输入裁剪多边形外环')
        self.state = PLGState.INPUT_CUTTER_INNER
        self.cutter_polygon.insert_inner(PlainPolygon())
        self.paint_area.repaint()

    def cut(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        if not self.main_polygon:
            return self.showMessageBox('请先输入主多边形')
        if not self.cutter_polygon:
            return self.showMessageBox('请先输入裁剪多边形')
        self.cutted = True
        self.paint_area.repaint()

    def move(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.showMessageBox('请使用鼠标"左键"进行平移')

    def rotate(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.showMessageBox('请使用鼠标"右键"进行旋转')

    def zoom(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.showMessageBox('请使用鼠标"滚轮"进行缩放')

    def flip_y(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        if not self.main_polygon:
            self.showMessageBox('请先输入主多边形')
            self.paint_area.repaint()
            return
        center = self.center_point
        points = self.main_polygon.vertices
        if self.cutted:
            points.extend(self.cutter_polygon.vertices)
        for point in points:
            point.setX(2 * center.x() - point.x())
        self.paint_area.repaint()

    def flip_x(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        if not self.main_polygon:
            self.showMessageBox('请先输入主多边形')
            self.paint_area.repaint()
            return
        center = self.center_point
        points = self.main_polygon.vertices
        if self.cutted:
            points.extend(self.cutter_polygon.vertices)
        for point in points:
            point.setY(2 * center.y() - point.y())
        self.paint_area.repaint()

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = color
            self.showMessage('输入颜色：%s' % color.name())
        self.paint_area.repaint()

    def select_center(self):
        if self.state != PLGState.NORMAL:
            return self.showMessageBox('请您先完成当前动作（Enter结束输入）')
        self.showMessageBox('请单击鼠标"中键"选择中心点')

    def paint_area_mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        if self.state == PLGState.INPUT_MAIN_OUTER:
            success, message = self.main_polygon.outer.insert(-1, Point(x, y))
            self.showMessage(message)
            self.paint_area.repaint()
        elif self.state == PLGState.INPUT_MAIN_INNER:
            success, message = self.main_polygon.inners[-1].insert(-1, Point(x, y))
            self.showMessage(message)
            self.paint_area.repaint()
        elif self.state == PLGState.INPUT_CUTTER_OUTER:
            success, message = self.cutter_polygon.outer.insert(-1, Point(x, y))
            self.showMessage(message)
            self.paint_area.repaint()
        elif self.state == PLGState.INPUT_CUTTER_INNER:
            success, message = self.cutter_polygon.inners[-1].insert(-1, Point(x, y))
            self.showMessage(message)
            self.paint_area.repaint()
        elif self.state == PLGState.NORMAL:
            if event.button() == Qt.LeftButton:
                if not self.main_polygon:
                    self.showMessageBox('请先输入主多边形')
                    self.paint_area.repaint()
                    return
                self.state = PLGState.MOVE
                self.orig_mouse_point = Point(x, y)
                self.orig_main_polygon = self.main_polygon.copy()
                if self.cutted:
                    self.orig_cutter_polygon = self.cutter_polygon.copy()
                self.paint_area.repaint()
            elif event.button() == Qt.RightButton:
                if not self.main_polygon:
                    self.showMessageBox('请先输入主多边形')
                    self.paint_area.repaint()
                    return
                self.state = PLGState.ROTATE
                self.orig_mouse_point = Point(x, y)
                self.orig_main_polygon = self.main_polygon.copy()
                if self.cutted:
                    self.orig_cutter_polygon = self.cutter_polygon.copy()
                self.paint_area.repaint()
            elif event.button() == Qt.MidButton:
                self.center_point = Point(x, y)
                self.showMessage('已选定中心点：%s' % self.center_point)
                self.paint_area.repaint()

    def paint_area_mouseReleaseEvent(self, event):
        x = event.x()
        y = event.y()
        if self.state == PLGState.MOVE:
            self.state = PLGState.NORMAL
            self.paint_area.repaint()
        elif self.state == PLGState.ROTATE:
            self.state = PLGState.NORMAL
            self.paint_area.repaint()

    def paint_area_mouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        if self.state == PLGState.MOVE:
            orig_mouse_x = self.orig_mouse_point.x()
            orig_mouse_y = self.orig_mouse_point.y()
            orig_points = self.orig_main_polygon.vertices
            points = self.main_polygon.vertices
            if self.cutted:
                orig_points.extend(self.orig_cutter_polygon.vertices)
                points.extend(self.cutter_polygon.vertices)
            for orig_point, point in zip(orig_points, points):
                point.setX(orig_point.x() + (x - self.orig_mouse_point.x()))
                point.setY(orig_point.y() + (y - self.orig_mouse_point.y()))
            if (x + y) % 11 == 0 or (x - y) % 11 == 0:  # 每次都 repaint 的话延迟过高
                self.paint_area.repaint()
        elif self.state == PLGState.ROTATE:
            orig_mouse_x = self.orig_mouse_point.x()
            orig_mouse_y = self.orig_mouse_point.y()
            ox = self.center_point.x()
            oy = self.center_point.y()
            angle = angle_between(Line(self.center_point,
                                       self.orig_mouse_point),
                                  Line(self.center_point,
                                       Point(x, y)))
            orig_points = self.orig_main_polygon.vertices
            points = self.main_polygon.vertices
            if self.cutted:
                orig_points.extend(self.orig_cutter_polygon.vertices)
                points.extend(self.cutter_polygon.vertices)
            for orig_point, point in zip(orig_points, points):
                px, py = orig_point.x(), orig_point.y()
                point.setX(ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy))
                point.setY(oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy))
            if (x + y) % 11 == 0 or (x - y) % 11 == 0:  # 每次都 repaint 的话延迟过高
                self.paint_area.repaint()

    def paint_area_wheelEvent(self, event):
        if self.state != PLGState.NORMAL:
            self.showMessageBox('请您先完成当前动作（Enter结束输入）')
            return
        if not self.main_polygon:
            self.showMessageBox('请先输入主多边形')
            self.paint_area.repaint()
            return
        factor = 1.1 if event.angleDelta().y() > 0 else 0.91
        center = self.center_point
        points = self.main_polygon.vertices
        if self.cutted:
            points.extend(self.cutter_polygon.vertices)
        for point in points:
            point.setX(center.x() + factor * (point.x() - center.x()))
            point.setY(center.y() + factor * (point.y() - center.y()))
        self.paint_area.repaint()

    def paint_area_keyPressEvent(self, event):
        key = event.key()
        if key in [Qt.Key_Enter, Qt.Key_Return]:
            if self.state == PLGState.INPUT_MAIN_OUTER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.is_valid():
                    self.main_polygon = None
            elif self.state == PLGState.INPUT_MAIN_INNER:
                self.state = PLGState.NORMAL
                if not self.main_polygon.inners[-1].is_valid():
                    self.main_polygon.inners.pop()
            elif self.state == PLGState.INPUT_CUTTER_OUTER:
                self.state = PLGState.NORMAL
                if not self.cutter_polygon.is_valid():
                    self.cutter_polygon = None
            elif self.state == PLGState.INPUT_CUTTER_INNER:
                self.state = PLGState.NORMAL
                if not self.cutter_polygon.inners[-1].is_valid():
                    self.cutter_polygon.inners.pop()
            self.paint_area.repaint()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PLGMainWindow()
    sys.exit(app.exec_())
