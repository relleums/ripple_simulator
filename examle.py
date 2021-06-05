import ripple_simulator as ris
import os
import subprocess

import numpy as np
import json

name = "clock"

if name == "clock":
    cir_clk = ris.harry_porter_computer.make_clock(periode=167)
    cir_clk = ris.build.add_group_name(circuit=cir_clk, name="CLOCK")
    cir_clk = ris.build.translate(circuit=cir_clk, pos=[0, 0])

    circuit = ris.compile(circuit=cir_clk)
    meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
    seed_mesh_idx = 4

elif name == "register":
    reg = ris.harry_porter_computer.make_register()
    reg_B = ris.build.add_group_name(circuit=reg, name="REGISTER-B")
    reg_B = ris.build.translate(circuit=reg_B, pos=[0, 0])

    circuit = ris.compile(circuit=reg_B)
    meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)

    # initial state
    # -------------
    relays["REGISTER-B_bit_7"]["state"] = 1
    relays["REGISTER-B_bit_5"]["state"] = 1
    relays["REGISTER-B_bit_0"]["state"] = 1
elif name == "gate":
    dx = 12
    cir_and = ris.logic.gate_and(labels=True)
    cir_and = ris.build.add_group_name(circuit=cir_and, name="AND")
    cir_and = ris.build.translate(circuit=cir_and, pos=[5 + 0 * dx, 10])

    cir_or = ris.logic.gate_or(labels=True)
    cir_or = ris.build.add_group_name(circuit=cir_or, name="OR")
    cir_or = ris.build.translate(circuit=cir_or, pos=[5 + 1 * dx, 10])

    cir_xor = ris.logic.gate_xor(labels=True)
    cir_xor = ris.build.add_group_name(circuit=cir_xor, name="XOR")
    cir_xor = ris.build.translate(circuit=cir_xor, pos=[5 + 2 * dx, 10])

    cir_not = ris.logic.gate_not(labels=True)
    cir_not = ris.build.add_group_name(circuit=cir_not, name="NOT")
    cir_not = ris.build.translate(circuit=cir_not, pos=[5 + 3 * dx, 10])

    cir_uni = ris.logic.gate_unity(labels=True)
    cir_uni = ris.build.add_group_name(circuit=cir_uni, name="UNITY")
    cir_uni = ris.build.translate(circuit=cir_uni, pos=[5 + 4 * dx, 10])

    cir = ris.build.merge_circuits(
        [cir_and, cir_or, cir_xor, cir_not, cir_uni]
    )

    cir = ris.logic.connect_vin_and_gnd_of_gates(cir, "AND", "OR")
    cir = ris.logic.connect_vin_and_gnd_of_gates(cir, "OR", "XOR")
    cir = ris.logic.connect_vin_and_gnd_of_gates(cir, "XOR", "NOT")
    cir = ris.logic.connect_vin_and_gnd_of_gates(cir, "NOT", "UNITY")

    cir["nodes"]["V"] = {"pos": [0, 0], "name": "V"}
    cir["bars"].append(("nodes/V", "nodes/AND_in_V", "transparent"))

    circuit = ris.compile(circuit=cir)
    meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
    seed_mesh_idx = 4
elif name == "half_adder":
    """
    cir_ha = ris.logic.half_adder(labels=True)
    cir_ha = ris.build.add_group_name(circuit=cir_ha, name="HA")
    cir_ha = ris.build.translate(circuit=cir_ha, pos=[10, 0])

    cir_fa = ris.logic.full_adder(labels=True)
    cir_fa = ris.build.add_group_name(circuit=cir_fa, name="FA")
    cir_fa = ris.build.translate(circuit=cir_fa, pos=[30, 4])
    """
    cir_rca = ris.logic.ripple_carry_adder(num_bits=4, labels=True)
    cir_rca = ris.build.add_group_name(circuit=cir_rca, name="RCA")
    cir_rca = ris.build.translate(circuit=cir_rca, pos=[1, 1])

    cir = ris.build.merge_circuits([cir_rca])

    circuit = ris.compile(circuit=cir)
    meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
    seed_mesh_idx = 0

steps = []
CLOCK_pegels = []
A_pegels = []
B_pegels = []
C_pegels = []
D_pegels = []

DRAW = True

# run ripple simulation
# ---------------------
for step in range(10):
    relays, capacitors, meshes_on_power = ris.simulate.one_step(
        relays=relays,
        capacitors=capacitors,
        meshes=meshes,
        seed_mesh_idx=seed_mesh_idx,
    )

    circuit_state = ris.compile_circuit_state(
        circuit=circuit,
        relays=relays,
        capacitors=capacitors,
        meshes_on_power=meshes_on_power,
    )

    if DRAW:
        if not os.path.exists("test_{:06d}.jpg".format(step)):
            ris.draw.draw_circuit(
                path="test_{:06d}.svg".format(step),
                circuit=circuit,
                circuit_state=circuit_state,
            )
            subprocess.call(
                [
                    "convert",
                    "test_{:06d}.svg".format(step),
                    "test_{:06d}.jpg".format(step),
                ]
            )
            subprocess.call(["rm", "test_{:06d}.svg".format(step)])

    print(
        step,
        circuit_state["nodes"]["nodes/CLOCK_CLOCK"],
        circuit_state["nodes"]["nodes/CLOCK_A"],
        circuit_state["nodes"]["nodes/CLOCK_B"],
        circuit_state["nodes"]["nodes/CLOCK_C"],
        circuit_state["nodes"]["nodes/CLOCK_D"],
    )
    steps.append(step)

    CLOCK_pegels.append(circuit_state["nodes"]["nodes/CLOCK_CLOCK"])
    A_pegels.append(circuit_state["nodes"]["nodes/CLOCK_A"])
    B_pegels.append(circuit_state["nodes"]["nodes/CLOCK_B"])
    C_pegels.append(circuit_state["nodes"]["nodes/CLOCK_C"])
    D_pegels.append(circuit_state["nodes"]["nodes/CLOCK_D"])

    # clock_pegels.append(circuit_state["nodes"]["nodes/CLOCK_CLK"])

"""
plt.plot(steps, CLOCK_pegels, "k")
plt.plot(steps, np.array(A_pegels) - 2, "red")
plt.plot(steps, np.array(B_pegels) - 4, "blue")
plt.plot(steps, np.array(C_pegels) - 6, "green")
plt.plot(steps, np.array(D_pegels) - 8, "orange")
"""
