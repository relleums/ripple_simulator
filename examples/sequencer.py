import ripple_simulator as ris
import os
import subprocess

seq = ris.harry_porter_computer.make_sequencer(num_steps=8)
seq = ris.build.add_group_name(circuit=seq, name="SEQUENCER")
seq = ris.build.translate(circuit=seq, pos=[0, 0])

seqs = ris.build.merge_circuits([seq])

seed_mesh_idx = 0
circuit = ris.compile(circuit=seqs)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)

DRAW = True

# run ripple simulation
# ---------------------
for step in range(2):
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
        # if not os.path.exists("test_{:06d}.jpg".format(step)):
        ris.draw.draw_circuit(
            path="seq_{:06d}.svg".format(step),
            circuit=circuit,
            circuit_state=circuit_state,
        )
        subprocess.call(
            [
                "convert",
                "seq_{:06d}.svg".format(step),
                "seq_{:06d}.jpg".format(step),
            ]
        )
        subprocess.call(["rm", "seq_{:06d}.svg".format(step)])
