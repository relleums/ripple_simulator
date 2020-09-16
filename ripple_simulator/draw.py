import numpy as np
import json
import svgwrite
from . import simulate


RM_PX = 16
RELAY_WIDTH_PX = 32
RELAY_HEIGHT_PX = 2 * RELAY_WIDTH_PX

GRID_WIDTH_Y = 48
GRID_WIDTH_X = 48
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


def add_relay(
    dwg,
    pos=[10, 10],
    state=0,
    power_coil=0,
    power_in=0,
    power_out_upper=0,
    power_out_lower=0,
    stroke_width=2.0,
    stroke="black",
):

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
    if power_coil == 1:
        dwg.add(
            dwg.line(
                grid_xy(x + 0, y + 0),
                grid_xy(x + 1.5, y + 0),
                stroke="red",
                stroke_width=2 * stroke_width,
            )
        )
    dwg.add(
        dwg.line(
            grid_xy(x + 0, y + 0),
            grid_xy(x + 1.5, y + 0),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

    if power_in == 1:
        dwg.add(
            dwg.line(
                grid_xy(x + 0, y + 2),
                grid_xy(x + 1.5, y + 2),
                stroke="red",
                stroke_width=2 * stroke_width,
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

    if power_out_lower == 1:
        dwg.add(
            dwg.line(
                grid_xy(x + 2.5, y + 1),
                grid_xy(x + 4, y + 1),
                stroke="red",
                stroke_width=2 * stroke_width,
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

    if power_out_upper == 1:
        dwg.add(
            dwg.line(
                grid_xy(x + 2.5, y + 3),
                grid_xy(x + 4, y + 3),
                stroke="red",
                stroke_width=2 * stroke_width,
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

    if state < simulate.STATE_OFF_LT:
        Y = -1
        coil_fill = "white"
    elif state > simulate.STATE_ON_GT:
        Y = 1
        coil_fill = "red"
    else:
        num_floating_states = simulate.STATE_ON_GT - simulate.STATE_OFF_LT
        Y = (state - simulate.STATE_OFF_LT) / num_floating_states - 0.5
        coil_fill = "orange"

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
    dwg,
    size=[GRID_WIDTH_X, GRID_WIDTH_Y],
    stroke="gray",
    stroke_width=0.3,
    fill="white",
):
    dwg.add(
        dwg.rect(
            (0, 0),
            (size[0] * RM_PX, size[1] * RM_PX),
            stroke="none",
            stroke_width=0,
            fill=fill,
        )
    )
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


def add_bar(
    dwg, start=(0, 0), stop=(1, 1), stroke_width=2.0, stroke="black", power=0
):
    if power == 1:
        dwg.add(
            dwg.line(
                grid_xy(start[0], start[1]),
                grid_xy(stop[0], stop[1]),
                stroke="red",
                stroke_width=stroke_width * 2,
            )
        )
    dwg.add(
        dwg.line(
            grid_xy(start[0], start[1]),
            grid_xy(stop[0], stop[1]),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )


def add_capacitor(
    dwg, pos=[0, 0], capacity=10, state=5, stroke_width=2.0, stroke="black"
):
    x = pos[0]
    y = pos[1]

    fill = state / capacity
    if fill > 1.0:
        fill = 1.0

    dwg.add(
        dwg.rect(
            grid_xy(x - 1, y - 0.5),
            (2 * RM_PX * fill, RM_PX * 1),
            stroke="none",
            stroke_width=0,
            fill="red",
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x, y),
            grid_xy(x, y - 0.5),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x - 1, y - 0.5),
            grid_xy(x + 1, y - 0.5),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x - 1, y - 1.5),
            grid_xy(x + 1, y - 1.5),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x, y - 1.5),
            grid_xy(x, y - 2),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )


def add_node(dwg, pos=(0, 0), stroke_width=0.0, stroke="black", power=0):
    node_radius = 0.3 * RM_PX
    if power == 1:
        dwg.add(
            dwg.circle(
                grid_xy(pos[0], pos[1]),
                1.3 * node_radius,
                stroke=stroke,
                stroke_width=stroke_width,
                fill="red",
            )
        )
    dwg.add(
        dwg.circle(
            grid_xy(pos[0], pos[1]),
            node_radius,
            stroke=stroke,
            stroke_width=stroke_width,
            fill=stroke,
        )
    )


def add_label_node(dwg, pos, name, stroke_width=2.0, stroke="black"):
    x, y = pos

    w = len(name)

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
    dwg.add(dwg.text(name, grid_xy(x - w - 0.5, y - 0.3)))


def add_curcuit(dwg, circuit, circuit_state):
    cir = circuit
    add_grid(dwg=dwg, size=[128, 64])

    for bar_idx, bar in enumerate(cir["bars"]):
        start = cir["nodes"][bar[0]]["pos"]
        stop = cir["nodes"][bar[1]]["pos"]
        if len(bar) == 2:
            add_bar(
                dwg=dwg,
                start=start,
                stop=stop,
                power=circuit_state["bars"][bar_idx],
            )
        else:
            add_bar(
                dwg=dwg,
                start=start,
                stop=stop,
                power=circuit_state["bars"][bar_idx],
                stroke_width=0.1
            )

    for node_key in cir["nodes"]:
        if len(cir["nodes"][node_key]["bars"]) > 2:
            add_node(
                dwg=dwg,
                pos=cir["nodes"][node_key]["pos"],
                power=circuit_state["nodes"][node_key],
            )
        if "name" in cir["nodes"][node_key]:
            add_label_node(
                dwg=dwg,
                pos=cir["nodes"][node_key]["pos"],
                name=cir["nodes"][node_key]["name"],
            )

    for relay_key in cir["relays"]:
        relay = cir["relays"][relay_key]
        add_relay(
            dwg=dwg,
            pos=relay["pos"],
            state=circuit_state["relays"][relay_key],
        )

        for terminal_key in RELAY_TERMINALS:
            node_key = "relays" + "/" + relay_key + "/" + terminal_key
            if len(cir["nodes"][node_key]["bars"]) > 1:
                add_node(
                    dwg=dwg,
                    pos=cir["nodes"][node_key]["pos"],
                    power=circuit_state["nodes"][node_key],
                )

    for cap_key in cir["capacitors"]:
        add_capacitor(
            dwg=dwg,
            pos=cir["capacitors"][cap_key]["pos"],
            state=circuit_state["capacitors"][cap_key],
            capacity=circuit["capacitors"][cap_key]["capacity"],
        )


def draw_circuit(path, circuit, circuit_state):
    dwg = svgwrite.Drawing(path, profile="tiny")
    add_curcuit(dwg=dwg, circuit=circuit, circuit_state=circuit_state)
    dwg.save()
