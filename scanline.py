from PyQt5.QtCore import Qt, QLineF, QPointF

from figures import Polygon, PlainPolygon, Line, Point, PLGFloat
from utils import count_list


def fill_polygon(paint_area, polygon, painter, color=Qt.black):
    if polygon.is_valid():
        scanline_fill(paint_area=paint_area, polygon=polygon, painter=painter, color=color)
    else:
        painter.setPen(color)
        polygon.draw(painter, color)


def scanline_fill(paint_area, polygon, painter, color=Qt.black):
    if not polygon.is_valid():
        raise Exception('多边形不合法，无法使用扫描线填充')

    painter.setPen(color)
    area_width = paint_area.width()
    area_height = paint_area.height()
    area_xmin = 0
    area_ymin = 0
    area_xmax = area_width - 1
    area_ymax = area_height - 1

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
                    points.remove(point)
            else:
                raise Exception('交点个数不合法')

        # 交点排序、配对，线段涂色
        points = sorted(points, key=lambda p: p.x())
        for i in range(0, len(points), 2):
            point1 = points[i]
            try:
                point2 = points[i+1]
            except:
                print(points)
                print(polygon.sides)
                raise
            painter.drawLine(point1.x(), ynow, point2.x(), ynow)

    # 再单独画一次边框
    polygon.draw(painter, color)
