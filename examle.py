import ripple_simulator as ris
import os

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10], "rot": 0}},
    "capacitors": {},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
}

reg = ris.harry_porter_computer.make_register()
clk0 = ris.harry_porter_computer.make_clock(periode=25)

clk2 = ris.build.add_group_name(circuit=clk0, name="CLOCK")
clk = ris.build.translate(circuit=clk2, pos=[0, 0])

reg_B = ris.build.add_group_name(circuit=reg, name="REGISTER-B")
reg_B = ris.build.translate(circuit=reg_B, pos=[0, 0])

cir = ris.build.merge_circuits([clk])
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
