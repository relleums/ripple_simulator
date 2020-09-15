import ripple_simulator as ris

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10], "num_steps_before_off": 0},},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
    "labels": {},
}

reg = ris.harry_porter_computer.make_register()
clk = ris.harry_porter_computer.make_clock(periode=5)

circuit = ris.compile(circuit=clk)


meshes, relays = ris.compile_relay_meshes(circuit=circuit)


# initial state
# -------------
"""
relays["clock_20"]["state"] = 1
relays["clock_21"]["state"] = 1

relays["clock_30"]["state"] = 1
relays["clock_31"]["state"] = 1
"""
seed_mesh_idx = 0


# run ripple simulation
# ---------------------
for step in range(300):
    relays, meshes_on_power = ris.simulate.one_step(
        relays=relays, meshes=meshes, seed_mesh_idx=seed_mesh_idx
    )

    circuit_state = ris.compile_circuit_state(
        circuit=circuit, relays=relays, meshes_on_power=meshes_on_power
    )


    ris.draw.draw_circuit(
        path="ripple_simulator/test_{:06d}.svg".format(step),
        circuit=circuit,
        circuit_state=circuit_state,
    )

    print(step, circuit_state["nodes"]["nodes/CLK"])
