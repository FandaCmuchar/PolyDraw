"""
Parses given input of PolyDraw DSL to AST.
"""

from parsy import string, regex ,seq
from typing import Any
from src.my_ast import PointNode, LineNode, PolygonNode, CircleNode, GeometryListNode

# Tokens
spaces = regex(r"\s*")
lexeme = lambda p: p << spaces
comma = lexeme(string(','))
l_bracket = lexeme(regex(r"[\(\[]"))
r_bracket = lexeme(regex(r"[\)\]]"))
decimal = lexeme(regex(r'-?\d+(\.\d+)?').map(float))
colon = lexeme(string(':'))
identifier = regex(r'[a-zA-Z_][a-zA-Z0-9_]*')
identifier_list = l_bracket >> identifier.sep_by(comma) << r_bracket

# Parser pro bod
point_parser = seq(decimal << spaces, decimal).combine(lambda x, y: [x, y])

# Parser pro seznam bodů
points_list = l_bracket >> point_parser.sep_by(comma) << r_bracket
color_list = l_bracket >> seq(decimal << (comma | spaces), decimal << (comma | spaces), decimal) << r_bracket

def tokenize_script(script: str) -> list[str]:
    blocks = script.strip().split("\n\n")  # Dvě nové řádky znamenají nový blok
    return [block.strip() for block in blocks if block.strip()] # Odstranit prázdné bloky

def parse_commands(code: str):
    variables = {}
    commands = tokenize_script(code)
    for command in commands:
        parsed = parse_command(command)
        variables[parsed["name"]] = parsed["obj"]
    
    return variables      

def parse_command(command: str) -> None:
    # Rozpoznání typu příkazu
    if command.startswith("point"):
        parsed = parse_point(command)
    elif command.startswith("line"):
        parsed = parse_line(command)
    elif command.startswith("polygon"):
        parsed = parse_polygon(command)
    elif command.startswith("circle"):
        parsed = parse_circle(command)
    else:
        raise ValueError(f"Unknown command: {command}")
    
    return parsed

def parse_point(command: str):
    point_def = seq(
        lexeme(string("point")) >> identifier << lexeme(string(":")),
        ((lexeme(string("coord")) >> lexeme(string("="))) | spaces) >> points_list,
        lexeme(string("color")) >> lexeme(string("=")) >> color_list
    ).combine(lambda name, point, color: {"name": name, "obj": PointNode(point[0], color)})
    
    return point_def.parse(command)

def parse_line(command: str):
    line_def = seq(
        lexeme(string("line")) >> lexeme(identifier) << lexeme(string(":")),
        lexeme(string('points')) >> lexeme(string('=')) >> points_list,
        lexeme(string('color'))  >> lexeme(string('=')) >> color_list
    ).combine(lambda name, points, color: {"name": name, "obj": LineNode(points=points, color=color)})

    return line_def.parse(command)
    
def parse_polygon(command: str) -> Any:    
    polygon_def = seq(
        lexeme(string('polygon')) >> lexeme(identifier) << lexeme(string(':')),
        lexeme(string('points')) >> lexeme(string('=')) >> points_list,
        lexeme(string('color'))  >> lexeme(string('=')) >> color_list
    ).combine(lambda name, points, color: {"name": name, "obj": PolygonNode(points=points, color=color)})
    
    return polygon_def.parse(command)

def parse_circle(command: str):
    circle_def = seq(
        lexeme(string("circle")) >> lexeme(identifier) << lexeme(string(":")),
        ((lexeme(string("center")) >> lexeme(string("="))) | spaces) >> points_list,
        ((lexeme(string("radius")) >> lexeme(string("="))) | spaces) >> decimal,
        lexeme(string('color'))  >> lexeme(string('=')) >> color_list
    ).combine(lambda name, center, radius, color: {"name": name, "obj": CircleNode(center=center[0], radius=radius, color=color)})
    
    return circle_def.parse(command)

def parse_geometry_list(command: str, variables: dict):
    list_parser = seq(
        string('list') >> spaces >> identifier << colon << spaces,
        identifier_list
    ).combine(lambda name, geom_list: {"name": name, "geoms": geom_list})
    
    parsed = list_parser.parse(command)
    geom_list = GeometryListNode()
    
    for geom_name in parsed["geoms"]:
        if geom_name in variables:
            geom_list.add(variables[geom_name])
        else:
            raise ValueError(f"Unknown geometry variable: {geom_name}")

    return geom_list