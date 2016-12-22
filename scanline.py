from numpy import array, zeros
from PyQt5.QtCore import Qt, QLineF, QPointF

from figures import Polygon, PlainPolygon, Line, Point, PLGFloat
from utils import count_list


def fill_polygon(paint_area, polygon, painter=None, color=Qt.black, to_matrix=False):
    if polygon.is_valid():
        result = scanline_fill(paint_area=paint_area, polygon=polygon,
                               painter=painter, color=color, to_matrix=to_matrix)
    elif polygon.outer.is_valid():
        valid_polygon = Polygon(outer=polygon.outer)
        invalid_inners = []
        for inner in polygon.inners:
            if inner.is_valid():
                valid_polygon.insert_inner(inner)
            else:
                invalid_inners.append(inner)
        scanline_fill(paint_area=paint_area, polygon=valid_polygon, painter=painter, color=color)
        for inner in invalid_inners:
            inner.draw(painter, Qt.white)
    else:
        polygon.draw(painter, color)
    if to_matrix:
        return result


def scanline_fill(paint_area, polygon, painter=None, color=Qt.black, to_matrix=False):
    if not polygon.is_valid():
        raise Exception('多边形不合法，无法使用扫描线填充')

    area_width = paint_area.width()
    area_height = paint_area.height()
    area_xmin = 0
    area_ymin = 0
    area_xmax = area_width - 1
    area_ymax = area_height - 1

    if to_matrix:
        matrix = zeros((area_height, area_width), dtype=int)
    else:
        painter.setPen(color)

    for ynow in range(area_ymin, area_ymax + 1):
        xline = QLineF(area_xmin, ynow, area_xmax, ynow)

        # 求交点
        points = []
        sides = []
        for side in polygon.sides:
            point = Point()
            intersect_type = side.intersect(xline, point)
            if intersect_type == QLineF.BoundedIntersection:
                points.append(point)
                sides.append(side)

        # 重复交点处理
        for point, count in count_list(points):
            if count == 1:
                continue
            elif count == 2:
                index1 = points.index(point)
                index2 = points.index(point, index1 + 1)
                side1 = sides[index1]
                side2 = sides[index2]
                another_y1 = side1.get_another_vertice(point).y()
                another_y2 = side2.get_another_vertice(point).y()
                if (another_y1 - ynow) * (another_y2 - ynow) < 0:  # 异侧：只留一个交点
                    points.pop(index2)
                    sides.pop(index2)
            else:
                raise Exception('交点个数不合法')

        # 交点排序、配对，线段涂色
        points = sorted(points, key=lambda p: p.x())
        for i in range(0, len(points), 2):
            x1 = round(points[i].x())
            try:
                x2 = round(points[i+1].x())
                if to_matrix:
                    matrix[ynow][x1:x2+1].fill(1)
                else:
                    painter.drawLine(x1, ynow, x2, ynow)
            except:
                pass

    # 再单独画一次边框
    for side in polygon.sides:
        x1 = round(side.x1())
        y1 = round(side.y1())
        x2 = round(side.x2())
        y2 = round(side.y2())
        if to_matrix:
            if y1 == y2:
                matrix[y1][x1:x2+1].fill(1)
        else:
            painter.drawLine(x1, y1, x2, y2)

    if to_matrix:
        return matrix
    else:
        return


def fill_matrix(paint_area, matrix, painter=None, color=Qt.black):
    area_width = paint_area.width()
    area_height = paint_area.height()
    area_xmin = 0
    area_ymin = 0
    area_xmax = area_width - 1
    area_ymax = area_height - 1

    painter.setPen(color)

    for ynow in range(area_ymin, area_ymax + 1):
        for xnow in range(area_xmin, area_xmax + 1):
            if matrix[ynow][xnow]:
                painter.drawPoint(xnow, ynow)
