"""
Parses given input of PolyDraw DSL to AST.
"""

from parsy import string, regex ,seq
from typing import Any
from src.my_ast import ASTNode, PointNode, LineNode, PolygonNode, CircleNode, GeometryListNode, TransformNode, RepeatCycleNode, DrawNode

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

def tokenize_script_to_blocks(script: str) -> list[str]:
    lines = [line for line in script.strip().split("\n") if line.strip()]
    blocks = []
    current_block = []

    for line in lines:
        # Odsazení aktuálního řádku
        indent_level = len(line) - len(line.lstrip())

        if indent_level == 0:
            # Pokud má řádek nulové odsazení, zahájíme nový blok
            if current_block:
                blocks.append("\n".join(current_block))  # Uložíme předchozí blok
            current_block = [line]  # Zahájíme nový blok
        else:
            # Pokud má řádek odsazení, přidáme jej do aktuálního bloku
            current_block.append(line)

    # Přidání posledního bloku
    if current_block:
        blocks.append("\n".join(current_block))

    return blocks

def parse_commands(code: str, variables: dict = {}):
    blocks = tokenize_script_to_blocks(code)
    for block in blocks:
        parsed = parse_command(block, variables)
        if parsed is not None:
            if isinstance(parsed, dict) and "name" in parsed:
                variables[parsed["name"]] = parsed["obj"]
            else:
                # There was transformation or cycle so evaluate
                parsed.evaluate()

    return variables      

def parse_command(command: str, variables: dict) -> None:
    command = command.strip()
    if command.startswith("point"):
        parsed = parse_point(command)
    elif command.startswith("line"):
        parsed = parse_line(command)
    elif command.startswith("polygon"):
        parsed = parse_polygon(command)
    elif command.startswith("circle"):
        parsed = parse_circle(command)
    elif command.startswith("list"):
        parsed = parse_geometry_list(command, variables=variables)
    elif command.startswith(("translate", "scale", "rotate")):
        parsed = parse_transform(command, variables=variables)
    elif command.startswith("repeat"):
        parsed = parse_repeat_cycle(command, variables)
    elif command.startswith("plot"):
        parsed = parse_plot(command, variables)
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

    return {"name": parsed["name"], "obj": geom_list}

def parse_transform(command: str, variables: dict):
    transform_parser = seq(
        lexeme(identifier), # transform type
        lexeme(identifier) << colon, # geometry object or list
        lexeme(identifier) << lexeme(string("=")), # first argument name
        lexeme(decimal), # float value
        lexeme(identifier) << lexeme(string("=")), # second argument name
        (lexeme(l_bracket) >> lexeme(point_parser) << lexeme(r_bracket) | lexeme(decimal) | lexeme(string("center"))) # point
    ).combine(
        lambda transform, geom_obj, arg1_name, arg1_value, arg2_name, arg2_value: 
        {
            "transform": transform, "obj": geom_obj, "kwargs": {
                arg1_name: arg1_value, arg2_name: arg2_value if not isinstance(arg2_value, list) else tuple(arg2_value)
                }
        }
    )

    parsed = transform_parser.parse(command)

    if isinstance(parsed["obj"], GeometryListNode):
        for var in parsed["obj"].evaluate():
            if var not in list(variables.values()):
                raise ValueError(f"Object: {var} is not known variable")
    elif isinstance(parsed["obj"], ASTNode):
        if parsed["obj"] not in list(variables.values()):
            raise ValueError(f"Object: {var} is not known variable")
        
    match parsed["transform"]:
        case "translate":
            if "x" not in parsed["kwargs"] or "y" not in parsed["kwargs"]:
                raise ValueError(f"Translate has wrong arguments: {parsed['kwargs']}")
        case "rotate":
            if "angle" not in parsed["kwargs"] or "origin" not in parsed["kwargs"]:
                raise ValueError(f"Rotate has wrong arguments: {parsed['kwargs']}")
        case "scale":
            if "factor" not in parsed["kwargs"] or "origin" not in parsed["kwargs"]:
                raise ValueError(f"Scale has wrong arguments: {parsed['kwargs']}")
            
    if len(parsed["kwargs"]) != 2:
        raise ValueError(f"Wrong input arguments count.")

    return TransformNode(geometry_nodes=variables[parsed["obj"]], operation=parsed["transform"], kwargs=parsed["kwargs"])

def parse_repeat_cycle(command: str, variables: dict):
    repeat_parser = seq(
        lexeme(string("repeat")),
        regex(r'\d+').map(int) << colon
    ).combine(lambda _, repetitions: repetitions)
 
    lines = command.split("\n")
    repetitions = repeat_parser.parse(lines[0])
    
    body_blocks = "\n".join([line[4:] for line in lines[1:]])
    body = [parse_command(block, variables) for block in tokenize_script_to_blocks(body_blocks)]
    return RepeatCycleNode(repetitions, body)

def parse_plot(command: str, variables: dict):
    plot_parser = seq(
        lexeme(string("plot")),
        lexeme(identifier)
    ).combine(lambda _, name: name)

    name = plot_parser.parse(command)

    if name not in variables:
        raise ValueError(f"Variable {name} not known")

    return DrawNode(geometry_nodes=variables[name])