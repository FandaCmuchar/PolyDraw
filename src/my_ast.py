from shapely.geometry import Point, LineString, Polygon
from shapely.affinity import translate, rotate, scale

import matplotlib.pyplot as plt

class ASTNode:
    def evaluate(self):
        raise NotImplementedError
    
    def set_geometry(self, geometry: "ASTNode"):
        raise NotImplementedError

class PointNode(ASTNode):
    def __init__(self, xy: tuple[float], color=None):
        self.color = color
        self.point = Point(xy[0], xy[1])

    def evaluate(self):
        return self.point
    
    def set_geometry(self, geometry: Point):
        self.point = geometry
    
    def __str__(self) -> str:
        return f"PointNode({self.point.x}, {self.point.y})"

class LineNode(ASTNode):
    def __init__(self, points: list[float] = None, start_node: PointNode | tuple[float] = None, end_node: PointNode | tuple[float] = None, color=None):
        self.color = color
        coords = points if points is not None else [start_node.evaluate(), end_node.evaluate()]
        self.line = LineString(coords)

    def evaluate(self):
        return self.line

    def set_geometry(self, geometry: LineString):
        self.line = geometry
    
    def __str__(self) -> str:
        return f"LineNode({self.line.coords})"

class PolygonNode(ASTNode):
    def __init__(self, points: PointNode | list[tuple[float | int]], color=None):
        self.color = color
        cords = [(p.evaluate().x, p.evaluate().y) if isinstance(p, PointNode) else p for p in points]
        self.polygon = Polygon(cords)

    def evaluate(self):
        return self.polygon
    
    def set_geometry(self, geometry: Polygon):
        self.polygon = geometry
    
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
        # TODO: check functionality
        return self.circle
    
    def set_geometry(self, geometry: Point):
        self.circle = geometry
    
    def __str__(self) -> str:
        return f"CircleNode({self.circle})"
    
class GeometryListNode(ASTNode):
    def __init__(self) -> None:
        self.geometries = []
    
    def add(self, geometry: ASTNode):
        self.geometries.append(geometry)
    
    def evaluate(self):
        return self.geometries
        

class TransformNode(ASTNode):
    def __init__(self, geometry_nodes: list[ASTNode] | ASTNode, operation: str, **kwargs):
        self.geometries: list[ASTNode] = geometry_nodes.evaluate() if isinstance(geometry_nodes, GeometryListNode) else [geometry_nodes]
        self.operation = operation
        self.kwargs = kwargs["kwargs"] if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict) else kwargs

    def evaluate(self):
        for geom in self.geometries:
            base_geom = geom.evaluate()
            if self.operation == "translate":
                x = self.kwargs.get("x", 0) # digit
                y = self.kwargs.get("y", 0) # digit
                geom.set_geometry(translate(base_geom, xoff=x, yoff=y))
            elif self.operation == "rotate":
                angle = self.kwargs.get("angle", 0) # digit
                origin = self.kwargs.get("origin", "center") # tuple[x, y] or default "center"
                geom.set_geometry(rotate(base_geom, origin=origin, angle=angle))
            elif self.operation == "scale":
                factor = self.kwargs.get("factor", 0.5) # digit
                origin = self.kwargs.get("origin", "center") # tuple[x, y] or default "center"
                geom.set_geometry(scale(base_geom, xfact=factor, yfact=factor, origin=origin))
                            
    def __str__(self) -> str:
        return f"TransformNode({self.operation}, {self.geometries}, {self.kwargs})"
    
class RepeatCycleNode(ASTNode):
    def __init__(self, repetitions: int, body: list[ASTNode]) -> None:
        self.repetitions = repetitions
        self.body = body

    def evaluate(self):
        for _ in range(self.repetitions):
            for el in self.body:
                el.evaluate()

class DrawNode(ASTNode):
    def __init__(self, geometry_nodes: GeometryListNode | ASTNode) -> None:
        self.geometries: list[ASTNode] = geometry_nodes.evaluate() if isinstance(geometry_nodes, GeometryListNode) else [geometry_nodes]
    
    def evaluate(self):
        fig, ax = plt.subplots()
        ax.axis('equal')
        print(len(self.geometries))
        for geometry in self.geometries:
            if isinstance(geometry, PolygonNode):
                x, y = geometry.evaluate().exterior.xy
                color = geometry.color
                ax.fill(x, y, alpha=0.5, fc=[c/255 for c in color], ec='k')  # Vyplnění polygonu
            elif isinstance(geometry, LineNode):
                x, y = geometry.evaluate().xy
                color = geometry.color
                ax.plot(x, y, color=[c/255 for c in color], linestyle="-")
                # vykresli primku
            elif isinstance(geometry, PointNode):
                x, y = geometry.evaluate().xy
                color = geometry.color
                ax.plot(x, y, color=[c/255 for c in color], marker='o')
            elif isinstance(geometry, CircleNode):
                x, y = geometry.evaluate().exterior.xy
                color = geometry.color
                ax.plot(x, y, color=[c/255 for c in color])
        fig.savefig("./test.jpg")
        plt.show()

