from . import build


GATE_V_POS = [0, 11]
GATE_B_POS = [0, 7]
GATE_C_POS = [0, 0]
GATE_OUT_POS = [8, 5]


def gate_and(b=0, c=0, out=0, labels=False):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": [c, 0]}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": [b, 7]}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    cir["nodes"]["n0"] = {"pos": [2, 5]}
    cir["bars"].append(("relays/c/in", "nodes/n0"))

    cir["nodes"]["out"] = {"pos": [8 + out, 5]}
    cir["bars"].append(("nodes/out", "nodes/n0"))

    cir["nodes"]["n2"] = {"pos": [7, 10]}
    cir["bars"].append(("relays/b/out_upper", "nodes/n2"))

    cir["nodes"]["n3"] = {"pos": [7, 3]}
    cir["bars"].append(("nodes/n2", "nodes/n3"))
    cir["bars"].append(("nodes/n3", "relays/c/out_upper"))

    cir["nodes"]["V"] = {"pos": [2, 9], "name": "V"}
    cir["bars"].append(("nodes/V", "relays/b/in"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "AND(B,C)"

    return cir


def gate_or(b=0, c=0, out=0, labels=False):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": [c, 0]}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": [b, 7]}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    cir["nodes"]["n0"] = {"pos": [7, 5]}
    cir["nodes"]["nb"] = {"pos": [7, 10]}
    cir["nodes"]["nc"] = {"pos": [7, 3]}

    cir["nodes"]["out"] = {"pos": [8 + out, 5]}
    cir["bars"].append(("nodes/out", "nodes/n0"))
    cir["bars"].append(("nodes/nb", "nodes/n0"))
    cir["bars"].append(("nodes/nc", "nodes/n0"))

    cir["bars"].append(("relays/b/out_upper", "nodes/nb"))
    cir["bars"].append(("relays/c/out_upper", "nodes/nc"))

    cir["nodes"]["V"] = {"pos": [1, 9], "name": "V"}
    cir["nodes"]["v2"] = {"pos": [1, 2]}
    cir["bars"].append(("nodes/V", "relays/b/in"))
    cir["bars"].append(("nodes/V", "nodes/v2"))
    cir["bars"].append(("nodes/v2", "relays/c/in"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "OR(B,C)"

    return cir


def gate_xor(b=0, c=0, out=0, labels=False):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [2, 7]}
    cir["relays"]["c"] = {"pos": [2, 0]}

    cir["nodes"]["c"] = {"pos": [c, 0]}
    cir["bars"].append(("nodes/c", "relays/c/coil"))

    cir["nodes"]["b"] = {"pos": [b, 7]}
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
    cir["nodes"]["out"] = {"pos": [8 + out, 5]}
    cir["bars"].append(("nodes/out", "nodes/o0"))

    # V
    cir["nodes"]["V"] = {"pos": [2, 9], "name": "V"}
    cir["bars"].append(("nodes/V", "relays/b/in"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "XOR(B,C)"

    return cir


def gate_not(b=0, out=0, labels=False):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [0, 7]}

    cir["nodes"]["b"] = {"pos": [b, 7]}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    # out
    cir["nodes"]["out"] = {"pos": [5 + out, 7]}
    cir["nodes"]["n"] = {"pos": [4 + out, 7]}
    cir["bars"].append(("nodes/n", "relays/b/out_lower"))
    cir["bars"].append(("nodes/n", "nodes/out"))

    # V
    cir["nodes"]["V"] = {"pos": [0, 9], "name": "V"}
    cir["bars"].append(("nodes/V", "relays/b/in"))

    if labels:
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "NOT(B)"

    return cir


def gate_unity(b=0, out=0, labels=False):
    cir = build.empty_circuit()

    cir["relays"]["b"] = {"pos": [0, 7]}

    cir["nodes"]["b"] = {"pos": [b, 7]}
    cir["bars"].append(("nodes/b", "relays/b/coil"))

    # out
    cir["nodes"]["out"] = {"pos": [5 + out, 7]}
    cir["nodes"]["n1"] = {"pos": [5, 7]}
    cir["nodes"]["n0"] = {"pos": [5, 10]}
    cir["bars"].append(("nodes/n0", "relays/b/out_upper"))
    cir["bars"].append(("nodes/n0", "nodes/n1"))
    cir["bars"].append(("nodes/out", "nodes/n1"))

    # V
    cir["nodes"]["V"] = {"pos": [0, 9], "name": "V"}
    cir["bars"].append(("nodes/V", "relays/b/in"))

    if labels:
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "UNITY(B)"

    return cir


def half_adder(sum_bc=0, carry_bc=0, b=0, c=0, labels=False):
    xor_ = gate_xor(b=1)
    xor_ = build.add_group_name(circuit=xor_, name="XOR")
    xor_ = build.translate(circuit=xor_, pos=[2, 14])

    and_ = gate_and(b=1)
    and_ = build.add_group_name(circuit=and_, name="AND")
    and_ = build.translate(circuit=and_, pos=[2, 0])

    cir = build.merge_circuits([xor_, and_])

    cir["bars"].append(("nodes/XOR_b", "nodes/AND_b"))
    cir["bars"].append(("nodes/XOR_c", "nodes/AND_c"))

    if b is not None:
        cir["nodes"]["b"] = {"pos": [0 + b, 7]}
        cir["bars"].append(("nodes/AND_b", "nodes/b"))
        if labels:
            cir["nodes"]["b"]["name"] = "B"

    if c is not None:
        cir["nodes"]["c"] = {"pos": [0 + c, 0]}
        cir["bars"].append(("nodes/AND_c", "nodes/c"))
        if labels:
            cir["nodes"]["c"]["name"] = "C"

    cir["nodes"]["sum"] = {"pos": [10 + sum_bc, 19]}
    cir["bars"].append(("nodes/XOR_out", "nodes/sum"))

    cir["nodes"]["carry"] = {"pos": [10 + carry_bc, 5]}
    cir["bars"].append(("nodes/AND_out", "nodes/carry"))

    if labels:
        cir["nodes"]["sum"]["name"] = "SUM(B,C)"
        cir["nodes"]["carry"]["name"] = "CARRY(B,C)"

    return cir


def full_adder(labels=True):

    ha1 = half_adder(b=None, c=None)
    ha1 = build.add_group_name(circuit=ha1, name="HA1")
    ha1 = build.translate(circuit=ha1, pos=[0, 6])

    ha2 = half_adder(b=None, c=None, sum_bc=1)
    ha2 = build.add_group_name(circuit=ha2, name="HA2")
    ha2 = build.translate(circuit=ha2, pos=[12, 6])

    or_ = gate_or()
    or_ = build.add_group_name(circuit=or_, name="OR")
    or_ = build.translate(circuit=or_, pos=[24, 6])

    cir = build.merge_circuits([ha1, ha2, or_])

    cir["nodes"]["c_in"] = {"pos": [0, 36], "name": "Cin"}
    cir["nodes"]["c_in_0"] = {"pos": [14, 36]}
    cir["bars"].append(("nodes/c_in", "nodes/c_in_0"))
    cir["bars"].append(("nodes/c_in_0", "nodes/HA2_XOR_c"))

    cir["nodes"]["b"] = {"pos": [0, 34], "name": "B"}
    cir["nodes"]["c"] = {"pos": [0, 32], "name": "C"}

    cir["nodes"]["sum_bc"] = {"pos": [0, 2], "name": "SUM(B,C)"}
    cir["nodes"]["sum_bc_0"] = {"pos": [23, 2]}
    cir["bars"].append(("nodes/sum_bc", "nodes/sum_bc_0"))
    cir["bars"].append(("nodes/sum_bc_0", "nodes/HA2_sum"))

    cir["nodes"]["c_out"] = {"pos": [0, 0], "name": "Cout"}
    cir["nodes"]["c_out_0"] = {"pos": [32, 0]}
    cir["bars"].append(("nodes/c_out_0", "nodes/OR_out"))
    cir["bars"].append(("nodes/c_out_0", "nodes/c_out"))

    return cir
