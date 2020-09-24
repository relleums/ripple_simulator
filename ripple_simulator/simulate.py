# 0 1 2 3 4 5 6
# |   |     |   |
NUM_STATES = 7
STATE_FULLY_ON = 6
STATE_ON_GT = 4
STATE_OFF_LT = 2
STATE_FULLY_OFF = 0


def find_relay_keys_in_mesh(mesh):
    relay_keys = set()
    for node_key in mesh:
        if "relays/" in node_key:
            _, relay_key, terminal_key = node_key.split("/")
            relay_keys.add(relay_key)
    return list(relay_keys)


def update_relay_states(meshes_on_power, relays):
    for relay_key in relays:
        rel = relays[relay_key]
        relay_coil_mesh_idx = rel["coil_mesh"]

        if relay_coil_mesh_idx in meshes_on_power:
            rel["state"] += 1
        else:
            rel["state"] -= 1

        if rel["state"] < STATE_FULLY_OFF:
            rel["state"] = STATE_FULLY_OFF

        if rel["state"] > STATE_FULLY_ON:
            rel["state"] = STATE_FULLY_ON

    return relays


def walk_meshes_on_power(meshes_on_power, meshes, seed_mesh_idx, relays):
    meshes_on_power.add(seed_mesh_idx)

    # find all connected meshes through relays
    relay_keys_in_mesh = find_relay_keys_in_mesh(mesh=meshes[seed_mesh_idx])

    connected_meshes = set()
    for relay_key in relay_keys_in_mesh:
        relay = relays[relay_key]

        if relay["in_mesh"] == seed_mesh_idx or relay["in2_mesh"] == seed_mesh_idx:
            if relay["state"] > STATE_ON_GT:
                connected_meshes.add(relay["out_upper_mesh"])
            elif relay["state"] < STATE_OFF_LT:
                connected_meshes.add(relay["out_lower_mesh"])

        elif relay["out_upper_mesh"] == seed_mesh_idx:
            if relay["state"] >= STATE_ON_GT:
                connected_meshes.add(relay["in_mesh"])
                connected_meshes.add(relay["in2_mesh"])

        elif relay["out_lower_mesh"] == seed_mesh_idx:
            if relay["state"] < STATE_OFF_LT:
                connected_meshes.add(relay["in_mesh"])
                connected_meshes.add(relay["in2_mesh"])

    new_meshes_on_power = connected_meshes.difference(meshes_on_power)

    for new_mesh in new_meshes_on_power:
        meshes_on_power.add(new_mesh)
        walk_meshes_on_power(
            meshes_on_power=meshes_on_power,
            meshes=meshes,
            seed_mesh_idx=new_mesh,
            relays=relays,
        )


def one_step(relays, capacitors, meshes, seed_mesh_idx):
    # initial mesh
    meshes_on_power = set()

    walk_meshes_on_power(
        meshes_on_power=meshes_on_power,
        meshes=meshes,
        seed_mesh_idx=seed_mesh_idx,
        relays=relays,
    )

    # find capacitors on or off power
    caps_on_power = []
    caps_off_power = []
    for cap_key in capacitors:
        if capacitors[cap_key]["mesh"] in meshes_on_power:
            caps_on_power.append(cap_key)
        else:
            caps_off_power.append(cap_key)

    # load capacitors when connected to power
    for cap_key in caps_on_power:
        capacitors[cap_key]["state"] = capacitors[cap_key]["capacity"]

    # discharge capacitors when not connected to power
    for cap_key in caps_off_power:
        capacitors[cap_key]["state"] -= 1
        if capacitors[cap_key]["state"] < 0:
            capacitors[cap_key]["state"] = 0

    caps_off_power_but_not_empty = []
    for cap_key in caps_off_power:
        if capacitors[cap_key]["state"] > 0:
            caps_off_power_but_not_empty.append(cap_key)

    # find capacitor meshes for discharge
    capacitor_meshes_on_power = {}
    for cap_key in caps_off_power_but_not_empty:
        capacitor_meshes_on_power[cap_key] = set()
        walk_meshes_on_power(
            meshes_on_power=capacitor_meshes_on_power[cap_key],
            meshes=meshes,
            seed_mesh_idx=capacitors[cap_key]["mesh"],
            relays=relays,
        )

    # add meshes powered by capacitors to meshes_on_power:
    for cap_key in capacitor_meshes_on_power:
        for mesh_idx in capacitor_meshes_on_power[cap_key]:
            meshes_on_power.add(mesh_idx)

    # next relay states
    relays = update_relay_states(
        meshes_on_power=meshes_on_power, relays=relays
    )

    return relays, capacitors, list(meshes_on_power)
