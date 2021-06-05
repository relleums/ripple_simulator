def add_trace(circuit, prefix, start_node, stop_node, trace=[]):
    num_bars = len(trace) + 1

    last_node = str(start_node)
    for n in range(num_bars - 1):
        node_name = "{:s}_{:03d}".format(prefix, n)
        node_key = "nodes/" + node_name
        circuit["nodes"][node_name] = {"pos": trace[n]}
        circuit["bars"].append((last_node, node_key))
        last_node = str(node_key)

    circuit["bars"].append((last_node, stop_node))
    return circuit


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
