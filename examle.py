import ripple_simulator as ris

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10], "num_steps_before_off": 5},},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
}

reg = ris.harry_porter_computer.make_register()

circuit = ris.compile(circuit=my_circuit)


meshes, relays = ris.compile_relay_meshes(circuit=circuit)

# initial state
# -------------
relays["bit"]["state"] = 0
seed_mesh_idx = 1


# run ripple simulation
# ---------------------
for step in range(10):
    relays, meshes_on_power = ris.simulate.one_step(
        relays=relays, meshes=meshes, seed_mesh_idx=seed_mesh_idx
    )

    circuit_state = ris.compile_circuit_state(
        circuit=circuit,
        relays=relays,
        meshes_on_power=meshes_on_power
    )

    ris.draw.draw_circuit(
        path="test_{:06d}.svg".format(step),
        circuit=circuit,
        circuit_state=circuit_state,
    )
