"""
Runs PolyDraw scripts.
"""

from src.parser import parse_polygon, parse_commands

# parse_polygon("polygon pol_y_12a1_: points = (1 2, 4 5, 7 8) color = (255, 0, 0)")

# code = """
#     polygon pol:
#         points = (1 2, 5 6, 7 8)
#         color = (255, 0, 0)

#     polygon pol1:
#         points = (5 2, 5 9, 7 8)
#         color = (255, 0, 255)
#     """

# parse_commands(code)

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

    scale l:
        factor = 0.5
        origin = (0 0)

    plot l
"""
        
parsed = parse_commands(code, {})