import numpy as np
import json
import svgwrite
from . import simulate


RM_PX = 10

GRID_WIDTH_Y = 39
GRID_WIDTH_X = 63
GRID_START_X = 5
GRID_START_Y = 5


def grid_xy(x, y):
    return (
        RM_PX * x + GRID_START_X * RM_PX,
        RM_PX * (GRID_WIDTH_Y - y) + GRID_START_Y * RM_PX,
    )


def grid_rot(xy, rot):
    if rot == 0:
        return xy
    elif rot == 1:
        return (xy[1], -xy[0])
    elif rot == 2:
        return (-xy[0], -xy[1])
    elif rot == 3:
        return (-xy[1], xy[0])
    else:
        raise KeyError


def grid_trans(xy, pos):
    return (xy[0] + pos[0], xy[1] + pos[1])


def add_line(dwg, start, stop, stroke, stroke_width):
    dwg.add(
        dwg.line(
            grid_xy(start[0], start[1]),
            grid_xy(stop[0], stop[1]),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

def add_dot(dwg, pos, stroke="black", stroke_width=0.2):
    dwg.add(
        dwg.circle(
            grid_xy(pos[0], pos[1]),
            0.2 * RM_PX,
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )

RELAY_TERMINALS = {
    "in": (0, 0),
    "in2": (3, 0),
    "coil": (0, 4),
    "coil2": (3, 4),
    "out_lower": (0, 5),
    "out_upper": (3, 5),
}


def add_relay(
    dwg,
    pos=[10, 10],
    rot=0,
    state=0,
    power_coil=0,
    power_in=0,
    power_out_upper=0,
    power_out_lower=0,
    stroke_width=2.0,
    stroke="black",
):
    """
    frame
    =====
    cC        cD
    +---------+
    |oUpp oLow|
    |         |
    |coi  coi2|
    |         |
    |         |
    |         |
    |in    in2|
    +---------+
    cA        cB

    Y
    ^
    |
    +----> X
    """
    _cA = (-0.5, -0.5)
    _cB = (+3.5, -0.5)
    _cC = (-0.5, +5.5)
    _cD = (+3.5, +5.5)

    _coil_center = (+1.5, +4.0)
    _in_center = (1.5, 0.0)

    cA = grid_trans(grid_rot(_cA, rot), pos)
    cB = grid_trans(grid_rot(_cB, rot), pos)
    cC = grid_trans(grid_rot(_cC, rot), pos)
    cD = grid_trans(grid_rot(_cD, rot), pos)
    coil_center = grid_trans(grid_rot(_coil_center, rot), pos)
    in_center = grid_trans(grid_rot(_in_center, rot), pos)


    add_line(dwg, cA, cB, stroke, stroke_width)
    add_line(dwg, cB, cD, stroke, stroke_width)
    add_line(dwg, cD, cC, stroke, stroke_width)
    add_line(dwg, cC, cA, stroke, stroke_width)

    # terminals
    # =========
    terminal_pos = {}
    for terminal_key in RELAY_TERMINALS:
        t_pos = RELAY_TERMINALS[terminal_key]
        t_pos_r = grid_trans(grid_rot(xy=t_pos, rot=rot), pos)
        terminal_pos[terminal_key] = t_pos_r
        add_dot(dwg, (t_pos_r[0], t_pos_r[1]), stroke, stroke_width)

    if state < simulate.STATE_OFF_LT:
        sx = -1
        coil_fill = "white"
    elif state > simulate.STATE_ON_GT:
        sx = 1
        coil_fill = "red"
    else:
        num_floating_states = simulate.STATE_ON_GT - simulate.STATE_OFF_LT
        sx = (state - simulate.STATE_OFF_LT) / num_floating_states - 0.5
        coil_fill = "orange"

    _switch_pos = (1.2*sx + 1.5, 5)
    switch_pos = grid_trans(grid_rot(_switch_pos, rot), pos)

    if power_in == 1:
        add_line(dwg, terminal_pos["in"], terminal_pos["in2"], "red", 2*stroke_width)
        add_line(dwg, in_center, coil_center, "red", 2*stroke_width)
        add_line(dwg, switch_pos, coil_center, "red", 2*stroke_width)
    add_line(dwg, terminal_pos["in"], terminal_pos["in2"], stroke, stroke_width)
    add_line(dwg, in_center, coil_center, stroke, stroke_width)
    add_line(dwg, switch_pos, coil_center, stroke, stroke_width)



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
    ow = 1.0
    c1 = (-0.5, -0.5)
    c2 = (GRID_WIDTH_X + 0.5, -0.5)
    c3 = (GRID_WIDTH_X + 0.5, GRID_WIDTH_Y + 0.5)
    c4 = (-0.5, GRID_WIDTH_Y + 0.5)
    add_line(dwg, c1, c2, stroke, ow)
    add_line(dwg, c2, c3, stroke, ow)
    add_line(dwg, c3, c4, stroke, ow)
    add_line(dwg, c4, c1, stroke, ow)

    for xl in range(size[0]):
        if xl % 10 == 0:
            xw = stroke_width
        else:
            xw = 0.5 * stroke_width

        add_line(dwg, (xl, 0), (xl, size[1]), stroke, xw)

        if xl % 5 == 0:
            dwg.add(dwg.text("{:>3d}".format(xl), grid_xy(xl - 0.5, -2),))
    dwg.add(dwg.text("X", grid_xy(size[0] + 1, -1)))

    for yl in range(size[1]):
        if yl % 10 == 0:
            yw = stroke_width
        else:
            yw = 0.5 * stroke_width

        add_line(dwg, (0, yl), (size[0], yl), stroke, yw)

        if yl % 5 == 0:
            dwg.add(dwg.text("{:>3d}".format(yl), grid_xy(-3, (yl - 0.5))))
        dwg.add(dwg.text("Y", grid_xy(-1, size[1] + 1)))


def add_bar(
    dwg, start=(0, 0), stop=(1, 1), stroke_width=2.0, stroke="black", power=0
):
    if power == 1:
        add_line(dwg, start, stop, "red", 2*stroke_width)
    add_line(dwg, start, stop, stroke, stroke_width)


def add_capacitor(
    dwg, pos=(0, 0), capacity=10, state=5, stroke_width=2.0, stroke="black"
):
    sw = stroke_width
    x = pos[0]
    y = pos[1]

    fill = state / capacity
    if fill > 1.0:
        fill = 1.0

    add_dot(dwg, (x, y), stroke, sw)
    add_dot(dwg, (x, y + 1), stroke, sw)

    dwg.add(
        dwg.rect(
            grid_xy(x - 0.75, y + 0.75),
            (1.5 * RM_PX * fill, RM_PX * 0.5),
            stroke="none",
            stroke_width=0,
            fill="red",
        )
    )
    add_line(dwg, (x - 0.75, y + 0.25), (x + 0.75, y + 0.25), stroke, 0.5*sw)
    add_line(dwg, (x - 0.75, y + 0.75), (x + 0.75, y + 0.75), stroke, 0.5*sw)

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
    sw = stroke_width
    w = len(name)
    add_line(dwg, (x, y), (x - 1, y + 0.75), stroke, sw)
    add_line(dwg, (x, y), (x - 1, y - 0.75), stroke, sw)
    add_line(dwg, (x - 1 - w, y - 0.75), (x - 1, y - 0.75), stroke, sw)
    add_line(dwg, (x - 1 - w, y + 0.75), (x - 1, y + 0.75), stroke, sw)
    add_line(dwg, (x - 1 - w, y - 0.75), (x - 1 - w, y + 0.75), stroke, sw)
    dwg.add(dwg.text(name, grid_xy(x - w - 0.5, y - 0.3)))


def add_curcuit(dwg, circuit, circuit_state):
    cir = circuit
    add_grid(dwg=dwg, size=[GRID_WIDTH_X, GRID_WIDTH_Y])

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

        in_state = circuit_state["nodes"]["relays/" + relay_key + "/in"]
        ou_state = circuit_state["nodes"]["relays/" + relay_key + "/out_upper"]
        ol_state = circuit_state["nodes"]["relays/" + relay_key + "/out_lower"]
        add_relay(
            dwg=dwg,
            pos=relay["pos"],
            rot=relay["rot"],
            state=circuit_state["relays"][relay_key],
            power_in=in_state,
            power_out_upper=ou_state,
            power_out_lower=ol_state,
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
