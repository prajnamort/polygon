import numpy


def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    """比较浮点数是否相等"""
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def count_list(l):
    items = []
    counts = []
    for item in l:
        if item not in items:
            items.append(item)
            counts.append(l.count(item))
    return zip(items, counts)


def angle_between(line1, line2):
    p1 = (line1.x2()-line1.x1(), line1.y2()-line1.y1())
    p2 = (line2.x2()-line2.x1(), line2.y2()-line2.y1())
    ang1 = numpy.arctan2(*p1[::-1])
    ang2 = numpy.arctan2(*p2[::-1])
    return -((ang1 - ang2) % (2 * numpy.pi))
