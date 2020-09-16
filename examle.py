import ripple_simulator as ris
import os

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10], "num_steps_before_off": 0},},
    "capacitors": {},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
}

reg = ris.harry_porter_computer.make_register()
clk = ris.harry_porter_computer.make_clock(periode=100)

clk = ris.build.add_group_name(circuit=clk, name="CLOCK")
clk = ris.build.translate(circuit=clk, pos=[72, 20])

"""
reg_B = ris.add_group_name(circuit=reg, name="REGISTER-B")
reg_B = ris.translate(circuit=reg_B, pos=[64, 0])
"""

gate_and = ris.logic.gate_and(labels=True)
gate_and = ris.build.add_group_name(circuit=gate_and, name="AND")
gate_and = ris.build.translate(circuit=gate_and, pos=[40, 0])

gate_or = ris.logic.gate_or(labels=True)
gate_or = ris.build.add_group_name(circuit=gate_or, name="OR")
gate_or = ris.build.translate(circuit=gate_or, pos=[50, 0])

gate_xor = ris.logic.gate_xor(labels=True)
gate_xor = ris.build.add_group_name(circuit=gate_xor, name="XOR")
gate_xor = ris.build.translate(circuit=gate_xor, pos=[60, 0])

gate_not = ris.logic.gate_not(labels=True)
gate_not = ris.build.add_group_name(circuit=gate_not, name="NOT")
gate_not = ris.build.translate(circuit=gate_not, pos=[70, 0])

gate_unity = ris.logic.gate_unity(labels=True)
gate_unity = ris.build.add_group_name(circuit=gate_unity, name="UNITY")
gate_unity = ris.build.translate(circuit=gate_unity, pos=[80, 0])

half_adder = ris.logic.half_adder(labels=True)
half_adder = ris.build.add_group_name(circuit=half_adder, name="HA")
half_adder = ris.build.translate(circuit=half_adder, pos=[70, 20])


full_adder = ris.logic.full_adder(labels=True)
full_adder = ris.build.add_group_name(circuit=full_adder, name="FA")
full_adder = ris.build.translate(circuit=full_adder, pos=[0, 0])

cir = ris.build.merge_circuits([clk, gate_and, gate_or, gate_xor, gate_not, gate_unity, half_adder, full_adder])
cir["nodes"]["V"] = {"pos": [0, 0], "name": "V"}

# connect all Vs
for node_key in cir["nodes"]:
    if node_key.endswith("_V"):
        print(node_key)
        cir["bars"].append(("nodes/V", "nodes/" + node_key, "transparent"))

cir["bars"].append(("nodes/V", "nodes/CLOCK_VCLK", "transparent"))

circuit = ris.compile(circuit=cir)

meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)


# initial state
# -------------
"""
relays["REGISTER-B_bit_7"]["state"] = 1
relays["REGISTER-B_bit_5"]["state"] = 1
relays["REGISTER-B_bit_0"]["state"] = 1
"""

seed_mesh_idx = 0

steps = []
clock_pegels = []

# run ripple simulation
# ---------------------
for step in range(1):
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

    ris.draw.draw_circuit(
        path="test_{:06d}.svg".format(step),
        circuit=circuit,
        circuit_state=circuit_state,
    )

    # print(step, circuit_state["relays"]["REGISTER-B_select"])
    print(step, circuit_state["nodes"]["nodes/CLOCK_CLK"])
    steps.append(step)
    clock_pegels.append(circuit_state["nodes"]["nodes/CLOCK_CLK"])


