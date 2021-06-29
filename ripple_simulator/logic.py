from . import build


def _add_gate_relays(cir, b=True, c=True):
    if b:
        cir["relays"]["b"] = {"pos": [-1, 0], "rot": 0}
    if c:
        cir["relays"]["c"] = {"pos": [4, 0], "rot": 0}
    return cir


def _add_b_c_inputs(cir, b=True, c=True):
    if b:
        cir["nodes"]["b"] = {"pos": [0, 0]}
        cir["nodes"]["b0"] = {"pos": [0, 4]}
        cir["bars"].append(("relays:b/coil0", "nodes:b0"))
        cir["bars"].append(("nodes:b0", "nodes:b"))
    if c:
        cir["nodes"]["c"] = {"pos": [5, 0]}
        cir["nodes"]["c0"] = {"pos": [5, 4]}
        cir["bars"].append(("relays:c/coil0", "nodes:c0"))
        cir["bars"].append(("nodes:c0", "nodes:c"))
    return cir


def _add_gnd_bar(cir):
    cir["nodes"]["in_GND"] = {"pos": [-2, 3]}
    cir["nodes"]["b_gnd"] = {"pos": [2, 3]}
    cir["nodes"]["c_gnd"] = {"pos": [7, 3]}
    cir["nodes"]["out_GND"] = {"pos": [8, 3]}
    cir["bars"].append(("nodes:in_GND", "nodes:b_gnd"))
    cir["bars"].append(("nodes:b_gnd", "nodes:c_gnd"))
    cir["bars"].append(("nodes:c_gnd", "nodes:out_GND"))

    cir["bars"].append(("nodes:b_gnd", "relays:b/coil1"))
    cir["bars"].append(("nodes:c_gnd", "relays:c/coil1"))
    return cir


def _add_gnd_bar_b(cir):
    cir["nodes"]["in_GND"] = {"pos": [-2, 3]}
    cir["nodes"]["b_gnd"] = {"pos": [2, 3]}
    cir["nodes"]["out_GND"] = {"pos": [3, 3]}
    cir["bars"].append(("nodes:in_GND", "nodes:b_gnd"))
    cir["bars"].append(("nodes:b_gnd", "nodes:out_GND"))

    cir["bars"].append(("nodes:b_gnd", "relays:b/coil1"))
    return cir


def _add_vin_bar_b_c(cir, b_in0=False, b_in1=False, c_in0=False, c_in1=False):
    cir["nodes"]["in_V"] = {"pos": [-2, 1]}

    cir["nodes"]["b0_v"] = {"pos": [-1, 1]}
    cir["nodes"]["b1_v"] = {"pos": [2, 1]}

    cir["nodes"]["c0_v"] = {"pos": [4, 1]}
    cir["nodes"]["c1_v"] = {"pos": [7, 1]}

    cir["nodes"]["out_V"] = {"pos": [8, 1]}

    cir["bars"].append(("nodes:in_V", "nodes:c0_v"))
    cir["bars"].append(("nodes:c0_v", "nodes:c1_v"))
    cir["bars"].append(("nodes:c1_v", "nodes:b0_v"))
    cir["bars"].append(("nodes:b0_v", "nodes:b1_v"))
    cir["bars"].append(("nodes:b1_v", "nodes:out_V"))

    if b_in0:
        cir["bars"].append(("nodes:b0_v", "relays:b/in0"))
    if b_in1:
        cir["bars"].append(("nodes:b1_v", "relays:b/in1"))
    if c_in0:
        cir["bars"].append(("nodes:c0_v", "relays:c/in0"))
    if c_in1:
        cir["bars"].append(("nodes:c1_v", "relays:c/in1"))

    return cir


def _add_vin_bar_b(cir, b_in0=False, b_in1=False):
    cir["nodes"]["in_V"] = {"pos": [-2, 1]}

    cir["nodes"]["b0_v"] = {"pos": [-1, 1]}
    cir["nodes"]["b1_v"] = {"pos": [2, 1]}

    cir["nodes"]["out_V"] = {"pos": [3, 1]}

    cir["bars"].append(("nodes:in_V", "nodes:b0_v"))
    cir["bars"].append(("nodes:b0_v", "nodes:b1_v"))
    cir["bars"].append(("nodes:b1_v", "nodes:out_V"))

    if b_in0:
        cir["bars"].append(("nodes:b0_v", "relays:b/in0"))
    if b_in1:
        cir["bars"].append(("nodes:b1_v", "relays:b/in1"))
    return cir


def _add_out_node(cir):
    cir["nodes"]["out"] = {"pos": [0, 5]}
    return cir


def gate_and(labels=False):
    cir = build.empty_circuit()
    cir = _add_gate_relays(cir=cir)
    cir = _add_b_c_inputs(cir=cir)
    cir = _add_gnd_bar(cir=cir)
    cir = _add_out_node(cir=cir)
    cir = _add_vin_bar_b_c(cir=cir, c_in0=True)

    # inner
    cir["nodes"]["0i"] = {"pos": [3, 5]}
    cir["bars"].append(("relays:c/nop", "nodes:0i"))
    cir["nodes"]["1i"] = {"pos": [3, 0]}
    cir["bars"].append(("nodes:0i", "nodes:1i"))
    cir["bars"].append(("nodes:1i", "relays:b/in1"))

    # out
    cir["bars"].append(("relays:b/nop", "nodes:out"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "AND(B,C)"

    return cir


def gate_or(labels=False):
    cir = build.empty_circuit()
    cir = _add_gate_relays(cir=cir)
    cir = _add_b_c_inputs(cir=cir)
    cir = _add_gnd_bar(cir=cir)
    cir = _add_out_node(cir=cir)
    cir = _add_vin_bar_b_c(cir=cir, b_in0=True, c_in0=True)

    # out
    cir["bars"].append(("relays:b/nop", "nodes:out"))
    cir["nodes"]["out_b"] = {"pos": [1, 5]}
    cir["bars"].append(("nodes:out_b", "nodes:out"))

    cir["nodes"]["out_c"] = {"pos": [3, 5]}
    cir["bars"].append(("relays:c/nop", "nodes:out_c"))

    cir["bars"].append(("nodes:out_b", "nodes:out_c", "wire-y"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "OR(B,C)"

    return cir


def gate_xor(labels=False, vin=True, gnd=True):
    cir = build.empty_circuit()
    cir = _add_gate_relays(cir=cir)
    cir = _add_b_c_inputs(cir=cir)
    cir = _add_out_node(cir=cir)
    if vin:
        cir = _add_vin_bar_b_c(cir=cir, b_in0=True)
    if gnd:
        cir = _add_gnd_bar(cir=cir)
    # inner
    cir["bars"].append(("relays:b/nop", "relays:c/ncl", "wire-y"))
    cir["bars"].append(("relays:b/ncl", "relays:c/nop"))

    # out
    cir["nodes"]["out_0"] = {"pos": [1, 5]}
    cir["bars"].append(("nodes:out", "nodes:out_0"))
    cir["nodes"]["out_1"] = {"pos": [1, 2]}
    cir["bars"].append(("nodes:out_0", "nodes:out_1"))
    cir["nodes"]["out_2"] = {"pos": [3, 2]}
    cir["bars"].append(("nodes:out_1", "nodes:out_2"))
    cir["nodes"]["out_3"] = {"pos": [3, 0]}
    cir["bars"].append(("nodes:out_2", "nodes:out_3"))
    cir["nodes"]["out_3"] = {"pos": [3, 0]}
    cir["bars"].append(("nodes:out_3", "relays:c/in0"))

    if labels:
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "XOR(B,C)"

    return cir


def gate_not(labels=False):
    cir = build.empty_circuit()
    cir = _add_gate_relays(cir, c=False)
    cir = _add_vin_bar_b(cir, b_in0=True)
    cir = _add_b_c_inputs(cir, c=False)
    cir = _add_gnd_bar_b(cir)
    cir = _add_out_node(cir=cir)

    # out
    cir["bars"].append(("relays:b/ncl", "nodes:out"))

    if labels:
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "NOT(B)"

    return cir


def gate_unity(labels=False):
    cir = build.empty_circuit()
    cir = _add_gate_relays(cir, c=False)
    cir = _add_vin_bar_b(cir, b_in0=True)
    cir = _add_b_c_inputs(cir, c=False)
    cir = _add_gnd_bar_b(cir)
    cir = _add_out_node(cir=cir)

    # out
    cir["bars"].append(("relays:b/nop", "nodes:out"))

    if labels:
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["out"]["name"] = "UNITY(B)"

    return cir


def connect_vin_and_gnd_of_gates(cir, gate_name_a, gate_name_b):
    cir["bars"].append(
        ("nodes:" + gate_name_a + "/out_V", "nodes:" + gate_name_b + "/in_V")
    )
    cir["bars"].append(
        (
            "nodes:" + gate_name_a + "/out_GND",
            "nodes:" + gate_name_b + "/in_GND",
        )
    )
    return cir


def half_adder(labels=False):
    cir_and = gate_and()
    cir_and = build.add_group_name(circuit=cir_and, name="AND")
    cir_and = build.translate(circuit=cir_and, pos=[0, 0])

    cir_xor = gate_xor()
    cir_xor = build.add_group_name(circuit=cir_xor, name="XOR")
    cir_xor = build.translate(circuit=cir_xor, pos=[0, 7])

    cir = build.merge_circuits([cir_xor, cir_and])
    # cir = connect_vin_and_gnd_of_gates(cir, "XOR", "AND")

    cir["bars"].append(("nodes:XOR/b", "nodes:AND/b", "wire-y"))
    cir["bars"].append(("nodes:XOR/c", "nodes:AND/c", "wire-y"))

    cir["nodes"]["b"] = {"pos": list(cir["nodes"]["AND/b"]["pos"])}
    cir["bars"].append(("nodes:XOR/b", "nodes:b"))

    cir["nodes"]["c"] = {"pos": list(cir["nodes"]["AND/c"]["pos"])}
    cir["bars"].append(("nodes:XOR/c", "nodes:c"))

    cir["nodes"]["sum"] = {"pos": list(cir["nodes"]["XOR/out"]["pos"])}
    cir["bars"].append(("nodes:XOR/out", "nodes:sum"))

    cir["nodes"]["carry"] = {"pos": [5, 12]}
    cir["nodes"]["carry-0"] = {"pos": [6, 12]}
    cir["nodes"]["carry-1"] = {"pos": [6, 6]}
    cir["nodes"]["carry-2"] = {"pos": [0, 6]}
    cir["bars"].append(("nodes:carry-0", "nodes:carry"))
    cir["bars"].append(("nodes:carry-1", "nodes:carry-0"))
    cir["bars"].append(("nodes:carry-2", "nodes:carry-1"))
    cir["bars"].append(("nodes:AND/out", "nodes:carry-2"))

    if labels:
        cir["nodes"]["b"]["name"] = "B"
        cir["nodes"]["c"]["name"] = "C"
        cir["nodes"]["sum"]["name"] = "SUM(B,C)"
        cir["nodes"]["carry"]["name"] = "CARRY(B,C)"

    return cir


def full_adder(labels=False):

    cir_ha1 = half_adder()
    cir_ha1 = build.add_group_name(circuit=cir_ha1, name="HA1")
    cir_ha1 = build.translate(circuit=cir_ha1, pos=[5, 0])

    cir_ha2 = half_adder()
    cir_ha2 = build.add_group_name(circuit=cir_ha2, name="HA2")
    cir_ha2 = build.translate(circuit=cir_ha2, pos=[0, 14])

    cir_or = gate_or()
    cir_or = build.add_group_name(circuit=cir_or, name="OR")
    cir_or = build.translate(circuit=cir_or, pos=[5, 28])

    cir = build.merge_circuits([cir_ha1, cir_ha2, cir_or])

    # input
    cir["nodes"]["A"] = {"pos": [0, 0]}
    cir["bars"].append(("nodes:A", "nodes:HA2/b"))

    cir["nodes"]["B"] = {"pos": [5, 0]}
    cir["bars"].append(("nodes:B", "nodes:HA1/b"))

    cir["nodes"]["Cin"] = {"pos": [10, 0]}
    cir["bars"].append(("nodes:Cin", "nodes:HA1/c"))

    # output
    cir["nodes"]["Sum"] = {"pos": [0, 33]}
    cir["bars"].append(("nodes:HA2/sum", "nodes:Sum"))

    cir["nodes"]["Cout"] = {"pos": [5, 33]}
    cir["bars"].append(("nodes:OR/out", "nodes:Cout"))

    # inner
    cir["bars"].append(("nodes:HA1/carry", "nodes:OR/c"))
    cir["bars"].append(("nodes:HA1/sum", "nodes:HA2/c"))
    cir["bars"].append(("nodes:HA2/carry", "nodes:OR/b"))

    if labels:
        cir["nodes"]["A"]["name"] = "A"
        cir["nodes"]["B"]["name"] = "B"
        cir["nodes"]["Sum"]["name"] = "Sum"
        cir["nodes"]["Cin"]["name"] = "Cin"
        cir["nodes"]["Cout"]["name"] = "Cout"
    return cir


def ripple_carry_adder(num_bits=3, labels=True):
    dx = 15
    fas = []
    for bit in range(num_bits):
        cfa = full_adder()
        cfa = build.add_group_name(circuit=cfa, name="FA{:02d}".format(bit))
        cfa = build.translate(circuit=cfa, pos=[bit * dx, 0])
        fas.append(cfa)
    cir = build.merge_circuits(fas)

    # V and GND
    for bit in range(num_bits - 1):
        cir = connect_vin_and_gnd_of_gates(
            cir,
            "FA{:02d}/HA1/AND".format(bit),
            "FA{:02d}/HA1/AND".format(bit + 1),
        )
        cir = connect_vin_and_gnd_of_gates(
            cir,
            "FA{:02d}/HA1/XOR".format(bit),
            "FA{:02d}/HA1/XOR".format(bit + 1),
        )

        cir = connect_vin_and_gnd_of_gates(
            cir,
            "FA{:02d}/HA2/AND".format(bit),
            "FA{:02d}/HA2/AND".format(bit + 1),
        )
        cir = connect_vin_and_gnd_of_gates(
            cir,
            "FA{:02d}/HA2/XOR".format(bit),
            "FA{:02d}/HA2/XOR".format(bit + 1),
        )

    # carry
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:FA{:02d}/Cin".format(bit + 1),
                "nodes:FA{:02d}/Cout".format(bit),
            )
        )

    if labels:
        for bit in range(num_bits):
            nn = "{:02d}".format(bit)
            cir["nodes"]["FA" + nn + "/A"]["name"] = "A" + nn
            cir["nodes"]["FA" + nn + "/B"]["name"] = "B" + nn
            cir["nodes"]["FA" + nn + "/Sum"]["name"] = "Sum" + nn

    return cir
