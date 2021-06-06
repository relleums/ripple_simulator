import ripple_simulator as ris
import os
import subprocess


reg_B = ris.harry_porter_computer.make_register(num_bits=8)
reg_B = ris.build.add_group_name(circuit=reg_B, name="REG-B")
reg_B = ris.build.translate(circuit=reg_B, pos=[0, 0])

reg_C = ris.harry_porter_computer.make_register(num_bits=8)
reg_C = ris.build.add_group_name(circuit=reg_C, name="REG-C")
reg_C = ris.build.translate(circuit=reg_C, pos=[0, 18])

regs = ris.build.merge_circuits([reg_B, reg_C])

seed_mesh_idx = 0
circuit = ris.compile(circuit=regs)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)

# initial state
# -------------
relays["REG-B_bit-01"]["state"] = 1
relays["REG-B_bit-02"]["state"] = 1
relays["REG-B_bit-00"]["state"] = 1

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
        if not os.path.exists("test_{:06d}.jpg".format(step)):
            ris.draw.draw_circuit(
                path="test_{:06d}.svg".format(step),
                circuit=circuit,
                circuit_state=circuit_state,
            )
            subprocess.call(
                [
                    "convert",
                    "test_{:06d}.svg".format(step),
                    "test_{:06d}.jpg".format(step),
                ]
            )
            subprocess.call(["rm", "test_{:06d}.svg".format(step)])
