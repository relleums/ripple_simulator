from . import simulate
from . import draw
from . import harry_porter_computer
from . import build
from . import logic


def copy_and_expand_node_names(nodes):
    out_nodes = {}
    for node_key in nodes:
        out_nodes["nodes" + "/" + node_key] = nodes[node_key]
    return out_nodes


def copy_and_expand_relay_node_names(relays):
    relay_nodes = {}
    for relay_key in relays:
        for relay_terminal_key in draw.RELAY_TERMINALS:
            name = "relays" + "/" + relay_key + "/" + relay_terminal_key
            relay = relays[relay_key]
            terminal = draw.RELAY_TERMINALS[relay_terminal_key]
            pos_x = relay["pos"][0] + terminal["pos"][0]
            pos_y = relay["pos"][1] + terminal["pos"][1]
            relay_nodes[name] = {"pos": [pos_x, pos_y]}
    return relay_nodes


def copy_and_expand_capacitor_names(capacitors):
    out_caps = {}
    for cap_key in capacitors:
        out_caps["capacitors" + "/" + cap_key] = capacitors[cap_key]
    return out_caps


def add_bar_references_to_nodes(nodes, bars):
    for node_key in nodes:
        nodes[node_key]["bars"] = []
    for bar_idx, bar in enumerate(bars):
        start_node_key = bar[0]
        stop_node_key = bar[1]
        nodes[start_node_key]["bars"].append(bar_idx)
        nodes[stop_node_key]["bars"].append(bar_idx)
    return nodes


def find_opposite_node(bar, node_key):
    if bar[0] == node_key:
        return bar[1]
    else:
        return bar[0]


def walk_nodes_of_equal_potential(
    nodes_of_equal_potential, seed_node_key, cpy_nodes
):
    seed_node = cpy_nodes.pop(seed_node_key)
    nodes_of_equal_potential.add(seed_node_key)
    for neighbor_node_key in seed_node["neighbors"]:
        if neighbor_node_key in cpy_nodes:
            walk_nodes_of_equal_potential(
                nodes_of_equal_potential=nodes_of_equal_potential,
                seed_node_key=neighbor_node_key,
                cpy_nodes=cpy_nodes,
            )


def add_direct_neighbor_references_to_nodes(nodes, bars):
    for node_key in nodes:
        neighbors = set()
        for bar_idx in nodes[node_key]["bars"]:
            op_node = find_opposite_node(bar=bars[bar_idx], node_key=node_key)
            neighbors.add(op_node)
        nodes[node_key]["neighbors"] = list(neighbors)
    return nodes


def find_all_meshes_of_equal_potential(nodes):
    cpy_nodes = dict(nodes)

    meshes_of_equal_potential = []
    while len(cpy_nodes) > 0:
        noep = set()
        seed_node_key = list(cpy_nodes.keys())[0]
        walk_nodes_of_equal_potential(
            nodes_of_equal_potential=noep,
            seed_node_key=seed_node_key,
            cpy_nodes=cpy_nodes,
        )
        meshes_of_equal_potential.append(list(noep))

    return meshes_of_equal_potential


def compile(circuit):
    nodes = copy_and_expand_node_names(nodes=circuit["nodes"])
    relay_nodes = copy_and_expand_relay_node_names(relays=circuit["relays"])
    nodes.update(relay_nodes)

    capacitor_nodes = copy_and_expand_capacitor_names(
        capacitors=circuit["capacitors"]
    )
    nodes.update(capacitor_nodes)
    nodes = add_bar_references_to_nodes(nodes=nodes, bars=circuit["bars"])

    nodes = add_direct_neighbor_references_to_nodes(
        nodes=nodes, bars=circuit["bars"]
    )
    meshes_of_equal_potential = find_all_meshes_of_equal_potential(nodes=nodes)

    return {
        "relays": dict(circuit["relays"]),
        "capacitors": dict(circuit["capacitors"]),
        "nodes": nodes,
        "bars": list(circuit["bars"]),
        "meshes_of_equal_potential": meshes_of_equal_potential,
    }


def compile_relay_meshes(circuit):
    meshes = []
    for mesh in circuit["meshes_of_equal_potential"]:
        relay_mesh = []
        for node_key in mesh:
            if "relays" in node_key or "capacitors" in node_key:
                relay_mesh.append(node_key)
        meshes.append(relay_mesh)

    relays = {}
    for relay_key in circuit["relays"]:
        relays[relay_key] = {}
        relays[relay_key]["state"] = simulate.STATE_FULLY_OFF

        in_key = "relays" + "/" + relay_key + "/" + "in"
        outl_key = "relays" + "/" + relay_key + "/" + "out_lower"
        outu_key = "relays" + "/" + relay_key + "/" + "out_upper"
        coil_key = "relays" + "/" + relay_key + "/" + "coil"

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

    capacitors = {}
    for cap_key in circuit["capacitors"]:
        capacitors[cap_key] = {}
        capacitors[cap_key]["state"] = 0
        capacitors[cap_key]["capacity"] = circuit["capacitors"][cap_key][
            "capacity"
        ]

        caps_node_key = "capacitors/" + cap_key
        for meshidx, mesh in enumerate(meshes):
            for node_key in mesh:
                if node_key == caps_node_key:
                    capacitors[cap_key]["mesh"] = meshidx

    return meshes, relays, capacitors


def compile_circuit_state(circuit, relays, capacitors, meshes_on_power):

    circuit_state = {}

    relay_states = {}
    for relay_key in relays:
        relay_states[relay_key] = relays[relay_key]["state"]
    circuit_state["relays"] = relay_states

    node_states = {}
    for mesh_idx, mesh in enumerate(circuit["meshes_of_equal_potential"]):

        if mesh_idx in meshes_on_power:
            mesh_state = 1
        else:
            mesh_state = 0

        for node_key in mesh:
            node_states[node_key] = mesh_state

    bar_state = []
    for bar_idx in range(len(circuit["bars"])):
        bar_state.append(0)
    for node_key in circuit["nodes"]:
        for bar_idx in circuit["nodes"][node_key]["bars"]:
            if node_states[node_key] == 1:
                bar_state[bar_idx] = 1

    capacitors_state = {}
    for cap_key in capacitors:
        capacitors_state[cap_key] = capacitors[cap_key]["state"]

    circuit_state["relays"] = relay_states
    circuit_state["capacitors"] = capacitors_state
    circuit_state["nodes"] = node_states
    circuit_state["bars"] = bar_state
    return circuit_state
