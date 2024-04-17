from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate, rotate, scale

class ASTNode:
    def __init__(self, name: str = "") -> None:
        self.name = name

    def evaluate(self):
        raise NotImplementedError

class PointNode(ASTNode):
    def __init__(self, x, y, name: str = "", color=None):
        super().__init__(name)
        self.color = color
        self.point = Point(x, y)

    def evaluate(self):
        return self.point
    
    def __str__(self) -> str:
        return f"PointNode({self.point.x}, {self.point.y})"

class LineNode(ASTNode):
    def __init__(self, start_node, end_node, name: str = "", color=None):
        super().__init__(name)
        self.color = color
        self.line = LineString([start_node.evaluate(), end_node.evaluate()])

    def evaluate(self):
        return self.line
    
    def __str__(self) -> str:
        return f"LineNode({self.line.coords})"

class PolygonNode(ASTNode):
    def __init__(self, points, name: str = "", color=None):
        super().__init__(name)
        self.color = color
        self.polygon = Polygon([p.evaluate() for p in points])

    def evaluate(self):
        return self.polygon
    
    def __str__(self) -> str:
        return f"PolygonNode({self.polygon.coords})"

class CircleNode(ASTNode):
    def __init__(self, center, radius, name: str = "", color=None):
        super().__init__(name)
        self.color = color
        self.center = center
        self.radius = radius
        self.circle = Point(center).buffer(radius)

    def evaluate(self):
        return self.circle
    
    def __str__(self) -> str:
        return f"CircleNode({self.circle})"

class TransformNode(ASTNode):
    def __init__(self, geometry_node, operation, name: str = "", **kwargs):
        super().__init__(name)
        self.geometry = geometry_node
        self.operation = operation
        self.kwargs = kwargs

    def evaluate(self):
        base_geom = self.geometry.evaluate()
        if self.operation == 'translate':
            return translate(base_geom, **self.kwargs)
        elif self.operation == 'rotate':
            return rotate(base_geom, **self.kwargs)
        elif self.operation == 'scale':
            return scale(base_geom, **self.kwargs)
        return base_geom
    
    def __str__(self) -> str:
        return f"TransformNode({self.operation}, {self.geometry})"
