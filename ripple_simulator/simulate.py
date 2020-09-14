def find_relay_keys_in_mesh(mesh):
    relay_keys = set()
    for node_key in mesh:
        _, relay_key, terminal_key = node_key.split("/")
        relay_keys.add(relay_key)
    return list(relay_keys)


def update_relay_states(meshes_on_power, relays):
    for relay_key in relays:
        rel = relays[relay_key]
        relay_coil_mesh_idx = rel["coil_mesh"]
        if relay_coil_mesh_idx in meshes_on_power:
            rel["state"] = 1
            rel["num_steps_since_power_off"] = 0
        else:
            if rel["num_steps_since_power_off"] == rel["num_steps_before_off"]:
                rel["state"] = 0
            else:
                rel["num_steps_since_power_off"] += 1
    return relays


def walk_meshes_on_power(meshes_on_power, meshes, seed_mesh_idx, relays):
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
            meshes=meshes,
            seed_mesh_idx=new_mesh,
            relays=relays,
        )


def one_step(relays, meshes, seed_mesh_idx):
    # initial mesh
    meshes_on_power = set()

    walk_meshes_on_power(
        meshes_on_power=meshes_on_power,
        meshes=meshes,
        seed_mesh_idx=seed_mesh_idx,
        relays=relays,
    )

    # next relay states
    relays = update_relay_states(
        meshes_on_power=meshes_on_power, relays=relays
    )

    return relays, list(meshes_on_power)
