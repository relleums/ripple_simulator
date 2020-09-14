import ripple_simulator as ris

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10], "num_steps_before_off": 0},},
    "nodes": {},
    "bars": [("relays/bit/coil", "relays/bit/in"),],
    "labels": {},
}

clock_delay = 20


relays = {}
nodes = {}
bars = []
labels = {}

RM_Y = 7
RM_X = 7
for i in range(4):
    ii = 4 - i
    key = "R{:d}".format(ii)
    relays[key] = {
        "pos": [RM_X, ii*RM_Y + 3],
        "num_steps_before_off": clock_delay
    }

labels["VCLK"] = {"pos": [0, 36], "name": "VCLK"}
nodes["VCLK"] = {"pos": [0, 36]}
nodes["v_end"] = {"pos": [48, 36]}
bars.append(("nodes/VCLK", "nodes/v_end"))

nodes["v"] = {"pos": [6, 36]}
bars.append(("nodes/v", "nodes/VCLK"))

nodes["v4"] = {"pos": [6, 4*RM_Y + 5]}
bars.append(("nodes/v", "nodes/v4"))
bars.append(("nodes/v4", "relays/R4/in"))

nodes["v3"] = {"pos": [6, 3*RM_Y + 5]}
bars.append(("nodes/v4", "nodes/v3"))
bars.append(("nodes/v3", "relays/R3/in"))

nodes["v2"] = {"pos": [6, 2*RM_Y + 5]}
bars.append(("nodes/v3", "nodes/v2"))
bars.append(("nodes/v2", "relays/R2/in"))

nodes["v1"] = {"pos": [6, 1*RM_Y + 5]}
bars.append(("nodes/v2", "nodes/v1"))
bars.append(("nodes/v1", "relays/R1/in"))



# coil-bus
for i in range(4):
    ii = 4 - i
    nodes["c{:d}_start".format(ii)] = {"pos": [RM_X, ii*RM_Y + 1]}
    nodes["c{:d}_end".format(ii)] = {"pos": [7*RM_X, ii*RM_Y + 1]}
    bars.append(("relays/R{:d}/coil".format(ii), "nodes/c{:d}_start".format(ii)))
    #bars.append(("nodes/c{:d}_start".format(ii), "nodes/c{:d}_end".format(ii)))

# unity-bus
for i in range(4):
    ii = 4 - i
    key = "unity_{:d}_end".format(ii)
    nodes[key] = {"pos": [7*RM_X, ii*RM_Y + 6]}
    #bars.append(("relays/R{:d}/out_upper".format(ii), "nodes/" + key))

# anti-bus
for i in range(4):
    ii = 4 - i
    key = "anti_{:d}_end".format(ii)
    nodes[key] = {"pos": [7*RM_X, ii*RM_Y + 4]}
    #bars.append(("relays/R{:d}/out_lower".format(ii), "nodes/" + key))

# FRZ
labels["FRZ"] = {"pos": [0, 43], "name": "FRZ"}
nodes["FRZ"] = {"pos": [0, 43]}
nodes["f0"] = {"pos": [17, 43]}
nodes["f1"] = {"pos": [24, 43]}
bars.append(("nodes/FRZ", "nodes/f0"))
bars.append(("nodes/f0", "nodes/f1"))

relays["FRZ_33"] = {"pos": [2*RM_X - 1, 5*RM_Y + 3]}
nodes["c3_FRZ_0"] = {"pos": [12, 5*RM_Y + 5]}
nodes["c3_FRZ_1"] = {"pos": [12, 3*RM_Y + 1]}
bars.append(("nodes/c3_FRZ_1", "nodes/c3_FRZ_0"))
bars.append(("nodes/c3_FRZ_0", "relays/FRZ_33/in"))
bars.append(("nodes/c3_start", "nodes/c3_FRZ_1"))

nodes["unity_3_FRZ"] = {"pos": [13, 3*RM_Y + 6]}
bars.append(("relays/FRZ_33/coil", "nodes/unity_3_FRZ"))
bars.append(("relays/R3/out_upper", "nodes/unity_3_FRZ"))

bars.append(("nodes/f0", "relays/FRZ_33/out_upper"))

relays["FRZ_12"] = {"pos": [3*RM_X - 1, 5*RM_Y + 3]}
nodes["c1_FRZ_0"] = {"pos": [19, 5*RM_Y + 5]}
nodes["c1_FRZ_1"] = {"pos": [19, 1*RM_Y + 1]}
bars.append(("nodes/c1_FRZ_1", "nodes/c1_FRZ_0"))
bars.append(("nodes/c1_FRZ_0", "relays/FRZ_12/in"))
bars.append(("nodes/c1_start", "nodes/c1_FRZ_1"))

nodes["unity_1_FRZ"] = {"pos": [20, 1*RM_Y + 6]}
bars.append(("relays/FRZ_12/coil", "nodes/unity_1_FRZ"))
bars.append(("relays/R1/out_upper", "nodes/unity_1_FRZ"))

bars.append(("nodes/f1", "relays/FRZ_12/out_upper"))

# CYCLE 32
relays["CYC32"] = {"pos": [4*RM_X - 1, 0*RM_Y + 3]}
nodes["cyc32_coil"] = {"pos": [4*RM_X - 2, 0*RM_Y + 3]}
bars.append(("relays/CYC32/coil", "nodes/cyc32_coil"))

nodes["cyc32_out_lower"] = {"pos": [4*RM_X + 4, 0*RM_Y + 4]}
bars.append(("relays/CYC32/out_lower", "nodes/cyc32_out_lower"))

nodes["unity_3_cyc32"] = {"pos": [4*RM_X - 2, 3*RM_Y + 6]}
bars.append(("nodes/cyc32_coil", "nodes/unity_3_cyc32"))
bars.append(("nodes/unity_3_FRZ", "nodes/unity_3_cyc32"))

nodes["anti_2_cyc32"] = {"pos": [4*RM_X - 1, 2*RM_Y + 4]}
bars.append(("nodes/anti_2_cyc32", "relays/CYC32/in"))
bars.append(("nodes/anti_2_cyc32", "relays/R2/out_lower"))

# CYCLE 22
relays["CYC22"] = {"pos": [5*RM_X - 1, 0*RM_Y + 3]}
nodes["cyc22_coil"] = {"pos": [5*RM_X - 2, 0*RM_Y + 3]}
bars.append(("relays/CYC22/coil", "nodes/cyc22_coil"))

nodes["cyc22_out_lower"] = {"pos": [5*RM_X + 4, 0*RM_Y + 4]}
bars.append(("relays/CYC22/out_lower", "nodes/cyc22_out_lower"))

nodes["cyc22_coil_CROSS_R2_out_upper"] = {"pos": [5*RM_X - 2, 2*RM_Y + 6]}
bars.append(("nodes/cyc22_coil_CROSS_R2_out_upper", "relays/R2/out_upper"))
bars.append(("nodes/cyc22_coil", "nodes/cyc22_coil_CROSS_R2_out_upper"))
bars.append(("nodes/cyc22_coil_CROSS_R2_out_upper", "nodes/unity_2_end"))

# CYCLE 14
relays["CYC14"] = {"pos": [6*RM_X - 1, 0*RM_Y + 3]}
nodes["cyc14_coil"] = {"pos": [6*RM_X - 2, 0*RM_Y + 3]}
bars.append(("relays/CYC14/coil", "nodes/cyc14_coil"))

nodes["cyc14_out_lower"] = {"pos": [6*RM_X + 4, 0*RM_Y + 4]}
bars.append(("relays/CYC14/out_lower", "nodes/cyc14_out_lower"))


"""
bars.append(("nodes/FRZ", "nodes/f30"))
bars.append(("nodes/f31", "relays/R3_FRZ/out_lower"))

relays["R1_FRZ"] = {"pos": [RM_X * 4 + 1, 20]}
bars.append(("relays/R1_FRZ/in", "relays/R1/coil"))
nodes["f10"] = {"pos": [36, 18]}
bars.append(("nodes/f30", "nodes/f10"))
bars.append(("nodes/f10", "relays/R1_FRZ/out_lower"))

nodes["n30"] = {"pos": [20, 16]}
bars.append(("relays/R3/out_upper", "nodes/n30"))
"""

clk = {}
clk["nodes"] = nodes
clk["relays"] = relays
clk["bars"] = bars
clk["labels"] = labels

reg = ris.harry_porter_computer.make_register()

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
for step in range(1):
    relays, meshes_on_power = ris.simulate.one_step(
        relays=relays, meshes=meshes, seed_mesh_idx=seed_mesh_idx
    )

    circuit_state = ris.compile_circuit_state(
        circuit=circuit, relays=relays, meshes_on_power=meshes_on_power
    )

    ris.draw.draw_circuit(
        path="test_{:06d}.svg".format(step),
        circuit=circuit,
        circuit_state=circuit_state,
    )
