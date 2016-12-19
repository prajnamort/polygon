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
