import ripple_simulator as ris
import os
import subprocess


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
"""
cir = ris.build.merge_circuits([cir_fa])

circuit = ris.compile(circuit=cir)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
seed_mesh_idx = 0

DRAW = True

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

    if DRAW:
        if not os.path.exists("adder_{:06d}.jpg".format(step)):
            ris.draw.draw_circuit(
                path="adder_{:06d}.svg".format(step),
                circuit=circuit,
                circuit_state=circuit_state,
            )
            subprocess.call(
                [
                    "convert",
                    "adder_{:06d}.svg".format(step),
                    "adder_{:06d}.jpg".format(step),
                ]
            )
            subprocess.call(["rm", "adder_{:06d}.svg".format(step)])
