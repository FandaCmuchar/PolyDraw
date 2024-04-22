from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate, rotate, scale

class ASTNode:
    def evaluate(self):
        raise NotImplementedError

class PointNode(ASTNode):
    def __init__(self, xy: tuple[float], color=None):
        self.color = color
        self.point = Point(xy[0], xy[1])

    def evaluate(self):
        return self.point
    
    def __str__(self) -> str:
        return f"PointNode({self.point.x}, {self.point.y})"

class LineNode(ASTNode):
    def __init__(self, points: list[float] = None, start_node: PointNode | tuple[float] = None, end_node: PointNode | tuple[float] = None, color=None):
        self.color = color
        coords = points if points is not None else [start_node.evaluate(), end_node.evaluate()]
        self.line = LineString(coords)

    def evaluate(self):
        return self.line
    
    def __str__(self) -> str:
        return f"LineNode({self.line.coords})"

class PolygonNode(ASTNode):
    def __init__(self, points: PointNode | list[tuple[float | int]], color=None):
        self.color = color
        cords = [(p.evaluate().x, p.evaluate().y) if isinstance(p, PointNode) else p for p in points]
        self.polygon = Polygon(cords)

    def evaluate(self):
        return self.polygon
    
    def __str__(self) -> str:
        return f"PolygonNode({list(self.polygon.exterior.coords)})"

class CircleNode(ASTNode):
    # https://gis.stackexchange.com/questions/190495/getting-intersection-of-circles-using-shapely
    def __init__(self, center, radius, color=None):
        self.color = color
        self.center = center
        self.radius = radius
        self.circle = Point(center).buffer(radius)

    def evaluate(self):
        return self.circle
    
    def __str__(self) -> str:
        return f"CircleNode({self.circle})"
    
class GeometryListNode(ASTNode):
    def __init__(self, geometries: list[ASTNode]) -> None:
        self.geometries = geometries
    
    def add(self, geometry: ASTNode):
        self.geometries.append(geometry)
        

class TransformNode(ASTNode):
    def __init__(self, geometry_nodes: list[ASTNode] | ASTNode, operation: str, **kwargs):
        self.geometries = geometry_nodes if isinstance(geometry_nodes, list) else [geometry_nodes]
        self.operation = operation
        self.kwargs = kwargs

    def evaluate(self):
        base_geoms = [geom.evaluate() for geom in self.geometries]
        if self.operation == 'translate':
            return [translate(base_geom, **self.kwargs) for base_geom in base_geoms]
        elif self.operation == 'rotate':
            return [rotate(base_geom, **self.kwargs) for base_geom in base_geoms]
        elif self.operation == 'scale':
            return [scale(base_geom, **self.kwargs) for base_geom in base_geoms]
        return base_geoms
    
    def __str__(self) -> str:
        return f"TransformNode({self.operation}, {self.geometries})"
