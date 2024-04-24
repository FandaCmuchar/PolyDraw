from src.my_ast import PointNode, LineNode, PolygonNode, CircleNode
from src.parser import parse_point, parse_line, parse_polygon, parse_commands, parse_circle
import pytest

def test_point_parse():
    polygon_str = "point p: (3 4) color = (255, 0, 0)"

    point = parse_point(polygon_str)

    assert isinstance(point["obj"], PointNode)
    assert point["name"] == "p"

def test_multiple_points_parse():
    code = """
point p1:
    coord = (1 2)
    color = (255, 0, 0)

point p2:
    coord = [5 2]
    color = [255, 0, 255]
    """

    parsed = parse_commands(code)
    points_objs = list(parsed.items())
    assert isinstance(parsed, dict)
    assert points_objs[0][0] == "p1"
    
    assert [points_objs[0][1].evaluate().x, points_objs[0][1].evaluate().y] == [1, 2]
    assert points_objs[0][1].color == [255, 0, 0]

    assert points_objs[1][0] == "p2"
    assert [points_objs[1][1].evaluate().x, points_objs[1][1].evaluate().y] == [5, 2]
    assert points_objs[1][1].color == [255, 0, 255]

def test_line_parse():
    line_str = "line l1: points = (1 0, 1 5) color = (0 255 0)"
    line = parse_line(line_str)

    assert isinstance(line["obj"], LineNode)
    assert line["name"] == "l1"

def test_multiple_lines_parse():
    code = """
line l_1:
    points = (1 2, 3 5)
    color = (255, 0, 0)

line l_2:
    points = [5 2, 8 9]
    color = [255 0 255]
    """

    parsed = parse_commands(code)
    assert isinstance(parsed, dict)
    assert "l_1" in parsed
    
    assert list(parsed["l_1"].evaluate().coords) == [(1, 2), (3, 5)]
    assert parsed["l_1"].color == [255, 0, 0]

    assert "l_2" in parsed
    assert list(parsed["l_2"].evaluate().coords) == [(5, 2), (8, 9)]
    assert parsed["l_2"].color == [255, 0, 255]

def test_polygon_parse():
    polygon_str = "polygon pol_y_12a1_: points = (1 2, 4 5, 7 8) color = (255, 0, 0)"

    polygon = parse_polygon(polygon_str)

    assert isinstance(polygon["obj"], PolygonNode)
    assert polygon["name"] == "pol_y_12a1_"

def test_multiple_polygon_parse():
    code = """
polygon pol:
    points = (1 2, 5 6, 7 8)
    color = (255, 0, 0)

polygon pol1:
    points = [5 2, 5 9, 7 8]
    color = [255, 0, 255]
    """

    polygons = parse_commands(code)
    assert isinstance(polygons, dict)
    assert "pol" in polygons
    
    assert list(polygons["pol"].evaluate().exterior.coords) == [(1, 2), (5, 6), (7, 8), (1, 2)]
    assert polygons["pol"].color == [255, 0, 0]

    assert "pol1" in polygons
    assert list(polygons["pol1"].evaluate().exterior.coords) == [(5, 2), (5, 9), (7, 8), (5, 2)]
    assert polygons["pol1"].color == [255, 0, 255]

def test_circle_parse():
    circle_str = "circle c: center = (1 2) radius = 5 color = (255, 0, 0)"

    circle = parse_circle(circle_str)

    assert isinstance(circle["obj"], CircleNode)
    assert circle["name"] == "c"

def test_multiple_circles_parse():
    code = """
circle c1:
    center = (1 2)
    radius = 5
    color = (255, 0, 0)

circle c2:
    center = (5 2)
    radius = 3
    color = [255, 0, 255]
    """

    parsed = parse_commands(code)
    assert isinstance(parsed, dict)

    assert "c1" in parsed    
    assert parsed["c1"].center == [1, 2]
    assert parsed["c1"].radius == 5
    assert parsed["c1"].color == [255, 0, 0]

    assert "c2" in parsed
    assert parsed["c2"].center == [5, 2]
    assert parsed["c2"].radius == 3
    assert parsed["c2"].color == [255, 0, 255]

def test_geometries_list():
    code = """
polygon p1:
    points = (1 2, 3 4, 5 6)
    color = (255, 0, 0)

polygon p2:
    points = (8 3, 5 7, 5 6)
    color = (255, 0, 255)

list polygons: [p1, p2]
    """

    parsed = parse_commands(code)
    assert isinstance(parsed, dict)
    assert "polygons" in parsed
    assert len(parsed["polygons"].geometries) == 2
    assert isinstance(parsed["polygons"].geometries[0], PolygonNode)

def test_transforms():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

scale p1:
    factor = 2
    origin = (0 0)

rotate p1:
    angle = 90
    origin = (0 0)

translate p1:
    x = 1
    y = 0    

    """
    parsed = parse_commands(code)
    assert isinstance(parsed, dict)
    assert "p1" in parsed
    assert list(parsed["p1"].evaluate().exterior.coords) == [(1, 0), (-1, 2), (1, 2), (1, 0)]


def test_list_transforms():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

polygon p2:
    points = (0 0, -1 -1, -1 0)
    color = (255, 255, 0)

list l:
    [p1, p2]
    
translate l:
    x = 1
    y = 0
    """

    parsed = parse_commands(code)
    assert isinstance(parsed, dict)
    assert "p1" in parsed
    assert list(parsed["p1"].evaluate().exterior.coords) == [(1, 0), (2, 1), (2, 0), (1, 0)]
    assert "p2" in parsed
    assert list(parsed["p2"].evaluate().exterior.coords) == [(1, 0), (0, -1), (0, 0), (1, 0)]

def test_cycle():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

repeat 2:
    translate p1:
        x = 1
        y = 0
    """

    parsed = parse_commands(code, {})
    assert isinstance(parsed, dict)
    assert len(parsed) == 1
    assert "p1" in parsed
    assert list(parsed["p1"].evaluate().exterior.coords) == [(2, 0), (3, 1), (3, 0), (2, 0)]

def test_list_cycle():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

polygon p2:
    points = (0 0, -1 -1, -1 0)
    color = (255, 255, 0)

list l:
    [p1, p2]

repeat 2:
    translate l:
        x = 1
        y = 0
    """

    parsed = parse_commands(code, {})
    assert isinstance(parsed, dict)
    print(parsed)
    assert len(parsed) == 3
    assert "p1" in parsed and "p2" in parsed
    assert list(parsed["p1"].evaluate().exterior.coords) == [(2, 0), (3, 1), (3, 0), (2, 0)]
    assert list(parsed["p2"].evaluate().exterior.coords) == [(2, 0), (1, -1), (1, 0), (2, 0)]

def test_double_cycle():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

repeat 2:
    repeat 2:
        translate p1:
            x = 1
            y = 0
    """

    parsed = parse_commands(code, {})
    assert isinstance(parsed, dict)
    assert len(parsed) == 1
    assert "p1" in parsed
    assert list(parsed["p1"].evaluate().exterior.coords) == [(4, 0), (5, 1), (5, 0), (4, 0)]


def test_polygons_plot():
    code = """
polygon p1:
    points = (0 0, 1 1, 1 0)
    color = (255, 0, 0)

polygon p2:
    points = (0 0, -1 -1, -1 0)
    color = (255, 255, 0)

list l: 
    [p1, p2]

plot l
    """
        
    parsed = parse_commands(code, {})
    assert len(parsed) == 3

def test_points_plot():
    code = """
point p1:
    coord = (0 0)
    color = (255, 0, 0)

point p2:
    coord = (-1 -1)
    color = (255, 255, 0)

list l: 
    [p1, p2]

plot l
    """
        
    parsed = parse_commands(code, {})
    assert len(parsed) == 3

def test_circle_plot():
    code = """
circle c1:
    center = (1 2)
    radius = 5
    color = (255, 0, 0)

plot c1
    """
        
    parsed = parse_commands(code, {})
    assert len(parsed) == 1