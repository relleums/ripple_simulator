from . import build


GATE_V_POS = [0, 11]
GATE_B_POS = [0, 7]
GATE_C_POS = [0, 0]
GATE_OUT_POS = [8, 5]

def gate_and(feed=True):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": list(GATE_C_POS)}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": list(GATE_B_POS)}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    cir["nodes"]["n0"] = {"pos": [2, 5]}
    cir["bars"].append(("relays/c/in", "nodes/n0"))

    cir["nodes"]["AND_bc"] = {"pos": list(GATE_OUT_POS)}
    cir["bars"].append(("nodes/AND_bc", "nodes/n0"))

    cir["nodes"]["n2"] = {"pos": [7, 10]}
    cir["bars"].append(("relays/b/out_upper", "nodes/n2"))

    cir["nodes"]["n3"] = {"pos": [7, 3]}
    cir["bars"].append(("nodes/n2", "nodes/n3"))
    cir["bars"].append(("nodes/n3", "relays/c/out_upper"))

    if feed:
        cir["nodes"]["V"] = {"pos": list(GATE_V_POS)}
        cir["nodes"]["v0"] = {"pos": [1, 11]}
        cir["nodes"]["v1"] = {"pos": [1, 9]}
        cir["bars"].append(("nodes/V", "nodes/v0"))
        cir["bars"].append(("nodes/v0", "nodes/v1"))
        cir["bars"].append(("nodes/v1", "relays/b/in"))

    return cir


def gate_or():
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": list(GATE_C_POS)}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": list(GATE_B_POS)}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    cir["nodes"]["n0"] = {"pos": [7, 5]}
    cir["nodes"]["nb"] = {"pos": [7, 10]}
    cir["nodes"]["nc"] = {"pos": [7, 3]}

    cir["nodes"]["OR_bc"] = {"pos": list(GATE_OUT_POS)}
    cir["bars"].append(("nodes/OR_bc", "nodes/n0"))
    cir["bars"].append(("nodes/nb", "nodes/n0"))
    cir["bars"].append(("nodes/nc", "nodes/n0"))

    cir["bars"].append(("relays/b/out_upper", "nodes/nb"))
    cir["bars"].append(("relays/c/out_upper", "nodes/nc"))

    cir["nodes"]["V"] = {"pos": list(GATE_V_POS)}
    cir["nodes"]["v0"] = {"pos": [1, 11]}
    cir["nodes"]["v1"] = {"pos": [1, 9]}
    cir["nodes"]["v2"] = {"pos": [1, 2]}
    cir["bars"].append(("nodes/V", "nodes/v0"))
    cir["bars"].append(("nodes/v0", "nodes/v1"))
    cir["bars"].append(("nodes/v1", "relays/b/in"))
    cir["bars"].append(("nodes/v1", "nodes/v2"))
    cir["bars"].append(("nodes/v2", "relays/c/in"))

    return cir


def gate_xor(feed=True):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": list(GATE_C_POS)}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": list(GATE_B_POS)}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    # outer bow
    cir["nodes"]["nbu"] = {"pos": [7, 10]}
    cir["bars"].append(("relays/b/out_upper", "nodes/nbu"))
    cir["nodes"]["ncl"] = {"pos": [7, 1]}
    cir["bars"].append(("nodes/nbu", "nodes/ncl"))
    cir["bars"].append(("relays/c/out_lower", "nodes/ncl"))

    # inner bow
    cir["bars"].append(("relays/c/out_upper", "relays/b/out_lower"))

    # out
    cir["nodes"]["o0"] = {"pos": [2, 5]}
    cir["bars"].append(("relays/c/in", "nodes/o0"))
    cir["nodes"]["XOR_bc"] = {"pos": list(GATE_OUT_POS)}
    cir["bars"].append(("nodes/XOR_bc", "nodes/o0"))

    # V
    if feed:
        cir["nodes"]["V"] = {"pos": list(GATE_V_POS)}
        cir["nodes"]["v0"] = {"pos": [1, 11]}
        cir["nodes"]["v1"] = {"pos": [1, 9]}
        cir["bars"].append(("nodes/V", "nodes/v0"))
        cir["bars"].append(("nodes/v0", "nodes/v1"))
        cir["bars"].append(("nodes/v1", "relays/b/in"))

    return cir


def gate_not():
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}

    cir["nodes"]["b"] = {"pos": list(GATE_B_POS)}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    # out
    cir["nodes"]["NOT_b"] = {"pos": list(GATE_OUT_POS)}
    cir["nodes"]["n0"] = {"pos": [6, 5]}
    cir["bars"].append(("nodes/n0", "relays/b/out_lower"))
    cir["bars"].append(("nodes/NOT_b", "nodes/n0"))

    # V
    cir["nodes"]["V"] = {"pos": list(GATE_V_POS)}
    cir["nodes"]["v0"] = {"pos": [1, 11]}
    cir["nodes"]["v1"] = {"pos": [1, 9]}
    cir["bars"].append(("nodes/V", "nodes/v0"))
    cir["bars"].append(("nodes/v0", "nodes/v1"))
    cir["bars"].append(("nodes/v1", "relays/b/in"))

    return cir


def gate_unity():
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}

    cir["nodes"]["b"] = {"pos": list(GATE_B_POS)}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    # out
    cir["nodes"]["UNITY_b"] = {"pos": list(GATE_OUT_POS)}
    cir["nodes"]["n1"] = {"pos": [7, 5]}
    cir["nodes"]["n0"] = {"pos": [7, 10]}
    cir["bars"].append(("nodes/n0", "relays/b/out_upper"))
    cir["bars"].append(("nodes/n0", "nodes/n1"))
    cir["bars"].append(("nodes/UNITY_b", "nodes/n1"))

    # V
    cir["nodes"]["V"] = {"pos": list(GATE_V_POS)}
    cir["nodes"]["v0"] = {"pos": [1, 11]}
    cir["nodes"]["v1"] = {"pos": [1, 9]}
    cir["bars"].append(("nodes/V", "nodes/v0"))
    cir["bars"].append(("nodes/v0", "nodes/v1"))
    cir["bars"].append(("nodes/v1", "relays/b/in"))

    return cir


def half_adder():
    xor_ = gate_xor(feed=False)
    xor_ = build.add_group_name(circuit=xor_, name="XOR")
    xor_ = build.translate(circuit=xor_, pos=[2, 14])

    and_ = gate_and(feed=False)
    and_ = build.add_group_name(circuit=and_, name="AND")
    and_ = build.translate(circuit=and_, pos=[2, 0])

    cir = build.merge_circuits([xor_, and_])

    cir["nodes"]["b"] = {"pos": [0, 0], "name": "B"}
    cir["bars"].append(("nodes/b", "nodes/AND_c"))

    cir["nodes"]["a"] = {"pos": [0, 7], "name": "A"}
    cir["nodes"]["a0"] = {"pos": [1, 7]}
    cir["bars"].append(("nodes/a", "nodes/a0"))
    cir["bars"].append(("nodes/a0", "nodes/AND_b"))

    # V
    cir["nodes"]["v0"] = {"pos": [3, 9]}
    cir["bars"].append(("nodes/v0", "relays/AND_b/in"))

    cir["nodes"]["v1"] = {"pos": [3, 23]}
    cir["bars"].append(("nodes/v1", "relays/XOR_b/in"))
    cir["bars"].append(("nodes/v1", "nodes/v0"))
    cir["nodes"]["v1"] = {"pos": [3, 23]}

    # C
    cir["bars"].append(("nodes/XOR_c", "nodes/AND_c"))

    # B
    cir["nodes"]["v2"] = {"pos": [1, 21]}
    cir["bars"].append(("nodes/v2", "nodes/XOR_b"))
    cir["bars"].append(("nodes/v2", "nodes/a0"))

    return cir
