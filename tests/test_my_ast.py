from src.my_ast import PointNode, LineNode, PolygonNode, CircleNode, TransformNode
from shapely import Point

def test_point_node_initialization():
    x, y = 5, 10
    point_node = PointNode(x, y)
    assert point_node.point.x == x and point_node.point.y == y, "PointNode does not correctly initialize its point."

def test_point_node_evaluation():
    point_node = PointNode(3, 4)
    evaluated_point = point_node.evaluate()
    assert evaluated_point.x == 3 and evaluated_point.y == 4, "PointNode.evaluate() does not return the correct point."

def test_line_node_initialization():
    start = PointNode(0, 0)
    end = PointNode(1, 1)
    line_node = LineNode(start, end)
    assert list(line_node.line.coords) == [(0, 0), (1, 1)], "LineNode does not correctly initialize its line."

def test_line_node_evaluation():
    start = PointNode(0, 0)
    end = PointNode(1, 1)
    line_node = LineNode(start, end)
    evaluated_line = line_node.evaluate()
    assert list(evaluated_line.coords) == [(0, 0), (1, 1)], "LineNode.evaluate() does not return the correct line."

def test_polygon_node_initialization_and_evaluation():
    points = [PointNode(0, 0), PointNode(1, 0), PointNode(1, 1), PointNode(0, 1)]
    polygon_node = PolygonNode(points)
    evaluated_polygon = polygon_node.evaluate()
    assert list(evaluated_polygon.exterior.coords) == [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)], "PolygonNode does not correctly handle the creation or evaluation of polygons."
    
def test_circle_node_initialization():
    center = (5, 5)
    radius = 1
    circle_node = CircleNode(center=center, radius=radius)

    assert circle_node.center == center, "CircleNode does not initialize center correctly."
    assert circle_node.radius == radius, "CircleNode does not initialize radius correctly."

def test_circle_node_evaluation():
    center = 3, 4
    radius = 15
    circle_node = CircleNode(center, radius)

    evaluated_circle = circle_node.evaluate()
    expected_circle = Point(center).buffer(radius)
    assert evaluated_circle.equals(expected_circle), "CircleNode.evaluate() does not return the correct circle geometry."

def test_transform_node_translation():
    point_node = PointNode(1, 1)
    transform_node = TransformNode(point_node, 'translate', xoff=10, yoff=5)
    translated_point = transform_node.evaluate()
    assert translated_point.x == 11 and translated_point.y == 6, "TransformNode does not correctly translate points."