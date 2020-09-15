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

clk = ris.add_group_name(circuit=clk, name="CLOCK")
clk = ris.translate(circuit=clk, pos=[0, 0])
"""
reg_B = ris.add_group_name(circuit=reg, name="REGISTER-B")
reg_B = ris.translate(circuit=reg_B, pos=[0, 0])

cir = ris.merge_circuits([clk, reg_B])
"""
circuit = ris.compile(circuit=clk)

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
for step in range(2000):
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

    """
    ris.draw.draw_circuit(
        path="test_{:06d}.svg".format(step),
        circuit=circuit,
        circuit_state=circuit_state,
    )
    """

    # print(step, circuit_state["relays"]["REGISTER-B_select"])
    print(step, circuit_state["nodes"]["nodes/CLOCK_CLK"])
    steps.append(step)
    clock_pegels.append(circuit_state["nodes"]["nodes/CLOCK_CLK"])


