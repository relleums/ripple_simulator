import ripple_simulator as ris
import os
import subprocess

"""
reg_A = ris.harry_porter_computer.make_register(num_bits=8, ADRBUS=False)
reg_A = ris.build.add_group_name(circuit=reg_A, name="REG-A")
reg_A = ris.build.translate(circuit=reg_A, pos=[0, -1])

reg_B = ris.harry_porter_computer.make_register(num_bits=8, ADRBUS=False)
reg_B = ris.build.add_group_name(circuit=reg_B, name="REG-B")
reg_B = ris.build.translate(circuit=reg_B, pos=[0, 14])

reg_C = ris.harry_porter_computer.make_register(num_bits=8, ADRBUS=False)
reg_C = ris.build.add_group_name(circuit=reg_C, name="REG-C")
reg_C = ris.build.translate(circuit=reg_C, pos=[0, 29])

regs = ris.build.merge_circuits([reg_A, reg_B, reg_C])
"""
reg_A = ris.harry_porter_computer.register(num_bits=8, busses=["DAT", "ADR"])
reg_A = ris.build.add_group_name(circuit=reg_A, name="REGISTER-A")
reg_A = ris.build.translate(circuit=reg_A, pos=[4, 0])

reg_B = ris.harry_porter_computer.register(num_bits=8, busses=["DAT", "ADR"])
reg_B = ris.build.add_group_name(circuit=reg_B, name="REGISTER-B")
reg_B = ris.build.translate(circuit=reg_B, pos=[4, 20])

regs = ris.build.merge_circuits([reg_A, reg_B])

seed_mesh_idx = 0
circuit = ris.compile(circuit=regs)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)

# initial state
# -------------
#relays["REG-B_bit-01"]["state"] = 5
#relays["REG-B_bit-02"]["state"] = 5

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
            path="test_{:06d}.jpg".format(step),
            circuit=circuit,
            circuit_state=circuit_state,
        )
