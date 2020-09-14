import ripple_simulator as ris

import numpy as np
import json

my_circuit = {
    "relays": {"bit": {"pos": [10, 10]},},
    "nodes": {},
    "bars": [("relay/bit/coil", "relay/bit/in"),],
}

reg = ris.harry_porter_computer.make_register()

circuit = ris.compile(circuit=my_circuit)

ris.draw.draw_circuit(path="test.svg", circuit_stage_B=circuit)


meshes = []
for mesh in circuit["meshes_of_equal_potential"]:
    relay_mesh = []
    for node_key in mesh:
        if "relay" in node_key:
            relay_mesh.append(node_key)
    meshes.append(relay_mesh)


# All zero
relays = {}
for relay_key in circuit["relays"]:
    relays[relay_key] = {}
    relays[relay_key]["state"] = 0

    in_key = "relay" + "/" + relay_key + "/" + "in"
    outl_key = "relay" + "/" + relay_key + "/" + "out_lower"
    outu_key = "relay" + "/" + relay_key + "/" + "out_upper"
    coil_key = "relay" + "/" + relay_key + "/" + "coil"

    for meshidx, mesh in enumerate(meshes):
        for node_key in mesh:
            if node_key == in_key:
                relays[relay_key]["in_mesh"] = meshidx
            if node_key == outl_key:
                relays[relay_key]["out_lower_mesh"] = meshidx
            if node_key == outu_key:
                relays[relay_key]["out_upper_mesh"] = meshidx
            if node_key == coil_key:
                relays[relay_key]["coil_mesh"] = meshidx


seed_mesh_idx = 1


def find_relay_keys_in_mesh(mesh):
    relay_keys = set()
    for node_key in mesh:
        _, relay_key, terminal_key = node_key.split("/")
        relay_keys.add(relay_key)
    return list(relay_keys)


def update_relay_states(meshes_on_power, relays):
    for relay_key in relays:
        relay_coil_mesh_idx = relays[relay_key]["coil_mesh"]
        if relay_coil_mesh_idx in meshes_on_power:
            relays[relay_key]["state"] = 1
        else:
            relays[relay_key]["state"] = 0
    return relays


def walk_meshes_on_power(meshes_on_power, seed_mesh_idx, relays):
    meshes_on_power.add(seed_mesh_idx)

    # find all connected meshes through relays
    relay_keys_in_mesh = find_relay_keys_in_mesh(mesh=meshes[seed_mesh_idx])

    connected_meshes = set()
    for relay_key in relay_keys_in_mesh:
        relay = relays[relay_key]

        if relay["in_mesh"] == seed_mesh_idx:
            if relay["state"] == 1:
                connected_meshes.add(relay["out_upper_mesh"])
            else:
                connected_meshes.add(relay["out_lower_mesh"])

        elif relay["out_upper_mesh"] == seed_mesh_idx:
            if relay["state"] == 1:
                connected_meshes.add(relay["in_mesh"])

        elif relay["out_lower_mesh"] == seed_mesh_idx:
            if relay["state"] == 0:
                connected_meshes.add(relay["in_mesh"])

    new_meshes_on_power = connected_meshes.difference(meshes_on_power)

    for new_mesh in new_meshes_on_power:
        meshes_on_power.add(new_mesh)
        walk_meshes_on_power(
            meshes_on_power=meshes_on_power,
            seed_mesh_idx=new_mesh,
            relays=relays
        )

def one_step(relays, seed_mesh_idx):
    # initial mesh
    meshes_on_power = set()

    walk_meshes_on_power(
        meshes_on_power=meshes_on_power,
        seed_mesh_idx=seed_mesh_idx,
        relays=relays,
    )

    # next relay states
    relays = update_relay_states(
        meshes_on_power=meshes_on_power, relays=relays
    )

    return relays, list(meshes_on_power)



for step in range(100):
    relays, meshes_on_power = one_step(
        relays=relays,
        seed_mesh_idx=seed_mesh_idx
    )

