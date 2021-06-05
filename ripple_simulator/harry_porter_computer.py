import numpy as np
from . import build
from . import logic


def make_register(num_bits=8):
    cir = build.empty_circuit()

    cir["nodes"]["V"] = {"pos": [63, 36], "name": "V"}

    for bit in range(num_bits):
        cir["relays"]["enable_{:d}".format(bit)] = {
            "pos": [1 + bit * 7, 9],
            "rot": 1,
        }

    # bits GND
    for bit in range(num_bits):
        cir["nodes"]["gnd_bit_{:d}".format(bit)] = {"pos": [5 + bit * 7, 2]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/gnd_bit_{:d}".format(bit),
                "nodes/gnd_bit_{:d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd_bit_{:d}".format(bit),
                "relays/bit_{:d}/coil1".format(bit),
            )
        )

    # bits hold
    for bit in range(num_bits):
        cir["nodes"]["hold_{:d}".format(bit)] = {"pos": [6 + bit * 7, 3]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            ("nodes/hold_{:d}".format(bit), "nodes/hold_{:d}".format(bit + 1))
        )
    for bit in range(num_bits):
        cir["bars"].append(
            ("nodes/hold_{:d}".format(bit), "relays/bit_{:d}/nop".format(bit))
        )

    # bit latch
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit_{:d}/in0".format(bit),
                "relays/bit_{:d}/coil0".format(bit),
            )
        )

    # enable GND
    for bit in range(num_bits):
        cir["nodes"]["gnd_ena_{:d}".format(bit)] = {"pos": [5 + bit * 7, 7]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/gnd_ena_{:d}".format(bit),
                "nodes/gnd_ena_{:d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd_ena_{:d}".format(bit),
                "relays/enable_{:d}/coil1".format(bit),
            )
        )

    # enable enable
    for bit in range(num_bits):
        cir["nodes"]["ena_ena_{:d}".format(bit)] = {"pos": [5 + bit * 7, 8]}
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/ena_ena_{:d}".format(bit),
                "nodes/ena_ena_{:d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/ena_ena_{:d}".format(bit),
                "relays/enable_{:d}/coil0".format(bit),
            )
        )

    # bit to enable
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/enable_{:d}/in1".format(bit),
                "relays/bit_{:d}/in0".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["relays"]["bit_{:d}".format(bit)] = {
            "pos": [1 + bit * 7, 4],
            "rot": 1,
        }

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
    cir = build.add_trace(
        circuit=cir,
        prefix="selr",
        start_node="relays/load_not/coil0",
        stop_node="nodes/load_1",
        trace=[[59, 1],],
    )

    # load-not GNG
    cir = build.add_trace(
        circuit=cir,
        prefix="load_not_gnd",
        start_node="relays/load_not/coil1",
        stop_node="nodes/gnd_bit_{:d}".format(num_bits - 1),
        trace=[[58, 2]],
    )

    # load-not GNG
    cir = build.add_trace(
        circuit=cir,
        prefix="sel_to_enable",
        start_node="relays/load/ncl",
        stop_node="relays/enable_{:d}/coil0".format(num_bits - 1),
        trace=[[54, 14]],
    )

    return cir


def _make_bar_in_x(cir, pos, length, name, label=False):
    assert length > 0
    px = pos[0]
    py = pos[1]
    cir["nodes"][name] = {"pos": pos}
    if label:
        cir["nodes"][name]["name"] = name

    for i in range(length):
        posx = px + i + 1
        cir["nodes"][name + "{:02d}".format(posx)] = {"pos": [px + i + 1, py]}

    cir["bars"].append(("nodes/"+name, "nodes/"+name+"{:02d}".format(px + 1)))

    for i in range(length - 1):
        posx = px + i + 1
        cir["bars"].append((
            "nodes/"+name+"{:02d}".format(posx),
            "nodes/"+name+"{:02d}".format(posx + 1)
        ))

    return cir


def _add_trace(cir, start_node, trace_nodes, stop_node):
    if len(trace_nodes) == 0:
        cir["bars"].append((start_node, stop_node))
        return cir

    for i in range(len(trace_nodes)):
        cir["nodes"][trace_nodes[i][0]] = {"pos": trace_nodes[i][1]}

    cir["bars"].append((start_node, "nodes/"+trace_nodes[0][0]))
    for i in range(len(trace_nodes) - 1):
        cir["bars"].append((
            "nodes/"+trace_nodes[i][0],
            "nodes/"+trace_nodes[i + 1][0],
        ))
    cir["bars"].append(("nodes/"+trace_nodes[-1][0], stop_node))


    return cir


def make_clock_2(periode):
    cir = build.empty_circuit()

    cir = _make_bar_in_x(cir=cir, pos=[1, 1], length=60, name="A", label=True)
    cir = _make_bar_in_x(cir=cir, pos=[1, 5], length=60, name="B", label=True)
    cir = _make_bar_in_x(cir=cir, pos=[1, 9], length=60, name="C", label=True)
    cir = _make_bar_in_x(cir=cir, pos=[1, 13], length=60, name="D", label=True)

    cir = _make_bar_in_x(cir=cir, pos=[1, 36], length=60, name="V", label=True)
    cir = _make_bar_in_x(cir=cir, pos=[1, 38], length=60, name="GND", label=True)

    cir = _make_bar_in_x(cir=cir, pos=[1, 34], length=60, name="CLOCK", label=True)
    cir = _make_bar_in_x(cir=cir, pos=[1, 32], length=6, name="FRZ", label=True)

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

    cir = _make_bar_in_x(cir=cir, pos=[5, 29], length=5, name="latch_GND")
    cir["bars"].append(("nodes/latch_GND", "relays/latch_A/coil1"))
    cir["bars"].append(("nodes/latch_GND10", "relays/latch_C/coil1"))
    cir["bars"].append(("nodes/GND06", "nodes/latch_GND06"))

    # XOR(C, D)
    cir["relays"]["xorc"] = {"pos": [17, 26], "rot": 0}
    cir["relays"]["xord"] = {"pos": [22, 26], "rot": 0}
    cir["bars"].append(("relays/xorc/ncl","relays/xord/nop"))
    cir = _add_trace(
        cir,
        "relays/xorc/nop",
        [
            ("xorbar0", [17, 32]),
            ("xorbar1", [25, 32]),
        ],
        "relays/xord/ncl"
    )
    cir = _add_trace(
        cir,
        "relays/xorc/in0",
        [
            ("xorclock0", [16, 26]),
        ],
        "nodes/CLOCK16"
    )

    cir = _add_trace(
        cir,
        "relays/xord/in1",
        [
            ("xorV", [26, 26]),
        ],
        "nodes/V26"
    )

    cir = _add_trace(
        cir,
        "relays/xorc/coil0",
        [
            ("xorc", [18, 30]),
        ],
        "nodes/C18"
    )
    cir = _add_trace(
        cir,
        "relays/xord/coil0",
        [
            ("xord", [23, 30]),
        ],
        "nodes/D23"
    )
    cir = _add_trace(
        cir,
        "relays/xorc/coil1",
        [
            ("xorgnd0", [20, 29]),
            ("xorgnd1", [21, 29]),
            ("xorgnd2", [25, 29]),
        ],
        "relays/xord/coil1",
    )
    cir = _add_trace(
        cir,
        "nodes/xorgnd1",
        [
        ],
        "nodes/GND21",
    )

    # Cycler
    # ======

    # CYCLER AD(B, C)
    # ---------------
    cir["relays"]["cycleAD-B"] = {"pos": [35, 31], "rot": 2}
    cir["relays"]["cycleAD-C"] = {"pos": [35, 24], "rot": 2}

    cir = _add_trace(
        cir,
        "relays/cycleAD-C/coil1",
        [
            ("cycADgnd0", [31, 20]),
            ("cycADgnd1", [31, 27]),
        ],
        "relays/cycleAD-B/coil1",
    )
    cir["bars"].append(("nodes/cycADgnd1", "nodes/GND31"))

    cir["bars"].append(("nodes/V35", "relays/cycleAD-B/in0"))

    cir = _add_trace(
        cir,
        "relays/cycleAD-B/coil0",
        [
            ("cycAD-B0", [37, 27]),
        ],
        "nodes/B37",
    )
    cir["bars"].append(("relays/cycleAD-B/ncl", "relays/cycleAD-C/in1"))

    cir = _add_trace(
        cir,
        "relays/cycleAD-C/coil0",
        [
            ("cycAD-C0", [36, 20]),
        ],
        "nodes/C36",
    )
    cir["bars"].append(("relays/cycleAD-C/ncl", "nodes/A32"))
    cir["bars"].append(("relays/cycleAD-C/nop", "nodes/D35"))

    # CYCLER B(D, A)
    # --------------
    cir["relays"]["cycleB-D"] = {"pos": [45, 31], "rot": 2}
    cir["relays"]["cycleB-A"] = {"pos": [45, 24], "rot": 2}
    cir = _add_trace(
        cir,
        "relays/cycleB-A/coil1",
        [
            ("cycBgnd0", [41, 20]),
            ("cycBgnd1", [41, 27]),
        ],
        "relays/cycleB-D/coil1",
    )
    cir["bars"].append(("nodes/cycBgnd1", "nodes/GND41"))
    cir["bars"].append(("nodes/V45", "relays/cycleB-D/in0"))

    cir = _add_trace(
        cir,
        "relays/cycleB-D/coil0",
        [
            ("cycB-D0", [47, 27]),
        ],
        "nodes/D47",
    )
    cir["bars"].append(("relays/cycleB-D/ncl", "relays/cycleB-A/in1"))
    cir = _add_trace(
        cir,
        "relays/cycleB-A/coil0",
        [
            ("cycB-A0", [46, 20]),
        ],
        "nodes/A46",
    )
    cir["bars"].append(("relays/cycleB-A/nop", "nodes/B45"))

    # CYCLER C(A, B)
    # --------------
    cir["relays"]["cycleC-A"] = {"pos": [55, 31], "rot": 2}
    cir["relays"]["cycleC-B"] = {"pos": [55, 24], "rot": 2}
    cir = _add_trace(
        cir,
        "relays/cycleC-B/coil1",
        [
            ("cycCgnd0", [51, 20]),
            ("cycCgnd1", [51, 27]),
        ],
        "relays/cycleC-A/coil1",
    )
    cir["bars"].append(("nodes/cycCgnd1", "nodes/GND51"))
    cir["bars"].append(("nodes/V55", "relays/cycleC-A/in0"))

    cir = _add_trace(
        cir,
        "relays/cycleC-A/coil0",
        [
            ("cycC-A0", [57, 27]),
        ],
        "nodes/A57",
    )
    cir["bars"].append(("relays/cycleC-A/ncl", "relays/cycleC-B/in1"))
    cir = _add_trace(
        cir,
        "relays/cycleC-B/coil0",
        [
            ("cycC-B0", [56, 20]),
        ],
        "nodes/B56",
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


def make_clock(periode):
    cir = build.empty_circuit()

    cir["nodes"]["VCLK"] = {"pos": [0, 37], "name": "VCLK"}
    cir["nodes"]["vclk1"] = {"pos": [6, 37]}
    cir["bars"].append(("nodes/VCLK", "nodes/vclk1"))

    DY = 5
    for i in range(4):
        ii = 4 - i
        rkey = "R{:d}".format(ii)
        cir["relays"][rkey] = {"pos": [6, ii * DY + 8], "rot": 1}

        nkey = "n{:d}".format(ii)
        cir["nodes"][nkey] = {"pos": [10, ii * DY + 7]}

        ckey = "C{:d}".format(ii)
        cir["capacitors"][ckey] = {
            "pos": [4, ii * DY + 7],
            "rot": 2,
            "capacity": periode,
        }
        cir["bars"].append(("capacitors/" + ckey, "nodes/" + nkey))
        cir["bars"].append(("nodes/" + nkey, "relays/" + rkey + "/coil0"))

        if ii > 1:
            prev_rkey = "R{:d}".format(ii - 1)
            cir["bars"].append(
                ("relays/" + rkey + "/in1", "relays/" + prev_rkey + "/in0")
            )

        """
        #GND
        nkey0 = "n{:d}_gnd_0".format(ii)
        cir["nodes"][nkey0] = {"pos": [10, ii * DY + 6]}
        cir["bars"].append(("nodes/" + nkey0, "relays/" + rkey + "/coil1"))
        nkey1 = "n{:d}_gnd_1".format(ii)
        cir["nodes"][nkey1] = {"pos": [0, ii * DY + 6]}
        cir["bars"].append(("nodes/" + nkey1, "nodes/" + nkey0))
        """


    cir["bars"].append(("relays/R4/in0", "nodes/vclk1"))

    # CYCLE 32
    cir["relays"]["CYC32"] = {"pos": [16, 35], "rot": 2}

    # CYCLE 22
    cir["relays"]["CYC22"] = {"pos": [21, 35], "rot": 2}

    # CYCLE 14
    cir["relays"]["CYC14"] = {"pos": [26, 35], "rot": 2}

    # pure clock
    # ----------
    cir = build.add_trace(
        circuit=cir,
        prefix="w",
        start_node="relays/R1/ncl",
        stop_node="relays/CYC14/in0",
        trace=[[27, 10], [27, 35]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="wa",
        start_node="relays/R1/coil0",
        stop_node="relays/CYC32/nop",
        trace=[[10, 14], [16, 14],],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="wb",
        start_node="relays/R2/nop",
        stop_node="relays/CYC32/coil0",
        trace=[[15, 18], [15, 31]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w3",
        start_node="relays/R2/coil0",
        stop_node="relays/CYC22/nop",
        trace=[[10, 19], [21, 19]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w4",
        start_node="relays/R3/ncl",
        stop_node="relays/CYC32/in0",
        trace=[[17, 20], [17, 35]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w5",
        start_node="relays/R3/nop",
        stop_node="relays/CYC22/coil0",
        trace=[[20, 23], [20, 31]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w6",
        start_node="relays/R3/coil0",
        stop_node="relays/CYC14/nop",
        trace=[[10, 24], [13, 24], [26, 24]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w7",
        start_node="relays/R4/ncl",
        stop_node="relays/CYC22/in0",
        trace=[[22, 25], [22, 35]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w8",
        start_node="relays/R4/nop",
        stop_node="relays/CYC14/coil0",
        trace=[[25, 28], [25, 31]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w9",
        start_node="relays/R4/coil0",
        stop_node="relays/CYC32/ncl",
        trace=[[10, 29], [13, 29]],
    )

    cir["nodes"]["1high"] = {"pos": [11, 35]}
    cir = build.add_trace(
        circuit=cir,
        prefix="w10",
        start_node="relays/R1/nop",
        stop_node="nodes/1high",
        trace=[[12, 13], [12, 35]],
    )

    # freeze
    # ------
    """
    cir["nodes"]["FRZ"] = {"pos": [0, 3], "name": "FRZ"}
    cir["relays"]["FRZ_33"] = {"pos": [18, 3], "rot": 0}
    cir["relays"]["FRZ_12"] = {"pos": [13, 3], "rot": 0}

    cir = build.add_trace(
        circuit=cir,
        prefix="frz0",
        start_node="nodes/FRZ",
        stop_node="relays/FRZ_33/nop",
        trace=[],
    )
    cir = build.add_trace(
        circuit=cir,
        prefix="frz1",
        start_node="nodes/FRZ",
        stop_node="relays/FRZ_12/nop",
        trace=[],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="frz_4",
        start_node="relays/R1/nop",
        stop_node="relays/FRZ_12/coil0",
        trace=[[14, 7]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="wa2",
        start_node="nodes/wa_001",
        stop_node="relays/FRZ_12/in1",
        trace=[[17, 14], [17, 3]],
    )

    # cir = build.add_trace(
    #     circuit=cir,
    #     prefix="frz2",
    #     start_node="relays/R1/coil0",
    #     stop_node="relays/FRZ_12/in1",
    #     trace=[[17, 3]],
    # )

    cir = build.add_trace(
        circuit=cir,
        prefix="frz3",
        start_node="relays/R3/nop",
        stop_node="relays/FRZ_33/coil0",
        trace=[[19, 7]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="w62",
        start_node="nodes/w6_002",
        stop_node="relays/FRZ_33/in1",
        trace=[],
    )
    """

    # xor clock
    # ---------
    """
    cir["nodes"]["CLK"] = {"pos": [42, 40], "name": "CLK"}

    cir["relays"]["XOR4"] = {"pos": [36, 28], "rot": 3}
    cir["relays"]["XOR3"] = {"pos": [36, 23], "rot": 3}

    cir = build.add_trace(
        circuit=cir,
        prefix="clk_out",
        start_node="nodes/CLK",
        stop_node="relays/XOR4/in1",
        trace=[[42, 31]],
    )

    cir = build.add_trace(
        circuit=cir,
        prefix="xor_vclk",
        start_node="nodes/vclk1",
        stop_node="relays/XOR3/in1",
        trace=[[35, 37], [35, 26]],
    )

    # xor itself
    cir = build.add_trace(
        circuit=cir,
        prefix="xor1",
        start_node="relays/XOR3/nop",
        stop_node="relays/XOR4/ncl",
        trace=[],
    )
    cir = build.add_trace(
        circuit=cir,
        prefix="xor2",
        start_node="relays/XOR3/ncl",
        stop_node="relays/XOR4/nop",
        trace=[],
    )

    # xor inputs
    cir = build.add_trace(
        circuit=cir,
        prefix="xor_in3",
        start_node="relays/XOR3/coil0",
        stop_node="relays/R3/nop",
        trace=[],
    )
    cir = build.add_trace(
        circuit=cir,
        prefix="xor_in4",
        start_node="relays/XOR4/coil0",
        stop_node="relays/R4/nop",
        trace=[],
    )
    """

    return cir
