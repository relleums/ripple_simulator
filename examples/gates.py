import ripple_simulator as ris
import os
import subprocess


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
        if not os.path.exists("gates_{:06d}.jpg".format(step)):
            ris.draw.draw_circuit(
                path="gates_{:06d}.svg".format(step),
                circuit=circuit,
                circuit_state=circuit_state,
            )
            subprocess.call(
                [
                    "convert",
                    "gates_{:06d}.svg".format(step),
                    "gates_{:06d}.jpg".format(step),
                ]
            )
            subprocess.call(["rm", "gates_{:06d}.svg".format(step)])
