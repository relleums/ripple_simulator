def make_register(num_bits=8):
    cir = {}
    cir["relays"] = {}
    cir["nodes"] = {}

    cir["bars"] = []

    x = 8
    y = 2

    for bit in range(num_bits):
        cir["relays"]["bit_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 18]
        }

    for bit in range(num_bits):
        cir["relays"]["enable_{:d}".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 12]
        }

    for bit in range(num_bits):
        cir["nodes"]["hold_{:d}".format(bit)] = {
            "pos": [x + 6 + bit * 6, y + 23]
        }

    for bit in range(num_bits - 1):
        cir["bars"].append(
            ("node/hold_{:d}".format(bit), "node/hold_{:d}".format(bit + 1),)
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "node/hold_{:d}".format(bit),
                "relay/bit_{:d}/out_upper".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relay/bit_{:d}/in".format(bit),
                "relay/bit_{:d}/coil".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relay/bit_{:d}/coil".format(bit),
                "relay/enable_{:d}/in".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["en_{:d}_a".format(bit)] = {
            "pos": [x + 7 + bit * 6, y + 15]
        }

    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relay/enable_{:d}/out_upper".format(bit),
                "node/en_{:d}_a".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}".format(bit)] = {
            "pos": [x + 7 + bit * 6, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            ("node/en_{:d}_a".format(bit), "node/bus_bit_{:d}".format(bit),)
        )
    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}_start".format(bit)] = {
            "pos": [x + 0, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "node/bus_bit_{:d}_start".format(bit),
                "node/bus_bit_{:d}".format(bit),
            )
        )
    for bit in range(num_bits):
        cir["nodes"]["bus_bit_{:d}_end".format(bit)] = {
            "pos": [x + num_bits * 6 + 4, y + bit]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "node/bus_bit_{:d}".format(bit),
                "node/bus_bit_{:d}_end".format(bit),
            )
        )

    for bit in range(num_bits):
        cir["nodes"]["en_{:d}_in".format(bit)] = {
            "pos": [x + 2 + bit * 6, y + 10]
        }
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relay/enable_{:d}/coil".format(bit),
                "node/en_{:d}_in".format(bit),
            )
        )
    for bit in range(num_bits - 1):
        cir["bars"].append(
            ("node/en_{:d}_in".format(bit), "node/en_{:d}_in".format(bit + 1))
        )

    cir["nodes"]["enable"] = {"pos": [x + 1, y + 10]}
    cir["bars"].append(("node/enable", "node/en_0_in"))

    cir["nodes"]["hold"] = {"pos": [x + 1, y + 23]}
    cir["bars"].append(("node/hold", "node/hold_0"))

    return cir
