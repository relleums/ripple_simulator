import ripple_simulator as ris
import os
import subprocess

cir_clk = ris.harry_porter_computer.make_clock(periode=33)
cir_clk = ris.build.add_group_name(circuit=cir_clk, name="CLOCK")
cir_clk = ris.build.translate(circuit=cir_clk, pos=[0, 0])

circuit = ris.compile(circuit=cir_clk)
meshes, relays, capacitors = ris.compile_relay_meshes(circuit=circuit)
seed_mesh_idx = 4

steps = []
CLOCK_pegels = []
A_pegels = []
B_pegels = []
C_pegels = []
D_pegels = []

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
            path="clock_{:06d}.svg".format(step),
            circuit=circuit,
            circuit_state=circuit_state,
        )
        subprocess.call(
            [
                "convert",
                "clock_{:06d}.svg".format(step),
                "clock_{:06d}.jpg".format(step),
            ]
        )
        subprocess.call(["rm", "clock_{:06d}.svg".format(step)])

    steps.append(step)

    CLOCK_pegels.append(circuit_state["nodes"]["nodes/CLOCK_CLOCK"])
    A_pegels.append(circuit_state["nodes"]["nodes/CLOCK_A"])
    B_pegels.append(circuit_state["nodes"]["nodes/CLOCK_B"])
    C_pegels.append(circuit_state["nodes"]["nodes/CLOCK_C"])
    D_pegels.append(circuit_state["nodes"]["nodes/CLOCK_D"])

"""
plt.plot(steps, CLOCK_pegels, "k")
plt.plot(steps, np.array(A_pegels) - 2, "red")
plt.plot(steps, np.array(B_pegels) - 4, "blue")
plt.plot(steps, np.array(C_pegels) - 6, "green")
plt.plot(steps, np.array(D_pegels) - 8, "orange")
"""
