def trace(cir, start_node, trace_nodes, stop_node):
    if len(trace_nodes) == 0:
        cir["bars"].append((start_node, stop_node))
        return cir
    for i in range(len(trace_nodes)):
        cir["nodes"][trace_nodes[i][0]] = {"pos": trace_nodes[i][1]}

    cir["bars"].append((start_node, "nodes/" + trace_nodes[0][0]))
    for i in range(len(trace_nodes) - 1):
        cir["bars"].append(
            ("nodes/" + trace_nodes[i][0], "nodes/" + trace_nodes[i + 1][0],)
        )
    cir["bars"].append(("nodes/" + trace_nodes[-1][0], stop_node))
    return cir


def bar_x(cir, pos, length, name, label=False):
    assert length > 0
    px = pos[0]
    py = pos[1]
    cir["nodes"][name] = {"pos": pos}
    if label:
        cir["nodes"][name]["name"] = name

    for i in range(length):
        posx = px + i + 1
        cir["nodes"][name + "{:02d}".format(posx)] = {"pos": [px + i + 1, py]}

    cir["bars"].append(
        ("nodes/" + name, "nodes/" + name + "{:02d}".format(px + 1))
    )

    for i in range(length - 1):
        posx = px + i + 1
        cir["bars"].append(
            (
                "nodes/" + name + "{:02d}".format(posx),
                "nodes/" + name + "{:02d}".format(posx + 1),
            )
        )

    return cir


def empty_circuit():
    cir = {}
    cir["relays"] = {}
    cir["capacitors"] = {}
    cir["nodes"] = {}
    cir["bars"] = []
    cir["labels"] = {}
    return cir


def translate(circuit, pos=[0, 0]):
    out = {}
    out["bars"] = list(circuit["bars"])

    out["nodes"] = {}
    for node_key in circuit["nodes"]:
        node = dict(circuit["nodes"][node_key])
        node["pos"][0] += pos[0]
        node["pos"][1] += pos[1]
        out["nodes"][node_key] = node

    out["relays"] = {}
    for relay_key in circuit["relays"]:
        relay = dict(circuit["relays"][relay_key])
        relay["pos"][0] += pos[0]
        relay["pos"][1] += pos[1]
        out["relays"][relay_key] = relay

    out["capacitors"] = {}
    for cap_key in circuit["capacitors"]:
        cap = dict(circuit["capacitors"][cap_key])
        cap["pos"][0] += pos[0]
        cap["pos"][1] += pos[1]
        out["capacitors"][cap_key] = cap

    return out


def add_group_name(circuit, name):
    out = {}

    out["relays"] = {}
    for key in circuit["relays"]:
        out_key = name + "_" + key
        out["relays"][out_key] = dict(circuit["relays"][key])

    out["capacitors"] = {}
    for key in circuit["capacitors"]:
        out_key = name + "_" + key
        out["capacitors"][out_key] = dict(circuit["capacitors"][key])

    out["nodes"] = {}
    for key in circuit["nodes"]:
        out_key = name + "_" + key
        out["nodes"][out_key] = dict(circuit["nodes"][key])

    out["bars"] = []
    for bar in circuit["bars"]:
        n0 = bar[0]
        n1 = bar[1]
        _0type = n0.split("/")[0]
        _0path = "/".join(n0.split("/")[1:])
        _0n = _0type + "/" + name + "_" + _0path

        _1type = n1.split("/")[0]
        _1path = "/".join(n1.split("/")[1:])
        _1n = _1type + "/" + name + "_" + _1path

        if len(bar) == 3:
            out["bars"].append((_0n, _1n, bar[2]))
        else:
            out["bars"].append((_0n, _1n))

    return out


def merge_circuits(circuits=[]):
    out = {}
    out["relays"] = {}
    out["capacitors"] = {}
    out["nodes"] = {}
    out["bars"] = []

    for circuit in circuits:

        for key in circuit["relays"]:
            out["relays"][key] = dict(circuit["relays"][key])

        for key in circuit["capacitors"]:
            out["capacitors"][key] = dict(circuit["capacitors"][key])

        for key in circuit["nodes"]:
            out["nodes"][key] = dict(circuit["nodes"][key])

        for bar in circuit["bars"]:
            out["bars"].append(bar)

    return out
