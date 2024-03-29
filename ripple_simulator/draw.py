import numpy as np
import json
import svgwrite
import os
import tempfile
import shutil
import subprocess
from . import simulate


RM_PX = 27

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


def add_dot(dwg, pos, radius=0.2 * RM_PX, stroke="black", stroke_width=0.2):
    dwg.add(
        dwg.circle(
            grid_xy(pos[0], pos[1]),
            radius,
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )


RELAY_TERMINALS = {
    "in0": (0, 0),
    "in1": (3, 0),
    "coil0": (0, 4),
    "coil1": (3, 4),
    "ncl": (3, 5),
    "nop": (0, 5),
}


def add_relay(
    dwg,
    pos=[10, 10],
    rot=0,
    state=0,
    power_coil=0,
    power_in=0,
    power_nop=0,
    power_ncl=0,
    stroke_width=0.1,
    stroke="black",
):
    case_stroke = svgwrite.rgb(75, 75, 75, "%")
    term_stroke = svgwrite.rgb(50, 50, 50, "%")
    sw = stroke_width * RM_PX
    """
    frame
    =====
    cC        cD
    +---------+
    |nop   ncl|
    |         |
    |cl0   cl1|
    |         |
    |         |
    |         |
    |in0   in1|
    +---------+
    cA        cB

    Y
    ^
    |
    +----> X
    """
    _cA = (-0.4, -0.4)
    _cB = (+3.4, -0.4)
    _cC = (-0.4, +5.4)
    _cD = (+3.4, +5.4)

    _switch_anchor = (+1.5, +4.0)
    _coil_center = (+1.5, +2.5)
    _in_center = (1.5, 0.0)

    cA = grid_trans(grid_rot(_cA, rot), pos)
    cB = grid_trans(grid_rot(_cB, rot), pos)
    cC = grid_trans(grid_rot(_cC, rot), pos)
    cD = grid_trans(grid_rot(_cD, rot), pos)
    switch_anchor = grid_trans(grid_rot(_switch_anchor, rot), pos)
    coil_center = grid_trans(grid_rot(_coil_center, rot), pos)
    in_center = grid_trans(grid_rot(_in_center, rot), pos)

    add_line(dwg, cA, cB, case_stroke, sw)
    add_line(dwg, cB, cD, case_stroke, sw)
    add_line(dwg, cD, cC, case_stroke, sw)
    add_line(dwg, cC, cA, case_stroke, sw)

    if state < simulate.STATE_OFF_LT:
        sx = 1
    elif state > simulate.STATE_ON_GT:
        sx = -1
    else:
        num_floating_states = simulate.STATE_ON_GT - simulate.STATE_OFF_LT
        sx = -((state - simulate.STATE_OFF_LT) / num_floating_states) + 0.5

    # coil color
    # ----------
    if state == simulate.STATE_FULLY_ON:
        coil_fill = "red"
    elif state == simulate.STATE_FULLY_OFF:
        coil_fill = "white"
    else:
        coil_fill = "orange"

    dwg.add(
        dwg.circle(
            grid_xy(coil_center[0], coil_center[1]),
            1.0 * RM_PX,
            stroke=stroke,
            stroke_width=0.025 * RM_PX,
            fill=coil_fill,
        )
    )

    # terminals
    # =========
    terminal_pos = {}
    for terminal_key in RELAY_TERMINALS:
        t_pos = RELAY_TERMINALS[terminal_key]
        t_pos_r = grid_trans(grid_rot(xy=t_pos, rot=rot), pos)
        terminal_pos[terminal_key] = t_pos_r
        add_dot(dwg, (t_pos_r[0], t_pos_r[1]), 0.1 * RM_PX, term_stroke, sw)

    _switch_pos = (1.5 * sx + 1.5, 5)
    switch_pos = grid_trans(grid_rot(_switch_pos, rot), pos)

    if power_in == 1:
        add_line(dwg, terminal_pos["in0"], terminal_pos["in1"], "red", sw)
        add_line(dwg, in_center, switch_anchor, "red", sw)
        add_line(dwg, switch_pos, switch_anchor, "red", sw)
    add_line(
        dwg, terminal_pos["in0"], terminal_pos["in1"], term_stroke, 0.5 * sw
    )
    add_line(dwg, in_center, switch_anchor, term_stroke, 0.5 * sw)
    add_line(dwg, switch_pos, switch_anchor, term_stroke, 0.5 * sw)


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
            (
                (size[0] + GRID_START_X + 3) * RM_PX,
                (size[1] + GRID_START_Y + 3) * RM_PX,
            ),
            stroke="none",
            stroke_width=0,
            fill=fill,
        )
    )
    ow = 1.0
    c1 = (-0.5, -0.5)
    c2 = (size[0] + 0.5, -0.5)
    c3 = (size[0] + 0.5, size[1] + 0.5)
    c4 = (-0.5, size[1] + 0.5)
    add_line(dwg, c1, c2, stroke, ow)
    add_line(dwg, c2, c3, stroke, ow)
    add_line(dwg, c3, c4, stroke, ow)
    add_line(dwg, c4, c1, stroke, ow)

    for xl in range(size[0] + 1):
        if xl % 5 == 0:
            xw = stroke_width
        else:
            xw = 0.5 * stroke_width

        add_line(dwg, (xl, 0), (xl, size[1]), stroke, xw)

        if xl % 5 == 0:
            dwg.add(
                dwg.text(
                    "{:>3d}".format(xl), grid_xy(xl - 0.5, -2), font_size=30
                )
            )
    dwg.add(dwg.text("X", grid_xy(size[0] + 1, -1), font_size=30))

    for yl in range(size[1] + 1):
        if yl % 5 == 0:
            yw = stroke_width
        else:
            yw = 0.5 * stroke_width

        add_line(dwg, (0, yl), (size[0], yl), stroke, yw)

        if yl % 5 == 0:
            dwg.add(
                dwg.text(
                    "{:>3d}".format(yl), grid_xy(-3, (yl - 0.5)), font_size=30
                )
            )
    dwg.add(dwg.text("Y", grid_xy(-1, size[1] + 1), font_size=30))


def add_bar(
    dwg, start=(0, 0), stop=(1, 1), stroke_width=0.15, stroke="black", power=0
):
    if power == 1:
        add_line(dwg, start, stop, "red", 2 * stroke_width * RM_PX)
    add_line(dwg, start, stop, stroke, stroke_width * RM_PX)


def add_capacitor(
    dwg, pos, rot, capacity, state, stroke_width=2.0, stroke="black",
):
    sw = stroke_width
    case_stroke = svgwrite.rgb(75, 75, 75, "%")
    """           term1
      c3  _______O_______ c2
      c0  _______________ c1
                 O
                  term0
    """
    _term0 = (0, 0)
    _term1 = (0, 1)
    _center = (0, 0.5)
    _c0 = (-0.75, 0.25)
    _c1 = (+0.75, 0.25)
    _c2 = (+0.75, 0.75)
    _c3 = (-0.75, 0.75)

    term0 = grid_trans(grid_rot(_term0, rot), pos)
    term1 = grid_trans(grid_rot(_term1, rot), pos)
    center = grid_trans(grid_rot(_center, rot), pos)
    c0 = grid_trans(grid_rot(_c0, rot), pos)
    c1 = grid_trans(grid_rot(_c1, rot), pos)
    c2 = grid_trans(grid_rot(_c2, rot), pos)
    c3 = grid_trans(grid_rot(_c3, rot), pos)

    fill = state / capacity
    if fill > 1.0:
        fill = 1.0

    add_dot(dwg, term0, 0.1 * RM_PX, stroke, sw)
    add_dot(dwg, term1, 0.1 * RM_PX, stroke, sw)

    add_line(dwg, c0, c1, stroke, 0.5 * sw)
    add_line(dwg, c2, c3, stroke, 0.5 * sw)
    dwg.add(
        dwg.circle(
            grid_xy(center[0], center[1]),
            0.9 * RM_PX,
            stroke=case_stroke,
            stroke_width=sw,
            fill=svgwrite.rgb(100.0 * fill, 0, 0, "%"),
        )
    )


def add_node_name(dwg, pos, name):
    rndx = np.random.uniform() - 0.5
    rndy = np.random.uniform() - 0.5
    dwg.add(dwg.text(name, grid_xy(pos[0] + rndx, pos[1] + rndy)))


def add_node_lamp(dwg, pos=(0, 0), stroke_width=2.0, stroke="black", power=0):
    r = 0.707
    cx = pos[0]
    cy = pos[1]

    # outer circle
    # ------------
    dwg.add(
        dwg.circle(
            grid_xy(cx + 0.5, cy),
            r * RM_PX,
            stroke=stroke,
            stroke_width=stroke_width,
            fill="red" if power else "none",
        )
    )

    # cross
    # -----
    add_cross(
        dwg=dwg,
        pos=[0.5 + cx, cy],
        r=r,
        stroke_width=stroke_width,
        stroke=stroke
    )

    # pins in grid
    # ------------
    for ccxx in [cx, cx + 1]:
        dwg.add(
            dwg.circle(
                grid_xy(ccxx, cy),
                r * RM_PX * 0.1,
                stroke=stroke,
                stroke_width=stroke_width,
                fill="none",
            )
        )


def add_node(
    dwg, pos=(0, 0), name=None, stroke_width=0.0, stroke="black", power=0
):
    node_radius = 0.2 * RM_PX
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
    if name:
        dwg.add(dwg.text(name, grid_xy(pos[0], pos[1])))


def add_node_pin_through(
    dwg, pos=(0, 0), stroke_width=1.0, stroke="black", power=0
):
    x, y = pos
    r = 0.4
    if power:
        add_cross(
            dwg=dwg,
            pos=pos,
            r=r*1.2,
            stroke_width=stroke_width*1.2,
            stroke="red"
        )
    add_cross(
        dwg=dwg,
        pos=pos,
        r=r,
        stroke_width=stroke_width,
        stroke=stroke
    )
    add_line(
        dwg=dwg,
        start=[x-r, y-r],
        stop=[x+r, y-r],
        stroke=stroke,
        stroke_width=stroke_width
    )
    add_line(
        dwg=dwg,
        start=[x+r, y-r],
        stop=[x+r, y+r],
        stroke=stroke,
        stroke_width=stroke_width
    )
    add_line(
        dwg=dwg,
        start=[x-r, y-r],
        stop=[x-r, y+r],
        stroke=stroke,
        stroke_width=stroke_width
    )
    add_line(
        dwg=dwg,
        start=[x-r, y+r],
        stop=[x+r, y+r],
        stroke=stroke,
        stroke_width=stroke_width
    )


def add_cross(
    dwg, pos=(0, 0), r=1.0, stroke_width=1.0, stroke="black",
):
    x, y = pos
    dwg.add(
        dwg.line(
            grid_xy(x - r / np.sqrt(2), y - r / np.sqrt(2)),
            grid_xy(x + r / np.sqrt(2), y + r / np.sqrt(2)),
            stroke=stroke,
            stroke_width=stroke_width,
        )
    )
    dwg.add(
        dwg.line(
            grid_xy(x - r / np.sqrt(2), y + r / np.sqrt(2)),
            grid_xy(x + r / np.sqrt(2), y - r / np.sqrt(2)),
            stroke=stroke,
            stroke_width=stroke_width,
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

    for cap_key in cir["capacitors"]:
        add_capacitor(
            dwg=dwg,
            pos=cir["capacitors"][cap_key]["pos"],
            rot=cir["capacitors"][cap_key]["rot"],
            state=circuit_state["capacitors"][cap_key],
            capacity=circuit["capacitors"][cap_key]["capacity"],
        )
        cap_node_key = "capacitors" + ":" + cap_key
        if len(cir["nodes"][cap_node_key]["bars"]) > 0:
            add_node(
                dwg=dwg,
                pos=cir["nodes"][cap_node_key]["pos"],
                power=circuit_state["nodes"][cap_node_key],
                name=cap_node_key,
            )

    for relay_key in cir["relays"]:
        relay = cir["relays"][relay_key]

        in_state = circuit_state["nodes"]["relays:" + relay_key + "/in0"]
        ou_state = circuit_state["nodes"]["relays:" + relay_key + "/nop"]
        ol_state = circuit_state["nodes"]["relays:" + relay_key + "/ncl"]
        add_relay(
            dwg=dwg,
            pos=relay["pos"],
            rot=relay["rot"],
            state=circuit_state["relays"][relay_key],
            power_in=in_state,
            power_nop=ou_state,
            power_ncl=ol_state,
        )

        for terminal_key in RELAY_TERMINALS:
            node_key = "relays" + ":" + relay_key + "/" + terminal_key
            if len(cir["nodes"][node_key]["bars"]) > 0:
                add_node(
                    dwg=dwg,
                    pos=cir["nodes"][node_key]["pos"],
                    power=circuit_state["nodes"][node_key],
                    name=None,
                )

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
        elif bar[2] == "transparent":
            pass
        elif bar[2] == "wire-y":
            yoff = -0.3
            add_bar(
                dwg=dwg,
                start=start,
                stop=(start[0], start[1] + yoff),
                power=circuit_state["bars"][bar_idx],
                stroke_width=0.1,
            )
            add_bar(
                dwg=dwg,
                start=(start[0], start[1] + yoff),
                stop=(stop[0], stop[1] + yoff),
                power=circuit_state["bars"][bar_idx],
                stroke_width=0.1,
            )
            add_bar(
                dwg=dwg,
                start=stop,
                stop=(stop[0], stop[1] + yoff),
                power=circuit_state["bars"][bar_idx],
                stroke_width=0.1,
            )
        else:
            add_bar(
                dwg=dwg,
                start=start,
                stop=stop,
                power=circuit_state["bars"][bar_idx],
                stroke_width=0.1,
            )

    for node_key in cir["nodes"]:
        if len(cir["nodes"][node_key]["bars"]) > 2:
            add_node(
                dwg=dwg,
                pos=cir["nodes"][node_key]["pos"],
                power=circuit_state["nodes"][node_key],
                name=None,
            )
        if "pin" in cir["nodes"][node_key]:
            add_node_pin_through(
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
        if "lamp" in cir["nodes"][node_key]:
            add_node_lamp(
                dwg=dwg,
                pos=cir["nodes"][node_key]["pos"],
                power=circuit_state["nodes"][node_key],
            )


def draw_circuit(path, circuit, circuit_state):

    with tempfile.TemporaryDirectory(prefix="ripple_simulator_") as tmp_dir:
        tmp_svg_path = os.path.join(tmp_dir, "circuit.svg")
        dwg = svgwrite.Drawing(tmp_svg_path, profile="tiny")
        dwg.attribs["width"] = "1920px"
        dwg.attribs["height"] = "1400px"
        add_curcuit(dwg=dwg, circuit=circuit, circuit_state=circuit_state)
        dwg.save()

        if os.path.splitext(path)[1] == ".svg":
            shutil.move(tmp_svg_path, path)
        else:
            subprocess.call(["convert", tmp_svg_path, path,])
