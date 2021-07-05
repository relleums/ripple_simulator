import ripple_simulator as ris
import os
import subprocess

cir_seqA = ris.harry_porter_computer.make_sequencer(labels_right=False)
cir_seqA = ris.build.add_group_name(circuit=cir_seqA, name="SEQ-A")
cir_seqA = ris.build.translate(circuit=cir_seqA, pos=[0, 0])

cir_seqB = ris.harry_porter_computer.make_sequencer(labels_left=False)
cir_seqB = ris.build.add_group_name(circuit=cir_seqB, name="SEQ-B")
cir_seqB = ris.build.translate(circuit=cir_seqB, pos=[20, 0])

cir = ris.build.merge_circuits([
    cir_seqA,
    cir_seqB
])

circuit = ris.compile(circuit=cir)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
seed_mesh_idx = 4

steps = []

DRAW = True

# run ripple simulation
# ---------------------
for step in range(1):
    print(step)
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
        # if not os.path.exists("clock_{:06d}.jpg".format(step)):
        ris.draw.draw_circuit(
            path="sequencer_{:06d}.jpg".format(step),
            circuit=circuit,
            circuit_state=circuit_state,
        )
    steps.append(step)
