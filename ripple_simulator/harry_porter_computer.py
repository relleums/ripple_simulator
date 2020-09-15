import numpy as np
from . import build


def make_register(num_bits=8):
    cir = build.empty_circuit()
    x = 16
    y = 0

    cir["nodes"]["v"] = {"pos": [x - 16, y + 23], "name": "V+"}

    for bit in range(num_bits):
        cir["relays"]["bit_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 18]
        }

    for bit in range(num_bits):
        cir["relays"]["enable_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 12]
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
            (
                "nodes/hold_{:d}".format(bit),
                "relays/bit_{:d}/out_upper".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit_{:d}/in".format(bit),
                "relays/bit_{:d}/coil".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit_{:d}/coil".format(bit),
                "relays/enable_{:d}/in".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["en_{:d}_a".format(bit)] = {
            "pos": [x + 7 + bit * 6, y + 15]
        }

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/enable_{:d}/out_upper".format(bit),
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
                "relays/enable_{:d}/coil".format(bit),
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

    cir["relays"]["load_not"] = {"pos": [x - 10, y + 12]}
    cir["relays"]["load"] = {"pos": [x - 10, y + 18]}
    cir["relays"]["select"] = {"pos": [x - 4, y + 12]}

    # load to relay coils
    cir["nodes"]["l0"] = {"pos": [x - 12, y + 18]}
    cir["bars"].append(("nodes/l0", "relays/load/coil"))

    cir["nodes"]["l1"] = {"pos": [x - 12, y + 12]}
    cir["bars"].append(("nodes/l1", "relays/load_not/coil"))

    cir["bars"].append(("nodes/l1", "nodes/l0"))
    cir["bars"].append(("nodes/l0", "nodes/load"))

    # V
    cir["nodes"]["v0"] = {"pos": [x - 10, y + 23]}
    cir["bars"].append(("nodes/v", "nodes/v0"))

    cir["bars"].append(("nodes/v0", "relays/load/in"))
    cir["bars"].append(("relays/load_not/in", "relays/load/in"))

    cir["nodes"]["v1"] = {"pos": [x - 4, y + 23]}
    cir["bars"].append(("nodes/v0", "nodes/v1"))
    cir["bars"].append(("nodes/v1", "relays/select/in"))

    # hold line
    cir["nodes"]["h0"] = {"pos": [x, y + 19]}
    cir["bars"].append(("relays/load/out_lower", "nodes/h0"))
    cir["bars"].append(("nodes/h0", "nodes/hold"))

    # load NOT to select
    cir["nodes"]["nhs"] = {"pos": [x - 6, y + 12]}
    cir["bars"].append(("relays/load_not/out_lower", "nodes/nhs"))
    cir["bars"].append(("relays/select/coil", "nodes/nhs"))

    # select to enable
    cir["bars"].append(("relays/select/out_lower", "nodes/enable"))

    return cir


def make_clock(periode):
    relays = {}
    caps = {}
    nodes = {}
    bars = []

    RM_Y = 7
    RM_X = 7
    for i in range(4):
        ii = 4 - i
        key = "R{:d}".format(ii)
        relays[key] = {"pos": [RM_X, ii * RM_Y + 3]}

        ckey = "C{:d}".format(ii)
        caps[ckey] = {"pos": [RM_X - 4, ii * RM_Y + 3], "capacity": periode}
        bars.append(("capacitors/" + ckey, "relays/" + key + "/coil"))

    nodes["VCLK"] = {"pos": [0, 36], "name": "VCLK"}
    nodes["v_end"] = {"pos": [48, 36]}
    bars.append(("nodes/VCLK", "nodes/v_end"))

    nodes["v"] = {"pos": [6, 36]}
    bars.append(("nodes/v", "nodes/VCLK"))

    nodes["v4"] = {"pos": [6, 4 * RM_Y + 5]}
    bars.append(("nodes/v", "nodes/v4"))
    bars.append(("nodes/v4", "relays/R4/in"))

    nodes["v3"] = {"pos": [6, 3 * RM_Y + 5]}
    bars.append(("nodes/v4", "nodes/v3"))
    bars.append(("nodes/v3", "relays/R3/in"))

    nodes["v2"] = {"pos": [6, 2 * RM_Y + 5]}
    bars.append(("nodes/v3", "nodes/v2"))
    bars.append(("nodes/v2", "relays/R2/in"))

    nodes["v1"] = {"pos": [6, 1 * RM_Y + 5]}
    bars.append(("nodes/v2", "nodes/v1"))
    bars.append(("nodes/v1", "relays/R1/in"))

    # coil-bus
    for i in range(4):
        ii = 4 - i
        BUS_Y = ii * RM_Y + 1
        x_start = 7
        for xx in np.arange(x_start, 49):
            nodes["coil_{:d}_{:d}".format(ii, xx)] = {"pos": [int(xx), BUS_Y]}
            if xx > x_start:
                bars.append(
                    (
                        "nodes/coil_{:d}_{:d}".format(ii, xx - 1),
                        "nodes/coil_{:d}_{:d}".format(ii, xx),
                    )
                )
        bars.append(
            (
                "relays/R{:d}/coil".format(ii),
                "nodes/coil_{:d}_{:d}".format(ii, x_start),
            )
        )

    # unity-bus
    for i in range(4):
        ii = 4 - i
        BUS_Y = ii * RM_Y + 6
        x_start = 11
        for xx in np.arange(x_start, 49):
            nodes["unity_{:d}_{:d}".format(ii, xx)] = {"pos": [int(xx), BUS_Y]}
            if xx > x_start:
                bars.append(
                    (
                        "nodes/unity_{:d}_{:d}".format(ii, xx - 1),
                        "nodes/unity_{:d}_{:d}".format(ii, xx),
                    )
                )
        bars.append(
            (
                "relays/R{:d}/out_upper".format(ii),
                "nodes/unity_{:d}_{:d}".format(ii, x_start),
            )
        )

    # anti-bus
    for i in range(4):
        ii = 4 - i
        BUS_Y = ii * RM_Y + 4
        x_start = 11
        for xx in np.arange(x_start, 49):
            nodes["anti_{:d}_{:d}".format(ii, xx)] = {"pos": [int(xx), BUS_Y]}
            if xx > x_start:
                bars.append(
                    (
                        "nodes/anti_{:d}_{:d}".format(ii, xx - 1),
                        "nodes/anti_{:d}_{:d}".format(ii, xx),
                    )
                )
        bars.append(
            (
                "relays/R{:d}/out_lower".format(ii),
                "nodes/anti_{:d}_{:d}".format(ii, x_start),
            )
        )

    # FRZ
    nodes["FRZ"] = {"pos": [0, 43], "name": "FRZ"}
    nodes["frz0"] = {"pos": [17, 43]}
    nodes["frz1"] = {"pos": [24, 43]}
    bars.append(("nodes/FRZ", "nodes/frz0"))
    bars.append(("nodes/frz0", "nodes/frz1"))

    relays["FRZ_33"] = {"pos": [2 * RM_X - 1, 5 * RM_Y + 3]}
    nodes["FRZ_coil_3"] = {"pos": [12, 5 * RM_Y + 5]}
    bars.append(("nodes/FRZ_coil_3", "relays/FRZ_33/in"))
    bars.append(("nodes/coil_3_12", "nodes/FRZ_coil_3"))
    bars.append(("relays/FRZ_33/coil", "nodes/unity_3_13"))
    bars.append(("nodes/frz0", "relays/FRZ_33/out_upper"))

    relays["FRZ_12"] = {"pos": [3 * RM_X - 1, 5 * RM_Y + 3]}
    nodes["FRZ_coil_1"] = {"pos": [19, 5 * RM_Y + 5]}
    bars.append(("nodes/FRZ_coil_1", "relays/FRZ_12/in"))
    bars.append(("nodes/coil_1_19", "nodes/FRZ_coil_1"))
    bars.append(("relays/FRZ_12/coil", "nodes/unity_1_20"))
    bars.append(("nodes/frz1", "relays/FRZ_12/out_upper"))

    # CYCLE 32
    relays["CYC32"] = {"pos": [4 * RM_X - 1, 0 * RM_Y + 3]}
    nodes["cyc32_coil"] = {"pos": [4 * RM_X - 2, 0 * RM_Y + 3]}
    bars.append(("relays/CYC32/coil", "nodes/cyc32_coil"))
    bars.append(("nodes/cyc32_coil", "nodes/unity_3_26"))

    nodes["cyc32_out_lower"] = {"pos": [4 * RM_X + 4, 0 * RM_Y + 4]}
    bars.append(("relays/CYC32/out_lower", "nodes/cyc32_out_lower"))
    bars.append(("nodes/cyc32_out_lower", "nodes/coil_1_32"))

    bars.append(("relays/CYC32/in", "nodes/anti_2_27"))
    bars.append(("relays/CYC32/out_upper", "nodes/coil_4_31"))

    # CYCLE 22
    relays["CYC22"] = {"pos": [5 * RM_X - 1, 0 * RM_Y + 3]}
    nodes["cyc22_coil"] = {"pos": [5 * RM_X - 2, 0 * RM_Y + 3]}
    bars.append(("relays/CYC22/coil", "nodes/cyc22_coil"))
    bars.append(("nodes/cyc22_coil", "nodes/unity_2_33"))

    nodes["cyc22_out_lower"] = {"pos": [5 * RM_X + 4, 0 * RM_Y + 4]}
    bars.append(("relays/CYC22/out_lower", "nodes/cyc22_out_lower"))

    bars.append(("relays/CYC22/in", "nodes/anti_1_34"))
    bars.append(("relays/CYC22/out_upper", "nodes/coil_3_38"))

    # CYCLE 14
    relays["CYC14"] = {"pos": [6 * RM_X - 1, 0 * RM_Y + 3]}
    nodes["cyc14_coil"] = {"pos": [6 * RM_X - 2, 0 * RM_Y + 3]}
    bars.append(("relays/CYC14/coil", "nodes/cyc14_coil"))
    bars.append(("nodes/cyc14_coil", "nodes/unity_1_40"))

    nodes["cyc14_out_lower"] = {"pos": [6 * RM_X + 4, 0 * RM_Y + 4]}
    bars.append(("relays/CYC14/out_lower", "nodes/cyc14_out_lower"))

    bars.append(("relays/CYC14/out_upper", "nodes/coil_2_45"))
    bars.append(("relays/CYC14/in", "nodes/anti_4_41"))

    # XOR
    relays["XOR4"] = {"pos": [7 * RM_X + 2, 4 * RM_Y + 6]}
    relays["XOR3"] = {"pos": [7 * RM_X + 2, 3 * RM_Y + 6]}
    bars.append(("relays/XOR4/coil", "nodes/unity_4_48"))
    bars.append(("relays/XOR3/coil", "nodes/unity_3_48"))
    bars.append(("relays/XOR3/out_upper", "relays/XOR4/out_lower"))

    nodes["CLK"] = {"pos": [51, 40], "name": "CLK"}

    nodes["vxor0"] = {"pos": [50, 36]}
    nodes["vxor1"] = {"pos": [50, 29]}
    bars.append(("relays/XOR4/in", "nodes/CLK"))
    bars.append(("nodes/v_end", "nodes/vxor0"))
    bars.append(("nodes/vxor0", "nodes/vxor1"))
    bars.append(("relays/XOR3/in", "nodes/vxor1"))
    nodes["xor_3"] = {"pos": [56, 28]}
    nodes["xor_4"] = {"pos": [56, 37]}
    bars.append(("nodes/xor_3", "nodes/xor_4"))
    bars.append(("nodes/xor_3", "relays/XOR3/out_lower"))
    bars.append(("nodes/xor_4", "relays/XOR4/out_upper"))

    clk = {}
    clk["nodes"] = nodes
    clk["relays"] = relays
    clk["bars"] = bars
    clk["capacitors"] = caps

    return clk
