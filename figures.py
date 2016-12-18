from PyQt5.QtCore import Qt, QLineF, QPointF, QLine, QPoint


class Polygon(object):
    """多边形（带内环）"""

    def __init__(self, outer, inners=None):
        self.outer = outer
        if inners:
            self.inners = inners
        else:
            self.inners = []
        self.num_inners = len(self.inners)

    def is_valid(self):
        """是否为合法的多边形。"""
        return all([plain_polygon.is_valid for plain_polygon in self.plain_polygons])

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

    def insert_inner(self, inner):
        """增加一个新的内环"""
        self.inners.append(inner)
        self.num_inners += 1

    def draw(self, painter, color=Qt.black):
        for side in self.sides:
            side.draw(painter, color)


class PlainPolygon(object):
    """普通多边形（不带内环）

    注：可能为非法多边形（边数小于3）
    """

    def __init__(self, vertices=None):
        self.vertices = []
        self.num_sides = 0
        if vertices:
            for vertice in vertices:
                self.insert(-1, vertice)

    def is_valid(self):
        """是否为合法的多边形。"""
        return len(self.vertices) >= 3

    @property
    def looped_vertices(self):
        result = list(self.vertices)
        result.append(self.vertices[0])
        return result

    @property
    def sides(self):
        """所有的边"""
        result = []
        for i in range(self.num_sides):
            result.append(Line(self.looped_vertices[i], self.looped_vertices[i+1]))
        return result

    def insert(self, index, vertice):
        """增加一个新的顶点

        返回值:
            - 输入成功：新多边形的边数
            - 输入失败：0
        """
        if vertice not in self.vertices:
            self.vertices.insert(index, vertice)
            self.num_sides += 1
            return self.num_sides
        else:
            return 0

    def __str__(self):
        return ' - '.join([str(vertice) for vertice in self.vertices])

    def draw(self, painter, color=Qt.black):
        for side in self.sides:
            side.draw(painter, color)


class Line(QLineF):
    """线段"""

    def __str__(self):
        return ' - '.join([str(self.p1()), str(self.p2())])

    def draw(self, painter, color=Qt.black):
        painter.setPen(color)
        painter.drawLine(self.x1(), self.y1(), self.x2(), self.y2())

    def get_another_vertice(self, vertice):
        p1 = Point(self.p1())
        p2 = Point(self.p2())
        if vertice == p1:
            return p2
        elif vertice == p2:
            return p1
        else:
            raise Exception('指定点并非该线段的顶点')


class Point(QPointF):
    """点"""

    def __str__(self):
        return '(%s, %s)' % (self.x(), self.y())

    def draw(self, painter, color=Qt.black):
        painter.setPen(color)
        painter.drawPoint(self.x(), self.y())
