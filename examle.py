import ripple_simulator as ris

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10]},},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
}

reg = ris.harry_porter_computer.make_register()

circuit = ris.compile(circuit=my_circuit)

ris.draw.draw_circuit(path="test.svg", circuit_stage_B=circuit)


meshes, relays = ris.compile_relay_meshes(circuit=circuit)


seed_mesh_idx = 1

for step in range(10):
    relays, meshes_on_power = ris.simulate.one_step(
        relays=relays, meshes=meshes, seed_mesh_idx=seed_mesh_idx
    )
    print(meshes_on_power)