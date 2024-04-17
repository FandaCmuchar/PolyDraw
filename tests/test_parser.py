from src.my_ast import PolygonNode
from src.parser import parse_polygon


def test_polygon_parse():
    polygon_str = "polynom pol_y_12a1_: points = (1 2, 4 5, 7 8) color = (255, 0, 0)"

    polygom = parse_polygon(polygon_str)

    assert isinstance(polygom, PolygonNode)
    # TODO: check values of polygon