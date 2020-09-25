import numpy as np
from . import build


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


def make_clock(periode):
    cir = build.empty_circuit()

    cir["nodes"]["VCLK"] = {"pos": [0, 36], "name": "VCLK"}
    cir["nodes"]["v_end"] = {"pos": [6, 36]}
    cir["bars"].append(("nodes/VCLK", "nodes/v_end"))

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

    cir["bars"].append(("relays/R4/in0", "nodes/v_end"))

    # FRZ
    cir["nodes"]["FRZ"] = {"pos": [0, 43], "name": "FRZ"}

    cir["relays"]["FRZ_33"] = {"pos": [15, 3], "rot": 0}
    cir["relays"]["FRZ_12"] = {"pos": [20, 3], "rot": 0}

    # CYCLE 32
    cir["relays"]["CYC32"] = {"pos": [16, 35], "rot": 2}

    # CYCLE 22
    cir["relays"]["CYC22"] = {"pos": [21, 35], "rot": 2}

    # CYCLE 14
    cir["relays"]["CYC14"] = {"pos": [26, 35], "rot": 2}

    # XOR
    cir["relays"]["XOR4"] = {"pos": [33, 20], "rot": 3}
    cir["relays"]["XOR3"] = {"pos": [33, 25], "rot": 3}

    cir["nodes"]["CLK"] = {"pos": [51, 40], "name": "CLK"}

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
        trace=[[10, 24], [26, 24]],
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

    return cir
