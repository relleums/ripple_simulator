import numpy as np
from . import build
from . import logic


def make_register(num_bits=8):
    cir = build.empty_circuit()
    cir = build.bar_x(cir=cir, pos=[1, 37], length=60, name="V", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 39], length=60, name="GND", label=True)

    ox = 10

    # bit relays
    for bit in range(num_bits):
        cir["relays"]["bit-{:02d}".format(bit)] = {
            "pos": [ox + 1 + bit * 7, 4],
            "rot": 1,
        }

    # enable relays
    for bit in range(num_bits):
        cir["relays"]["enable-{:02d}".format(bit)] = {
            "pos": [ox + 1 + bit * 7, 9],
            "rot": 1,
        }

    # bits GND
    for bit in range(num_bits):
        cir["nodes"]["gnd-bit-{:02d}".format(bit)] = {"pos": [ox + 5 + bit * 7, 2]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/gnd-bit-{:02d}".format(bit),
                "nodes/gnd-bit-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd-bit-{:02d}".format(bit),
                "relays/bit-{:02d}/coil1".format(bit),
            )
        )

    # bits hold
    for bit in range(num_bits):
        cir["nodes"]["hold-{:02d}".format(bit)] = {"pos": [ox + 6 + bit * 7, 3]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            ("nodes/hold-{:02d}".format(bit), "nodes/hold-{:02d}".format(bit + 1))
        )
    for bit in range(num_bits):
        cir["bars"].append(
            ("nodes/hold-{:02d}".format(bit), "relays/bit-{:02d}/nop".format(bit))
        )

    # bit latch
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit-{:02d}/in0".format(bit),
                "relays/bit-{:02d}/coil0".format(bit),
            )
        )

    # enable GND
    for bit in range(num_bits):
        cir["nodes"]["gnd-ena-{:02d}".format(bit)] = {"pos": [ox + 5 + bit * 7, 7]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/gnd-ena-{:02d}".format(bit),
                "nodes/gnd-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd-ena-{:02d}".format(bit),
                "relays/enable-{:02d}/coil1".format(bit),
            )
        )

    # enable enable
    for bit in range(num_bits):
        cir["nodes"]["ena-ena-{:02d}".format(bit)] = {"pos": [ox + 5 + bit * 7, 8]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/ena-ena-{:02d}".format(bit),
                "nodes/ena-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/ena-ena-{:02d}".format(bit),
                "relays/enable-{:02d}/coil0".format(bit),
            )
        )

    # bit to enable
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/enable-{:02d}/in1".format(bit),
                "relays/bit-{:02d}/in0".format(bit),
            )
        )

    # enable to bus
    for bit in range(num_bits):
        node_name = "BUS{:02d}".format(bit)
        cir["nodes"][node_name] = {"pos": [ox + 6 + bit * 7, 10], "name": node_name}
        cir["bars"].append(
            (
                "relays/enable-{:02d}/nop".format(bit),
                "nodes/" + node_name,
            )
        )


    """
    cir["relays"]["load_not"] = {"pos": [62, 1], "rot": 3}
    cir["bars"].append(
        ("relays/load_not/ncl", "relays/bit_{:d}/nop".format(num_bits - 1))
    )

    cir["relays"]["load"] = {"pos": [62, 11], "rot": 3}
    cir["relays"]["select"] = {"pos": [62, 6], "rot": 3}

    cir["nodes"]["LOAD"] = {"pos": [63, 2], "name": "LOAD"}
    cir["nodes"]["load_0"] = {"pos": [58, 5]}
    cir["nodes"]["load_1"] = {"pos": [59, 5]}
    cir["bars"].append(("nodes/LOAD", "nodes/load_1"))
    cir["bars"].append(("nodes/load_1", "nodes/load_0"))
    cir["bars"].append(("relays/select/coil0", "nodes/load_0"))
    cir = build.trace(
        cir,
        start_node="relays/load_not/coil0",
        stop_node="nodes/load_1",
        trace_nodes=[("001", [59, 1]),],
    )

    # load-not GND
    cir = build.trace(
        cir,
        start_node="relays/load_not/coil1",
        stop_node="nodes/gnd_bit_{:d}".format(num_bits - 1),
        trace_nodes=[("002", [58, 2])],
    )

    # load-not GND
    cir = build.trace(
        cir,
        start_node="relays/load/ncl",
        stop_node="relays/enable_{:d}/coil0".format(num_bits - 1),
        trace_nodes=[("003", [54, 14])],
    )
    """

    return cir


def make_clock(periode):
    cir = build.empty_circuit()

    cir = build.bar_x(cir=cir, pos=[1, 1], length=60, name="A", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 5], length=60, name="B", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 9], length=60, name="C", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 13], length=60, name="D", label=True)

    cir = build.bar_x(cir=cir, pos=[1, 36], length=60, name="V", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 38], length=60, name="GND", label=True)

    cir = build.bar_x(
        cir=cir, pos=[1, 34], length=60, name="CLOCK", label=True
    )
    cir = build.bar_x(cir=cir, pos=[1, 32], length=6, name="FRZ", label=True)

    # latch A
    cir["relays"]["latch_A"] = {"pos": [2, 26], "rot": 0}
    cir["bars"].append(("relays/latch_A/nop", "nodes/FRZ02"))
    cir["bars"].append(("relays/latch_A/coil0", "relays/latch_A/in0"))
    cir["bars"].append(("nodes/A02", "relays/latch_A/in0"))

    # latch C
    cir["relays"]["latch_C"] = {"pos": [7, 26], "rot": 0}
    cir["bars"].append(("relays/latch_C/nop", "nodes/FRZ07"))
    cir["bars"].append(("relays/latch_C/coil0", "relays/latch_C/in0"))
    cir["bars"].append(("nodes/C07", "relays/latch_C/in0"))

    cir = build.bar_x(cir=cir, pos=[5, 29], length=6, name="latch_GND")
    cir["bars"].append(("nodes/latch_GND", "relays/latch_A/coil1"))
    cir["bars"].append(("nodes/latch_GND10", "relays/latch_C/coil1"))
    cir["bars"].append(("nodes/GND11", "nodes/latch_GND11"))

    # XOR(C, D)
    cir["relays"]["xorc"] = {"pos": [17, 26], "rot": 0}
    cir["relays"]["xord"] = {"pos": [22, 26], "rot": 0}
    cir["bars"].append(("relays/xorc/ncl", "relays/xord/nop"))
    cir = build.trace(
        cir,
        "relays/xorc/nop",
        [("xorbar0", [17, 32]), ("xorbar1", [25, 32]),],
        "relays/xord/ncl",
    )
    cir = build.trace(
        cir, "relays/xorc/in0", [("xorclock0", [16, 26]),], "nodes/CLOCK16"
    )

    cir = build.trace(
        cir, "relays/xord/in1", [("xorV", [27, 26]),], "nodes/V27"
    )

    cir = build.trace(
        cir, "relays/xorc/coil0", [("xorc", [18, 30]),], "nodes/C18"
    )
    cir = build.trace(
        cir, "relays/xord/coil0", [("xord", [23, 30]),], "nodes/D23"
    )
    cir = build.bar_x(cir=cir, pos=[20, 29], length=6, name="xorgnd")
    cir["bars"].append(("nodes/xorgnd", "relays/xorc/coil1"))
    cir["bars"].append(("nodes/xorgnd25", "relays/xord/coil1"))
    cir["bars"].append(("nodes/xorgnd26", "nodes/GND26"))

    # Cycler
    # ======

    # CYCLER AD(B, C)
    # ---------------
    cir["relays"]["cycleAD-B"] = {"pos": [35, 31], "rot": 2}
    cir["relays"]["cycleAD-C"] = {"pos": [35, 24], "rot": 2}

    cir = build.trace(
        cir,
        "relays/cycleAD-C/coil1",
        [("cycADgnd0", [31, 20]), ("cycADgnd1", [31, 27]),],
        "relays/cycleAD-B/coil1",
    )
    cir["bars"].append(("nodes/cycADgnd1", "nodes/GND31"))

    cir["bars"].append(("nodes/V35", "relays/cycleAD-B/in0"))

    cir = build.trace(
        cir, "relays/cycleAD-B/coil0", [("cycAD-B0", [37, 27]),], "nodes/B37",
    )
    cir["bars"].append(("relays/cycleAD-B/ncl", "relays/cycleAD-C/in1"))

    cir = build.trace(
        cir, "relays/cycleAD-C/coil0", [("cycAD-C0", [36, 20]),], "nodes/C36",
    )
    cir["bars"].append(("relays/cycleAD-C/ncl", "nodes/A32"))
    cir["bars"].append(("relays/cycleAD-C/nop", "nodes/D35"))

    # CYCLER B(D, A)
    # --------------
    cir["relays"]["cycleB-D"] = {"pos": [45, 31], "rot": 2}
    cir["relays"]["cycleB-A"] = {"pos": [45, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays/cycleB-A/coil1",
        [("cycBgnd0", [41, 20]), ("cycBgnd1", [41, 27]),],
        "relays/cycleB-D/coil1",
    )
    cir["bars"].append(("nodes/cycBgnd1", "nodes/GND41"))
    cir["bars"].append(("nodes/V45", "relays/cycleB-D/in0"))

    cir = build.trace(
        cir, "relays/cycleB-D/coil0", [("cycB-D0", [47, 27]),], "nodes/D47",
    )
    cir["bars"].append(("relays/cycleB-D/ncl", "relays/cycleB-A/in1"))
    cir = build.trace(
        cir, "relays/cycleB-A/coil0", [("cycB-A0", [46, 20]),], "nodes/A46",
    )
    cir["bars"].append(("relays/cycleB-A/nop", "nodes/B45"))

    # CYCLER C(A, B)
    # --------------
    cir["relays"]["cycleC-A"] = {"pos": [55, 31], "rot": 2}
    cir["relays"]["cycleC-B"] = {"pos": [55, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays/cycleC-B/coil1",
        [("cycCgnd0", [51, 20]), ("cycCgnd1", [51, 27]),],
        "relays/cycleC-A/coil1",
    )
    cir["bars"].append(("nodes/cycCgnd1", "nodes/GND51"))
    cir["bars"].append(("nodes/V55", "relays/cycleC-A/in0"))

    cir = build.trace(
        cir, "relays/cycleC-A/coil0", [("cycC-A0", [57, 27]),], "nodes/A57",
    )
    cir["bars"].append(("relays/cycleC-A/ncl", "relays/cycleC-B/in1"))
    cir = build.trace(
        cir, "relays/cycleC-B/coil0", [("cycC-B0", [56, 20]),], "nodes/B56",
    )
    cir["bars"].append(("relays/cycleC-B/nop", "nodes/C55"))

    # capacitors
    # ==========

    cir["capacitors"]["CAP-A"] = {
        "pos": [13, 1],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-A", "nodes/A13"))

    cir["capacitors"]["CAP-B"] = {
        "pos": [13, 5],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-B", "nodes/B13"))

    cir["capacitors"]["CAP-C"] = {
        "pos": [13, 9],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-C", "nodes/C13"))

    cir["capacitors"]["CAP-D"] = {
        "pos": [13, 13],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-D", "nodes/D13"))

    return cir
