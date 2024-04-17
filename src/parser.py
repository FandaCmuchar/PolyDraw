"""
Parses given input of PolyDraw DSL to AST.
"""

from parsy import whitespace, string, regex ,seq
from typing import Any
from src.my_ast import PolygonNode

# Tokens
spaces = regex(r"\s*")
lexeme = lambda p: p << spaces
comma = lexeme(string(','))
l_bracket = lexeme(string('('))
r_bracket = lexeme(string(')'))
decimal = lexeme(regex(r'-?\d+(\.\d+)?').map(float))
colon = lexeme(string(':'))

point = seq(decimal, decimal).combine(lambda x, y: (x, y))
points_list = l_bracket >> point.sep_by(comma) << r_bracket


def parse_polygon(code: str) -> Any:
    variables = {}

    polygon = string("polygon").result(PolygonNode)
    

    identifier = lexeme(regex(r'[a-zA-Z_][a-zA-Z0-9_]*'))
    
    # Parser pro polygon
    polygon = seq(
        string('polygon') >> whitespace >> identifier,
        colon,
        string('points') >> whitespace >> points_list
    ).combine(lambda name, _, points: PolygonNode(name, points))
    
    assignment = seq(identifier << spaces << string("=") << spaces, polygon).combine(variables.setdefault)
    print(assignment)
    print(polygon)
    return polygon