import numpy as np
from . import build


def make_register(num_bits=8):
    cir = build.empty_circuit()
    x = 16
    y = 0

    cir["nodes"]["v"] = {"pos": [x - 16, y + 23], "name": "V+"}

    for bit in range(num_bits):
        cir["relays"]["bit_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 18],
            "rot": 0,
        }

    for bit in range(num_bits):
        cir["relays"]["enable_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 12],
            "rot": 0,
        }

    for bit in range(num_bits):
        cir["nodes"]["hold_{:d}".format(bit)] = {
            "pos": [x + 6 + bit * 6, y + 23]
        }

    for bit in range(num_bits - 1):
        cir["bars"].append(
            ("nodes/hold_{:d}".format(bit), "nodes/hold_{:d}".format(bit + 1),)
        )
    for bit in range(num_bits):
        cir["bars"].append(
            ("nodes/hold_{:d}".format(bit), "relays/bit_{:d}/nop".format(bit),)
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit_{:d}/in0".format(bit),
                "relays/bit_{:d}/coil0".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit_{:d}/coil0".format(bit),
                "relays/enable_{:d}/in0".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["en_{:d}_a".format(bit)] = {
            "pos": [x + 7 + bit * 6, y + 15]
        }

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/enable_{:d}/nop".format(bit),
                "nodes/en_{:d}_a".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}".format(bit)] = {
            "pos": [x + 7 + bit * 6, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            ("nodes/en_{:d}_a".format(bit), "nodes/bus_bit_{:d}".format(bit),)
        )
    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}_start".format(bit)] = {
            "pos": [x + 0, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/bus_bit_{:d}_start".format(bit),
                "nodes/bus_bit_{:d}".format(bit),
            )
        )
    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}_end".format(bit)] = {
            "pos": [x + num_bits * 6 + 4, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/bus_bit_{:d}".format(bit),
                "nodes/bus_bit_{:d}_end".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["en_{:d}_in".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 10]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/enable_{:d}/coil0".format(bit),
                "nodes/en_{:d}_in".format(bit),
            )
        )
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/en_{:d}_in".format(bit),
                "nodes/en_{:d}_in".format(bit + 1),
            )
        )

    cir["nodes"]["enable"] = {"pos": [x + 0, y + 10]}
    cir["bars"].append(("nodes/enable", "nodes/en_0_in"))

    cir["nodes"]["hold"] = {"pos": [x + 0, y + 23]}
    cir["bars"].append(("nodes/hold", "nodes/hold_0"))

    # load select

    cir["nodes"]["load"] = {"pos": [x - 16, y + 18], "name": "LOAD"}
    cir["nodes"]["select"] = {"pos": [x - 16, y + 10], "name": "SEL"}

    cir["bars"].append(("nodes/select", "nodes/enable"))

    cir["relays"]["load_not"] = {"pos": [x - 10, y + 12], "rot": 0}
    cir["relays"]["load"] = {"pos": [x - 10, y + 18], "rot": 0}
    cir["relays"]["select"] = {"pos": [x - 4, y + 12], "rot": 0}

    # load to relay coils
    cir["nodes"]["l0"] = {"pos": [x - 12, y + 18]}
    cir["bars"].append(("nodes/l0", "relays/load/coil0"))

    cir["nodes"]["l1"] = {"pos": [x - 12, y + 12]}
    cir["bars"].append(("nodes/l1", "relays/load_not/coil0"))

    cir["bars"].append(("nodes/l1", "nodes/l0"))
    cir["bars"].append(("nodes/l0", "nodes/load"))

    # V
    cir["nodes"]["v0"] = {"pos": [x - 10, y + 23]}
    cir["bars"].append(("nodes/v", "nodes/v0"))

    cir["bars"].append(("nodes/v0", "relays/load/in0"))
    cir["bars"].append(("relays/load_not/in0", "relays/load/in0"))

    cir["nodes"]["v1"] = {"pos": [x - 4, y + 23]}
    cir["bars"].append(("nodes/v0", "nodes/v1"))
    cir["bars"].append(("nodes/v1", "relays/select/in0"))

    # hold line
    cir["nodes"]["h0"] = {"pos": [x, y + 19]}
    cir["bars"].append(("relays/load/ncl", "nodes/h0"))
    cir["bars"].append(("nodes/h0", "nodes/hold"))

    # load NOT to select
    cir["nodes"]["nhs"] = {"pos": [x - 6, y + 12]}
    cir["bars"].append(("relays/load_not/ncl", "nodes/nhs"))
    cir["bars"].append(("relays/select/coil0", "nodes/nhs"))

    # select to enable
    cir["bars"].append(("relays/select/ncl", "nodes/enable"))

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
        start_node="relays/R4/nop",
        stop_node="relays/CYC32/in0",
        trace=[[15, 28], [15, 35]],
    )

    return cir
