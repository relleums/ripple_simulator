from . import draw
from . import harry_porter_computer


def _precompile_circuit(circuit):

    nodes = {}
    for node_key in circuit["nodes"]:
        nodes["node" + "/" + node_key] = circuit["nodes"][node_key]

    for relay_key in circuit["relays"]:
        for relay_terminal_key in draw.RELAY_TERMINALS:
            name = "relay" + "/" + relay_key + "/" + relay_terminal_key
            relay = circuit["relays"][relay_key]
            terminal = draw.RELAY_TERMINALS[relay_terminal_key]
            pos_x = relay["pos"][0] + terminal["pos"][0]
            pos_y = relay["pos"][1] + terminal["pos"][1]
            nodes[name] = {"pos": [pos_x, pos_y]}

    for node_key in nodes:
        nodes[node_key]["bars"] = []
    for bar_idx, bar in enumerate(circuit["bars"]):
        start_node_key = bar[0]
        stop_node_key = bar[1]
        nodes[start_node_key]["bars"].append(bar_idx)
        nodes[stop_node_key]["bars"].append(bar_idx)

    relays = {}
    for relay_key in circuit["relays"]:
        relays[relay_key] = circuit["relays"][relay_key]

    bars = []
    for bar in circuit["bars"]:
        bars.append(bar)

    return {
        "relays": relays,
        "nodes": nodes,
        "bars": bars,
    }


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


def compile(circuit):
    cir = _precompile_circuit(circuit=circuit)

    # find direct neighbor nodes
    # --------------------------
    for node_key in cir["nodes"]:
        neighbors = set()
        for bar_idx in cir["nodes"][node_key]["bars"]:
            op_node = find_opposite_node(
                bar=cir["bars"][bar_idx], node_key=node_key
            )
            neighbors.add(op_node)
        cir["nodes"][node_key]["neighbors"] = list(neighbors)

    # copy input
    # ----------
    cpy_nodes = {}
    for node_key in cir["nodes"]:
        cpy_nodes[node_key] = cir["nodes"][node_key]

    # walk
    # ----
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

    cir["meshes_of_equal_potential"] = meshes_of_equal_potential
    return cir
