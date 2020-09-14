import numpy as np
import json
import svgwrite


RM_PX = 16
RELAY_WIDTH_PX = 32
RELAY_HEIGHT_PX = 2 * RELAY_WIDTH_PX

GRID_WIDTH_Y = 32
GRID_WIDTH_X = 32
GRID_START_X = 3
GRID_START_Y = 3


def grid_xy(x, y):
    return (
        RM_PX * x + GRID_START_X * RM_PX,
        RM_PX * (GRID_WIDTH_Y - y) + GRID_START_Y * RM_PX,
    )


RELAY_TERMINALS = {
    "coil": {"pos": [0, 0]},
    "in": {"pos": [0, 2]},
    "out_lower": {"pos": [4, 1]},
    "out_upper": {"pos": [4, 3]},
}


def add_relay(dwg, pos=[10, 10], state=0, stroke_width=2.0, stroke="black"):

    x = pos[0]
    y = pos[1]

    # frame
    # =====
    dwg.add(
        dwg.line(
            grid_xy(x + 1, y - 1),
            grid_xy(x + 1, y + 4),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x + 3, y - 1),
            grid_xy(x + 3, y + 4),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    dwg.add(
        dwg.line(
            grid_xy(x + 1, y - 1),
            grid_xy(x + 3, y - 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x + 1, y + 4),
            grid_xy(x + 3, y + 4),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    # terminals
    # =========
    dwg.add(
        dwg.line(
            grid_xy(x + 0, y + 0),
            grid_xy(x + 1.5, y + 0),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x + 0, y + 2),
            grid_xy(x + 1.5, y + 2),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    dwg.add(
        dwg.line(
            grid_xy(x + 2.5, y + 1),
            grid_xy(x + 4, y + 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x + 2.5, y + 3),
            grid_xy(x + 4, y + 3),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    if state == 0:
        Y = -1
        coil_fill = "white"
    else:
        Y = 1
        coil_fill = "black"

    dwg.add(
        dwg.line(
            grid_xy(x + 1.5, y + 2),
            grid_xy(x + 2.5, y + 2 + Y),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    # coil
    # ====
    dwg.add(
        dwg.circle(
            grid_xy(x + 2, y + 0),
            0.6 * RM_PX,
            stroke=stroke,
            stroke_width=stroke_width,
            fill=coil_fill,
        )
    )


def add_grid(
    dwg, size=[GRID_WIDTH_X, GRID_WIDTH_Y], stroke="gray", stroke_width=0.3
):
    for xl in range(size[0]):
        if xl % 10 == 0:
            xw = stroke_width
        else:
            xw = 0.5 * stroke_width

        dwg.add(
            dwg.line(
                grid_xy(xl, 0),
                grid_xy(xl, size[1]),
                stroke=stroke,
                stroke_width=xw,
            )
        )
        if xl % 5 == 0:
            dwg.add(dwg.text("{:>3d}".format(xl), grid_xy(xl - 0.5, -1),))
    dwg.add(dwg.text("X", grid_xy(size[0] + 1, -1)))

    for yl in range(size[1]):
        if yl % 10 == 0:
            yw = stroke_width
        else:
            yw = 0.5 * stroke_width

        dwg.add(
            dwg.line(
                grid_xy(0, yl),
                grid_xy(size[0], yl),
                stroke=stroke,
                stroke_width=yw,
            )
        )
        if yl % 5 == 0:
            dwg.add(dwg.text("{:>3d}".format(yl), grid_xy(-1, (yl - 0.5))))
        dwg.add(dwg.text("Y", grid_xy(-1, size[1] + 1)))


def add_bar(dwg, start=(0, 0), stop=(1, 1), stroke_width=2.0, stroke="black"):
    dwg.add(
        dwg.line(
            grid_xy(start[0], start[1]),
            grid_xy(stop[0], stop[1]),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )


def add_node(dwg, pos=(0, 0), stroke_width=0.0, stroke="black"):
    dwg.add(
        dwg.circle(
            grid_xy(pos[0], pos[1]),
            0.3 * RM_PX,
            stroke=stroke,
            stroke_width=stroke_width,
            fill=stroke,
        )
    )


def add_label_node(dwg, pos, name, stroke_width=2.0, stroke="black"):
    x, y = pos

    w = 2 / 3 * len(name)

    dwg.add(
        dwg.line(
            grid_xy(x, y),
            grid_xy(x - 1, y + 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x, y),
            grid_xy(x - 1, y - 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    dwg.add(
        dwg.line(
            grid_xy(x - 1 - w, y - 1),
            grid_xy(x - 1, y - 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x - 1 - w, y + 1),
            grid_xy(x - 1, y + 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x - 1 - w, y - 1),
            grid_xy(x - 1 - w, y + 1),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(dwg.text(name, grid_xy(x - w, y)))


def add_curcuit(dwg, circuit_stage_B):
    cir = circuit_stage_B
    add_grid(dwg=dwg)

    for bar in cir["bars"]:
        start = cir["nodes"][bar[0]]["pos"]
        stop = cir["nodes"][bar[1]]["pos"]
        add_bar(dwg=dwg, start=start, stop=stop)

    for node_key in cir["nodes"]:
        if len(cir["nodes"][node_key]["bars"]) > 2:
            add_node(dwg=dwg, pos=cir["nodes"][node_key]["pos"])

    for relay_key in cir["relays"]:
        relay = cir["relays"][relay_key]
        add_relay(dwg=dwg, pos=relay["pos"], state=0)

        for terminal_key in RELAY_TERMINALS:
            node_key = "relay" + "/" + relay_key + "/" + terminal_key
            if len(cir["nodes"][node_key]["bars"]) > 1:
                add_node(dwg=dwg, pos=cir["nodes"][node_key]["pos"])


def draw_circuit(path, circuit_stage_B):
    dwg = svgwrite.Drawing(path, profile="tiny")
    add_curcuit(dwg=dwg, circuit_stage_B=circuit_stage_B)
    dwg.save()
