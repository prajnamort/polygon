from PyQt5.QtCore import Qt, QLineF, QPointF

from utils import isclose


class Polygon(object):
    """多边形（带内环）"""

    def __init__(self, outer=None, inners=None):
        if outer:
            self.outer = outer
        else:
            self.outer = PlainPolygon()
        if inners:
            self.inners = inners
        else:
            self.inners = []
        self.num_inners = len(self.inners)

    def is_valid(self):
        """是否为合法的多边形。"""
        return all([plain_polygon.is_valid() for plain_polygon in self.plain_polygons])

    @property
    def plain_polygons(self):
        """所有的普通多边形。"""
        result = list(self.inners)
        result.insert(0, self.outer)
        return result

    @property
    def vertices(self):
        """所有的顶点。"""
        result = []
        for plain_polygon in self.plain_polygons:
            result.extend(plain_polygon.vertices)
        return result

    @property
    def sides(self):
        """所有的边。"""
        result = []
        for plain_polygon in self.plain_polygons:
            result.extend(plain_polygon.sides)
        return result

    @property
    def center(self):
        return self.outer.center

    def insert_inner(self, inner):
        """增加一个新的内环"""
        self.inners.append(inner)
        self.num_inners += 1

    def draw(self, painter, color=Qt.black):
        for plain_polygon in self.plain_polygons:
            plain_polygon.draw(painter, color)

    def copy(self):
        outer = self.outer.copy()
        inners = [inner.copy() for inner in self.inners]
        return Polygon(outer, inners)


class PlainPolygon(object):
    """普通多边形（不带内环）

    注：可能为非法多边形（边数小于3）
    """

    def __init__(self, vertices=None):
        self.vertices = []
        if vertices:
            for vertice in vertices:
                self.insert(-1, vertice)

    @property
    def n(self):
        return len(self.vertices)

    def is_valid(self):
        """是否为合法的多边形。"""
        return self.n >= 3

    @property
    def looped_vertices(self):
        result = list(self.vertices)
        result.append(self.vertices[0])
        return result

    @property
    def sides(self):
        """所有的边"""
        result = []
        for i in range(self.n):
            result.append(Line(self.looped_vertices[i], self.looped_vertices[i+1]))
        return result

    @property
    def center(self):
        """图形中心"""
        if not self.is_valid():
            return None
        x_list = [point.x() for point in self.vertices]
        y_list = [point.y() for point in self.vertices]
        x_min, x_max = min(x_list), max(x_list)
        y_min, y_max = min(y_list), max(y_list)
        return Point((x_min+x_max)/2, (y_min+y_max/2))

    def insert(self, index, point):
        """增加一个新的顶点

        返回值:
            success (bool), message (str)
        """
        if point in self.vertices:
            return False, '输入失败：顶点不允许重合'

        # if self.n >= 2:
        #     pairs = [(Line(self.vertices[-1], point), self.vertices[-1]),
        #              (Line(point, self.vertices[0]), self.vertices[0])]
        # elif self.n == 1:
        #     pairs = [(Line(self.vertices[-1], point), self.vertices[-1])]
        # else:
        #     pairs = []

        # for line, vertice in pairs:
        #     for side in self.sides:
        #         intersect_point = Point()
        #         intersect_type = side.intersect(line, intersect_point)
        #         if intersect_type == QLineF.BoundedIntersection:
        #             pass  # TMP

        self.vertices.insert(index, point)
        return True, '输入成功：%s' % point

    def __str__(self):
        return ' - '.join([str(vertice) for vertice in self.vertices])

    def draw(self, painter, color=Qt.black):
        for side in self.sides:
            side.draw(painter, color)

    def copy(self):
        return PlainPolygon([point.copy() for point in self.vertices])


class Line(QLineF):
    """线段"""

    def __str__(self):
        return ' - '.join([str(self.p1()), str(self.p2())])

    def draw(self, painter, color=Qt.black):
        painter.setPen(color)
        painter.drawLine(self.x1(), self.y1(), self.x2(), self.y2())

    def get_another_vertice(self, vertice):
        p1 = self.p1()
        p2 = self.p2()
        vertice = Point(vertice)
        if vertice == p1:
            return p2
        elif vertice == p2:
            return p1
        else:
            raise Exception('指定点并非该线段的顶点')

    def p1(self):
        return Point(super().p1())

    def p2(self):
        return Point(super().p2())

    def x1(self):
        return PLGFloat(super().x1())

    def y1(self):
        return PLGFloat(super().y1())

    def x2(self):
        return PLGFloat(super().x2())

    def y2(self):
        return PLGFloat(super().y2())

    def copy(self):
        return Line(self.p1.copy(), self.p2.copy())


class Point(QPointF):
    """点"""

    def __str__(self):
        return '(%s, %s)' % (self.x(), self.y())

    def __eq__(self, other):
        return (self.x() == other.x() and self.y() == other.y())

    def draw(self, painter, color=Qt.black):
        painter.setPen(color)
        painter.drawPoint(self.x(), self.y())

    def x(self):
        return PLGFloat(super().x())

    def y(self):
        return PLGFloat(super().y())

    def copy(self):
        return Point(self.x(), self.y())


class PLGFloat(float):

    def __lt__(self, other):
        return super().__lt__(other) and not isclose(self, other)

    def __gt__(self, other):
        return super().__gt__(other) and not isclose(self, other)

    def __eq__(self, other):
        return isclose(self, other)

    def __le__(self, other):
        return super().__le__(other) or isclose(self, other)

    def __ge__(self, other):
        return super().__ge__(other) or isclose(self, other)

    def __ne__(self, other):
        return not isclose(self, other)
