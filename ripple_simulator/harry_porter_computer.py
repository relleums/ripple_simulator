import numpy as np
from . import build
from . import logic


def register(num_bits=4, busses=["Data", "Address"], hold=True):
    cir = build.empty_circuit()
    dx = 7
    Y = 5
    BAR_LENGTH = dx*num_bits-2

    # bit-latch-relays
    for bit in range(num_bits):
        cir["relays"]["BIT-{:02d}".format(bit)] = {
            "pos": [bit * dx, Y + 3],
            "rot": 1,
        }
        # latch
        cir["bars"].append(
            (
                "relays:BIT-{:02d}/in0".format(bit),
                "relays:BIT-{:02d}/coil0".format(bit),
            )
        )
        # to hold
        cir["bars"].append(
            (
                "relays:BIT-{:02d}/nop".format(bit),
                "nodes:HOLD-{:02d}".format(5 + bit*dx),
            )
        )
        # to gnd
        cir["bars"].append(
            (
                "relays:BIT-{:02d}/coil1".format(bit),
                "nodes:GND-BITS-{:02d}".format(4 + bit*dx),
            )
        )

    cir = build.bar_x(
        cir=cir, pos=[0, 6], length=BAR_LENGTH, name="GND-BITS-", label=False)
    cir = build.bar_x(
        cir=cir, pos=[0, 7], length=BAR_LENGTH, name="HOLD-", label=False)

    # bit-indicator-lamps
    for bit in range(num_bits):
        lamp_name = "LED-{:02d}".format(bit)
        cir["nodes"][lamp_name] = {"pos": [2 + bit * dx, 3], "lamp": True}
        cir = build.trace(
            cir,
            "relays:BIT-{:02d}/in1".format(bit),
            [("led-node-{:02d}".format(bit), [0 + bit * dx, 3])],
            "nodes:" + lamp_name,
        )

    dy = 5
    for busidx, buskey in enumerate(busses):
        bus_Y = 5 + Y + busidx*(dy)

        cir = build.bar_x(
            cir=cir, pos=[0, bus_Y + 1],
            length=BAR_LENGTH,
            name="GND-{:s}-".format(buskey),
            label=False
        )

        cir = build.bar_x(
            cir=cir, pos=[0, bus_Y + 2],
            length=BAR_LENGTH,
            name="ENABLE-{:s}-".format(buskey),
            label=False
        )

        # bus-enable-relays
        for bit in range(num_bits):
            cir["relays"]["{:s}-{:02d}".format(buskey, bit)] = {
                "pos": [bit * dx, bus_Y + 3],
                "rot": 1,
            }
            # to gnd
            cir["bars"].append(
                (
                    "relays:{:s}-{:02d}/coil1".format(buskey, bit),
                    "nodes:GND-{:s}-{:02d}".format(buskey, 4 + bit*dx),
                )
            )
            # to enable
            cir["bars"].append(
                (
                    "relays:{:s}-{:02d}/coil0".format(buskey, bit),
                    "nodes:ENABLE-{:s}-{:02d}".format(buskey, 4 + bit*dx),
                )
            )
            # to bit
            if busidx == 0:
                cir["bars"].append(
                    (
                        "relays:{:s}-{:02d}/in1".format(buskey, bit),
                        "relays:BIT-{:02d}/in0".format(bit),
                    )
                )
            else:
                lower_buskey = busses[busidx - 1]
                cir["bars"].append(
                    (
                        "relays:{:s}-{:02d}/in1".format(buskey, bit),
                        "relays:{:s}-{:02d}/in0".format(lower_buskey, bit),
                    )
                )
            busbitnodename = "{:s}-{:02d}".format(buskey, bit)
            cir["nodes"][busbitnodename] = {
                "pos": [bit * dx + 5, bus_Y + 4],
                #"name": busbitnodename,
                "pin": True,
            }
            cir["nodes"][busbitnodename+"-1"] = {
                "pos": [bit * dx + 4, bus_Y + 4],
                "pin": True,
            }
            cir["nodes"][busbitnodename+"-2"] = {
                "pos": [bit * dx + 3, bus_Y + 4],
                "pin": True,
            }

            cir["bars"].append(
                (
                    "nodes:" + busbitnodename,
                    "relays:{:s}-{:02d}/nop".format(buskey, bit),
                )
            )
            cir["bars"].append(
                (
                    "nodes:" + busbitnodename,
                    "nodes:" + busbitnodename+"-1",
                )
            )
            cir["bars"].append(
                (
                    "nodes:" + busbitnodename+"-1",
                    "nodes:" + busbitnodename+"-2",
                )
            )

    if hold:
        cir["relays"]["HOLD"] = {
            "pos": [(-1) * dx, Y + 3],
            "rot": 1,
        }
        # hold line
        cir["nodes"]["hold-hold"] = {"pos": [(-1) * dx + 0, Y + 2],}
        cir["bars"].append(("relays:HOLD/in0", "nodes:hold-hold"))
        cir["bars"].append(("nodes:hold-hold", "nodes:HOLD-"))

        # gnd
        cir["nodes"]["hold-gnd"] = {"pos": [(-1) * dx + 4, Y + 1],}
        cir["bars"].append(("relays:HOLD/coil1", "nodes:hold-gnd"))
        cir["bars"].append(("nodes:hold-gnd", "nodes:GND-BITS-"))


    return cir



def make_register(num_bits=4, ADRBUS=True):
    cir = build.empty_circuit()

    ox = 7

    cir["nodes"]["V"] = {"pos": [0, 3], "name": "V"}
    cir["nodes"]["GND"] = {"pos": [0, 2], "name": "GND"}

    cir["nodes"]["SELECT"] = {"pos": [0, 13], "name": "SELECT"}
    cir["nodes"]["LOAD"] = {"pos": [0, 8], "name": "LOAD"}

    # bit relays
    for bit in range(num_bits):
        cir["relays"]["bit-{:02d}".format(bit)] = {
            "pos": [ox + 1 + bit * 7, 9],
            "rot": 1,
        }

    # enable relays
    for bit in range(num_bits):
        cir["relays"]["ena-dat-{:02d}".format(bit)] = {
            "pos": [ox + 1 + bit * 7, 14],
            "rot": 1,
        }

    # bits GND
    for bit in range(num_bits):
        cir["nodes"]["gnd-bit-{:02d}".format(bit)] = {
            "pos": [ox + 5 + bit * 7, 7]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:gnd-bit-{:02d}".format(bit),
                "nodes:gnd-bit-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes:gnd-bit-{:02d}".format(bit),
                "relays:bit-{:02d}/coil1".format(bit),
            )
        )

    # bits hold
    for bit in range(num_bits):
        cir["nodes"]["hold-{:02d}".format(bit)] = {
            "pos": [ox + 6 + bit * 7, 8]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:hold-{:02d}".format(bit),
                "nodes:hold-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes:hold-{:02d}".format(bit),
                "relays:bit-{:02d}/nop".format(bit),
            )
        )

    # bit latch
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays:bit-{:02d}/in0".format(bit),
                "relays:bit-{:02d}/coil0".format(bit),
            )
        )

    # enable GND
    for bit in range(num_bits):
        cir["nodes"]["gnd-ena-{:02d}".format(bit)] = {
            "pos": [ox + 5 + bit * 7, 12]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:gnd-ena-{:02d}".format(bit),
                "nodes:gnd-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes:gnd-ena-{:02d}".format(bit),
                "relays:ena-dat-{:02d}/coil1".format(bit),
            )
        )

    # enable enable
    for bit in range(num_bits):
        cir["nodes"]["ena-ena-{:02d}".format(bit)] = {
            "pos": [ox + 5 + bit * 7, 13]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:ena-ena-{:02d}".format(bit),
                "nodes:ena-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes:ena-ena-{:02d}".format(bit),
                "relays:ena-dat-{:02d}/coil0".format(bit),
            )
        )

    # bit to enable
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays:ena-dat-{:02d}/in1".format(bit),
                "relays:bit-{:02d}/in0".format(bit),
            )
        )

    # enable to bus
    for bit in range(num_bits):
        node_name = "BUS{:02d}".format(bit)
        cir["nodes"][node_name] = {
            "pos": [ox + 6 + bit * 7, 15],
            "name": node_name,
        }
        cir["bars"].append(
            ("relays:ena-dat-{:02d}/nop".format(bit), "nodes:" + node_name,)
        )

    # indicator lamps
    for bit in range(num_bits):
        lamp_name = "LAMP{:02d}".format(bit)
        lamp_con_node = "lam-{:02d}".format(bit)
        cir["nodes"][lamp_name] = {"pos": [ox + 4 + bit * 7, 3], "lamp": True}
        cir["nodes"][lamp_con_node] = {"pos": [ox + 1 + bit * 7, 3]}

        cir["bars"].append(
            ("relays:bit-{:02d}/in1".format(bit), "nodes:" + lamp_con_node,)
        )
        cir["bars"].append(("nodes:" + lamp_con_node, "nodes:" + lamp_name))

    # lamp gnd
    for bit in range(num_bits):
        cir["nodes"]["gnd-lmp-{:02d}".format(bit)] = {
            "pos": [ox + 5 + bit * 7, 2]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes:gnd-lmp-{:02d}".format(bit),
                "nodes:gnd-lmp-{:02d}".format(bit + 1),
            )
        )

    cir["nodes"]["HOLD"] = {"pos": [ox, 8], "name": "HOLD"}
    cir["bars"].append(("nodes:HOLD", "nodes:hold-00"))

    cir["nodes"]["ENABLE"] = {"pos": [ox, 13], "name": "ENABLE"}
    cir["bars"].append(("nodes:ENABLE", "nodes:ena-ena-00"))

    cir["relays"]["LOAD-NOT-HOLD"] = {"pos": [1, 4], "rot": 1}
    cir["relays"]["LOAD-NOT-SELECT"] = {"pos": [1, 9], "rot": 1}
    cir["relays"]["LOAD-NOT-SELECT-2"] = {"pos": [1, 14], "rot": 1}

    # V
    cir = build.trace(
        cir, "nodes:V", [("vv0", [1, 3])], "relays:LOAD-NOT-HOLD/in0"
    )
    cir["bars"].append(
        ("relays:LOAD-NOT-HOLD/in0", "relays:LOAD-NOT-SELECT/in1")
    )
    cir["bars"].append(
        ("relays:LOAD-NOT-SELECT/in0", "relays:LOAD-NOT-SELECT-2/in1")
    )

    # GND
    cir["nodes"]["gnd-2-2"] = {"pos": [2, 2]}
    cir["bars"].append(("nodes:GND", "nodes:gnd-2-2"))

    cir["nodes"]["gnd-2-1"] = {"pos": [2, 1]}
    cir["bars"].append(("nodes:gnd-2-2", "nodes:gnd-2-1"))
    cir["bars"].append(("relays:LOAD-NOT-HOLD/coil1", "nodes:gnd-2-1"))

    cir["nodes"]["gnd-2-6"] = {"pos": [2, 6]}
    cir["bars"].append(("nodes:gnd-2-2", "nodes:gnd-2-6"))
    cir["bars"].append(("relays:LOAD-NOT-SELECT/coil1", "nodes:gnd-2-6"))

    # GND to bits
    cir["nodes"]["gnd-2-7"] = {"pos": [2, 7]}
    cir["bars"].append(("nodes:gnd-2-6", "nodes:gnd-2-7"))
    cir["bars"].append(("nodes:gnd-bit-00", "nodes:gnd-2-7"))

    cir["nodes"]["gnd-2-11"] = {"pos": [2, 11]}
    cir["bars"].append(("nodes:gnd-2-7", "nodes:gnd-2-11"))
    cir["bars"].append(("relays:LOAD-NOT-SELECT-2/coil1", "nodes:gnd-2-11"))

    # GND to enable
    cir["nodes"]["gnd-2-12"] = {"pos": [2, 12]}
    cir["bars"].append(("nodes:gnd-2-11", "nodes:gnd-2-12"))
    cir["bars"].append(("nodes:gnd-ena-00", "nodes:gnd-2-12"))

    # GND lamps
    cir["bars"].append(("nodes:gnd-2-2", "nodes:gnd-lmp-00"))

    # LOAD
    cir["nodes"]["load-4-8"] = {"pos": [4, 8]}
    cir["bars"].append(("nodes:LOAD", "nodes:load-4-8"))
    cir = build.trace(
        cir,
        "relays:LOAD-NOT-SELECT/coil0",
        [("nn0", [4, 9])],
        "nodes:load-4-8",
    )
    cir = build.trace(
        cir, "relays:LOAD-NOT-HOLD/coil0", [["nn1", [4, 4]]], "nodes:load-4-8"
    )
    cir = build.trace(
        cir, "relays:LOAD-NOT-HOLD/ncl", [("hh0", [7, 1])], "nodes:HOLD"
    )

    # SELECT

    cir["bars"].append(("nodes:SELECT", "nodes:ENABLE"))
    cir = build.trace(
        cir,
        "nodes:ENABLE",
        [("en-7-11", [7, 11])],
        "relays:LOAD-NOT-SELECT-2/ncl",
    )

    cir = build.trace(
        cir,
        "relays:LOAD-NOT-SELECT/ncl",
        [("sl-00", [6, 5]), ("sl-01", [3, 5]), ("sl-02", [3, 14]),],
        "relays:LOAD-NOT-SELECT-2/coil0",
    )

    if ADRBUS:
        for bit in range(num_bits):
            cir["relays"]["ena-adr-{:02d}".format(bit)] = {
                "pos": [ox + 1 + bit * 7, 19],
                "rot": 1,
            }

        # enable GND
        for bit in range(num_bits):
            cir["nodes"]["gnd-ena-adr-{:02d}".format(bit)] = {
                "pos": [ox + 5 + bit * 7, 17]
            }
        for bit in range(num_bits - 1):
            cir["bars"].append(
                (
                    "nodes:gnd-ena-adr-{:02d}".format(bit),
                    "nodes:gnd-ena-adr-{:02d}".format(bit + 1),
                )
            )
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "nodes:gnd-ena-adr-{:02d}".format(bit),
                    "relays:ena-adr-{:02d}/coil1".format(bit),
                )
            )

        # enable ena-adr
        for bit in range(num_bits):
            cir["nodes"]["ena-ena-adr-{:02d}".format(bit)] = {
                "pos": [ox + 5 + bit * 7, 18]
            }
        for bit in range(num_bits - 1):
            cir["bars"].append(
                (
                    "nodes:ena-ena-adr-{:02d}".format(bit),
                    "nodes:ena-ena-adr-{:02d}".format(bit + 1),
                )
            )
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "nodes:ena-ena-adr-{:02d}".format(bit),
                    "relays:ena-adr-{:02d}/coil0".format(bit),
                )
            )

        # bit to ena-adr
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "relays:ena-adr-{:02d}/in1".format(bit),
                    "relays:ena-dat-{:02d}/in0".format(bit),
                )
            )

        # ena-adr to bus
        for bit in range(num_bits):
            node_name = "ADR{:02d}".format(bit)
            cir["nodes"][node_name] = {
                "pos": [ox + 6 + bit * 7, 20],
                "name": node_name,
            }
            cir["bars"].append(
                (
                    "relays:ena-adr-{:02d}/nop".format(bit),
                    "nodes:" + node_name,
                )
            )

    return cir


def make_clock(periode):
    cir = build.empty_circuit()

    cir = build.bar_x(cir=cir, pos=[1, 4], length=33, name="A", label=True)
    cir = build.bar_x(
        cir=cir, pos=[5, 5], length=16, name="A-GND", label=False
    )

    cir = build.bar_x(cir=cir, pos=[5, 7], length=31, name="B", label=True)
    cir = build.bar_x(
        cir=cir, pos=[5, 8], length=16, name="B-GND", label=False
    )

    cir = build.bar_x(cir=cir, pos=[5, 10], length=30, name="C", label=True)
    cir = build.bar_x(
        cir=cir, pos=[5, 11], length=16, name="C-GND", label=False
    )

    cir = build.bar_x(cir=cir, pos=[5, 13], length=24, name="D", label=True)
    cir = build.bar_x(
        cir=cir, pos=[5, 14], length=16, name="D-GND", label=False
    )

    cir = build.bar_x(cir=cir, pos=[1, 30], length=35, name="V", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 28], length=35, name="GND", label=True)

    cir = build.bar_x(
        cir=cir, pos=[1, 17], length=11, name="CLOCK", label=True
    )
    cir = build.bar_x(cir=cir, pos=[1, 26], length=3, name="FRZ", label=True)

    # Freeze
    # ======

    cir["relays"]["frz1"] = {
        "pos": [5, 31],
        "rot": 2,
        "comment": "Prevent backdriving thr FRZ-line",
    }
    cir = build.trace(
        cir, "relays:frz1/coil0", [("frz1-coil0", [4, 27])], "nodes:FRZ04",
    )
    cir = build.trace(
        cir, "relays:frz1/coil1", [("frz1-gnd", [3, 27])], "nodes:GND03",
    )
    cir = build.trace(cir, "relays:frz1/in0", [], "nodes:V05",)

    cir = build.bar_x(cir=cir, pos=[2, 25], length=5, name="latch_BAR")
    cir["bars"].append(("relays:latch_A/nop", "nodes:latch_BAR"))
    cir["bars"].append(("relays:latch_C/nop", "nodes:latch_BAR07"))
    cir["bars"].append(("relays:frz1/nop", "nodes:latch_BAR05"))

    # latch A
    cir["relays"]["latch_A"] = {"pos": [2, 19], "rot": 0}
    # cir["bars"].append(("relays:latch_A/nop", "nodes:FRZ02"))
    cir["bars"].append(("relays:latch_A/coil0", "relays:latch_A/in0"))
    cir["bars"].append(("nodes:A02", "relays:latch_A/in0"))

    # latch C
    cir["relays"]["latch_C"] = {"pos": [7, 19], "rot": 0}
    # cir["bars"].append(("relays:latch_C/nop", "nodes:FRZ07"))
    cir["bars"].append(("relays:latch_C/coil0", "relays:latch_C/in0"))
    cir["bars"].append(("nodes:C07", "relays:latch_C/in0"))

    cir = build.bar_x(cir=cir, pos=[5, 22], length=5, name="latch_GND")
    cir["bars"].append(("nodes:latch_GND", "relays:latch_A/coil1"))
    cir["bars"].append(("nodes:latch_GND10", "relays:latch_C/coil1"))
    cir = build.trace(
        cir,
        "relays:latch_C/coil1",
        [("latch_C-GND00", [11, 23])],
        "nodes:GND11",
    )

    # XOR(C, D)
    # =========
    cir["relays"]["xorc"] = {"pos": [12, 19], "rot": 0}
    cir["relays"]["xord"] = {"pos": [15, 31], "rot": 2}
    cir["bars"].append(("relays:xorc/ncl", "relays:xord/nop"))
    cir = build.trace(cir, "relays:xorc/nop", [], "relays:xord/ncl",)
    cir = build.trace(cir, "relays:xorc/in0", [], "nodes:CLOCK12")

    cir = build.trace(cir, "relays:xord/in0", [], "nodes:V15")

    cir = build.trace(
        cir, "relays:xorc/coil0", [("xorc", [13, 23]),], "nodes:C13"
    )
    cir = build.trace(
        cir, "relays:xord/coil0", [("xord", [14, 27]),], "nodes:D14"
    )
    # GND
    cir = build.trace(
        cir, "relays:xorc/coil1", [("xorc-gnd", [16, 23]),], "nodes:GND16"
    )
    cir = build.trace(
        cir, "relays:xord/coil1", [("xord-gnd", [13, 27]),], "nodes:GND13"
    )

    # Cycler
    # ======

    # CYCLER AD(B, C)
    # ---------------
    cir["relays"]["cycleAD-B"] = {"pos": [25, 31], "rot": 2}
    cir["relays"]["cycleAD-C"] = {"pos": [25, 24], "rot": 2}

    cir = build.trace(
        cir,
        "relays:cycleAD-C/coil1",
        [("cycADgnd0", [23, 20]), ("cycADgnd1", [23, 27]),],
        "relays:cycleAD-B/coil1",
    )
    cir["bars"].append(("nodes:cycADgnd1", "nodes:GND23"))

    cir["bars"].append(("nodes:V25", "relays:cycleAD-B/in0"))

    cir = build.trace(
        cir, "relays:cycleAD-B/coil0", [("cycAD-B0", [24, 27]),], "nodes:B24",
    )
    cir["bars"].append(("relays:cycleAD-B/ncl", "relays:cycleAD-C/in1"))

    cir = build.trace(
        cir, "relays:cycleAD-C/coil0", [("cycAD-C0", [26, 20]),], "nodes:C26",
    )
    cir["bars"].append(("relays:cycleAD-C/ncl", "nodes:A22"))
    cir["bars"].append(("relays:cycleAD-C/nop", "nodes:D25"))

    # CYCLER B(D, A)
    # --------------
    cir["relays"]["cycleB-D"] = {"pos": [30, 31], "rot": 2}
    cir["relays"]["cycleB-A"] = {"pos": [30, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays:cycleB-A/coil1",
        [("cycBgnd0", [28, 20]), ("cycBgnd1", [28, 27]),],
        "relays:cycleB-D/coil1",
    )
    cir["bars"].append(("nodes:cycBgnd1", "nodes:GND28"))
    cir["bars"].append(("nodes:V30", "relays:cycleB-D/in0"))

    cir = build.trace(
        cir, "relays:cycleB-D/coil0", [("cycB-D0", [29, 27]),], "nodes:D29",
    )
    cir["bars"].append(("relays:cycleB-D/ncl", "relays:cycleB-A/in1"))
    cir = build.trace(
        cir, "relays:cycleB-A/coil0", [("cycB-A0", [31, 20]),], "nodes:A31",
    )
    cir["bars"].append(("relays:cycleB-A/nop", "nodes:B30"))

    # CYCLER C(A, B)
    # --------------
    cir["relays"]["cycleC-A"] = {"pos": [35, 31], "rot": 2}
    cir["relays"]["cycleC-B"] = {"pos": [35, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays:cycleC-B/coil1",
        [("cycCgnd0", [33, 20]), ("cycCgnd1", [33, 27]),],
        "relays:cycleC-A/coil1",
    )
    cir["bars"].append(("nodes:cycCgnd1", "nodes:GND33"))
    cir["bars"].append(("nodes:V35", "relays:cycleC-A/in0"))

    cir = build.trace(
        cir, "relays:cycleC-A/coil0", [("cycC-A0", [34, 27]),], "nodes:A34",
    )
    cir["bars"].append(("relays:cycleC-A/ncl", "relays:cycleC-B/in1"))
    cir = build.trace(
        cir, "relays:cycleC-B/coil0", [("cycC-B0", [36, 20]),], "nodes:B36",
    )
    cir["bars"].append(("relays:cycleC-B/nop", "nodes:C35"))

    # capacitors
    # ==========

    CAP_X = 9
    cir["capacitors"]["CAP-A"] = {
        "pos": [CAP_X, 4],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors:CAP-A", "nodes:A{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-B"] = {
        "pos": [CAP_X, 7],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors:CAP-B", "nodes:B{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-C"] = {
        "pos": [CAP_X, 10],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors:CAP-C", "nodes:C{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-D"] = {
        "pos": [CAP_X, 13],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors:CAP-D", "nodes:D{:02d}".format(CAP_X)))

    # lamps
    # =====
    LAM_X = 20
    cir["nodes"]["LAMP-A"] = {"pos": [LAM_X, 4 + 1], "lamp": True}
    cir["bars"].append(("nodes:LAMP-A", "nodes:A{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-B"] = {"pos": [LAM_X, 7 + 1], "lamp": True}
    cir["bars"].append(("nodes:LAMP-B", "nodes:B{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-C"] = {"pos": [LAM_X, 10 + 1], "lamp": True}
    cir["bars"].append(("nodes:LAMP-C", "nodes:C{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-D"] = {"pos": [LAM_X, 13 + 1], "lamp": True}
    cir["bars"].append(("nodes:LAMP-D", "nodes:D{:02d}".format(LAM_X)))

    return cir


def make_sequencer(labels_left=True, labels_right=True, abort_latch=True):
    """
    motivated by Paul Law
    """
    cir = build.empty_circuit()

    odd = 0

    sy = 2
    dy = 7

    sx = 2
    dx = 5

    cir["relays"]["ODD-0"] = {"pos": [sx + 0*dx, sy + 0*dy], "rot": 0}
    cir["relays"]["ODD-1"] = {"pos": [sx + 0*dx, sy + 1*dy], "rot": 0}
    cir["relays"]["ODD-2"] = {"pos": [sx + 0*dx, sy + 2*dy], "rot": 0}
    cir["relays"]["ODD-3"] = {"pos": [sx + 0*dx, sy + 3*dy], "rot": 0}

    even = odd + 1

    cir["relays"]["EVE-0"] = {"pos": [sx + 2*dx, sy + 0*dy], "rot": 0}
    cir["relays"]["EVE-1"] = {"pos": [sx + 2*dx, sy + 1*dy], "rot": 0}
    cir["relays"]["EVE-2"] = {"pos": [sx + 2*dx, sy + 2*dy], "rot": 0}
    cir["relays"]["EVE-3"] = {"pos": [sx + 2*dx, sy + 3*dy], "rot": 0}

    cir["relays"]["TICKTOCK".format(odd)] = {"pos": [sx + 1*dx, sy + 2*dy + 2], "rot": 0}

    Z_y = sy + 27
    Y_y = sy - 2
    X_y = sy - 1
    GND_y = sy + 28
    V_y = sy
    CLOCK_y = sy + 29
    RESET_y = sy + 37
    Sminus1_y = sy + 36
    cir["nodes"]["Z_left"] = {"pos": [sx - 2, Z_y]}
    cir["nodes"]["Z_right"] = {"pos": [4*dx -2, Z_y]}

    cir["nodes"]["Y_left"] = {"pos": [sx - 2, Y_y]}
    cir["nodes"]["Y_right"] = {"pos": [4*dx -2, Y_y]}

    cir["nodes"]["X_left"] = {"pos": [sx - 2, X_y]}
    cir["nodes"]["X_right"] = {"pos": [4*dx -2, X_y]}

    cir["nodes"]["GND_left"] = {"pos": [sx - 2, GND_y]}
    cir["nodes"]["GND_right"] = {"pos": [4*dx -2, GND_y]}

    cir["nodes"]["V_left"] = {"pos": [sx - 2, V_y]}
    cir["nodes"]["V_right"] = {"pos": [4*dx -2, V_y]}

    cir["nodes"]["CLOCK_left"] = {"pos": [sx - 2, CLOCK_y]}
    cir["nodes"]["CLOCK_right"] = {"pos": [4*dx -2, CLOCK_y]}

    cir["nodes"]["RESET_left"] = {"pos": [sx - 2, RESET_y]}
    cir["nodes"]["RESET_right"] = {"pos": [4*dx -2, RESET_y]}

    cir["nodes"]["Sminus1_left"] = {"pos": [sx - 2, Sminus1_y]}
    cir["nodes"]["Sminus1_right"] = {"pos": [4*dx -2, Sminus1_y]}


    if labels_left:
        cir["nodes"]["Z_left"]["name"] = "Z_left"
        cir["nodes"]["Y_left"]["name"] = "Y_left"
        cir["nodes"]["X_left"]["name"] = "X_left"
        cir["nodes"]["GND_left"]["name"] = "GND_left"
        cir["nodes"]["V_left"]["name"] = "V_left"
        cir["nodes"]["CLOCK_left"]["name"] = "CLOCK_left"
        cir["nodes"]["Sminus1_left"]["name"] = "Sminus1_right"
        cir["nodes"]["RESET_left"]["name"] = "RESET_left"
    if labels_right:
        cir["nodes"]["Z_right"]["name"] = "Z_right"
        cir["nodes"]["Y_right"]["name"] = "Y_right"
        cir["nodes"]["X_right"]["name"] = "X_right"
        cir["nodes"]["GND_right"]["name"] = "GND_right"
        cir["nodes"]["V_right"]["name"] = "V_right"
        cir["nodes"]["CLOCK_right"]["name"] = "CLOCK_right"
        cir["nodes"]["Sminus1_right"]["name"] = "Sminus1_right"
        cir["nodes"]["RESET_right"]["name"] = "RESET_right"

    # tick-tock-clock-divider
    cir["bars"].append((
        "relays:TICKTOCK/nop",
        "relays:ODD-3/in1",
    ))
    cir["bars"].append((
        "relays:TICKTOCK/ncl",
        "relays:EVE-3/in0",
    ))

    # GND
    # ===

    # odd GND
    cir["nodes"]["GND_odd_4"] = {"pos": [sx + 2, GND_y]}
    for ii in range(4):
        rr = 3 - ii
        cir = build.trace(
            cir,
            "nodes:GND_odd_{:d}".format(rr + 1),
            [("GND_odd_{:d}".format(rr), [sx+2, sy + rr*dy + 4])],
            "relays:ODD-{:d}/coil1".format(rr),
        )

    # even GND
    cir["nodes"]["GND_even_4"] = {"pos": [sx+2*dx + 2, GND_y]}
    for ii in range(4):
        rr = 3 - ii
        cir = build.trace(
            cir,
            "nodes:GND_even_{:d}".format(rr + 1),
            [("GND_even_{:d}".format(rr), [sx+2*dx+2, sy + rr*dy + 4])],
            "relays:EVE-{:d}/coil1".format(rr),
        )

    # tick-tock GND
    cir["nodes"]["GND_tick_tock_4"] = {"pos": [sx+1*dx + 2, GND_y]}
    cir = build.trace(
        cir,
        "nodes:GND_tick_tock_4",
        [("GND_tick_tock_3", [sx+1*dx+2, sy + 20])],
        "relays:TICKTOCK/coil1".format(odd),
    )

    # GND bus
    cir["bars"].append(("nodes:GND_left", "nodes:GND_odd_4"))
    cir["bars"].append(("nodes:GND_odd_4", "nodes:GND_tick_tock_4"))
    cir["bars"].append(("nodes:GND_tick_tock_4", "nodes:GND_even_4"))
    cir["bars"].append(("nodes:GND_even_4", "nodes:GND_right"))

    # V
    # =

    # V bus
    cir["bars"].append(("nodes:V_left", "relays:ODD-0/in0"))
    cir["bars"].append(("relays:ODD-0/in1", "relays:EVE-0/in0"))
    cir["bars"].append(("nodes:V_left", "relays:ODD-0/in0"))
    cir["bars"].append(("nodes:V_right", "relays:EVE-0/in1"))

    # V tick-tock
    cir = build.trace(
        cir,
        "relays:EVE-0/in0",
        [
            ("tt1", [sx + 10, sy +3]),
            ("tt0", [sx + 8, sy +3]),
        ],
        "relays:TICKTOCK/in1",
    )

    # CLOCK
    # =====
    cir["nodes"]["CLOCK_1"] = {"pos": [sx+1*dx + 1, CLOCK_y]}
    cir = build.trace(
        cir,
        "nodes:CLOCK_1".format(even),
        [("CLOCK_2", [sx+1*dx + 1, sy + 20])],
        "relays:TICKTOCK/coil0",
    )

    # CLOCK bus
    cir["bars"].append(("nodes:CLOCK_left", "nodes:CLOCK_1"))
    cir["bars"].append(("nodes:CLOCK_1", "nodes:CLOCK_right"))

    # Z left
    # ======
    cir["nodes"]["Z_odd_4"] = {"pos": [sx+0*dx-1, Z_y]}
    cir["bars"].append(("nodes:Z_left", "nodes:Z_odd_4"))

    cir["nodes"]["Z_odd_3"] = {"pos": [sx+0*dx-1, sy + 3*dy + 4]}
    cir["bars"].append(("nodes:Z_odd_4", "nodes:Z_odd_3"))
    cir["bars"].append(("relays:ODD-3/coil0", "nodes:Z_odd_3"))

    cir["nodes"]["Z_odd_2l"] = {"pos": [sx+0*dx-1, sy + 2*dy + 4 + 1]}
    cir["bars"].append(("nodes:Z_odd_3", "nodes:Z_odd_2l"))
    cir["bars"].append(("relays:ODD-2/nop", "nodes:Z_odd_2l"))

    cir["nodes"]["Z_odd_2"] = {"pos": [sx+0*dx-1, sy + 2*dy + 4]}
    cir["bars"].append(("nodes:Z_odd_2l", "nodes:Z_odd_2"))
    cir["bars"].append(("relays:ODD-2/coil0", "nodes:Z_odd_2"))

    cir["nodes"]["Z_odd_1"] = {"pos": [sx+0*dx-1, sy + 1*dy + 4]}
    cir["bars"].append(("nodes:Z_odd_2", "nodes:Z_odd_1"))
    cir["bars"].append(("relays:ODD-1/coil0", "nodes:Z_odd_1"))

    cir["nodes"]["Z_odd_0"] = {"pos": [sx+0*dx-1, sy + 0*dy + 4]}
    cir["bars"].append(("nodes:Z_odd_1", "nodes:Z_odd_0"))
    cir["bars"].append(("relays:ODD-0/coil0", "nodes:Z_odd_0"))

    # Inner
    # =====

    # odd
    cir["nodes"]["I_odd_4"] = {"pos": [sx+0*dx+1, Z_y]}

    cir["nodes"]["I_odd_3"] = {"pos": [sx+0*dx+1, sy + 3*dy + 5]}
    cir["bars"].append(("nodes:I_odd_4", "nodes:I_odd_3"))
    cir["bars"].append(("relays:ODD-3/nop", "nodes:I_odd_3"))

    cir["nodes"]["I_odd_1"] = {"pos": [sx+0*dx+1, sy + 1*dy + 5]}
    cir["bars"].append(("nodes:I_odd_3", "nodes:I_odd_1"))
    cir["bars"].append(("relays:ODD-1/nop", "nodes:I_odd_1"))

    cir["nodes"]["I_eve_4"] = {"pos": [sx+2*dx-1, Z_y]}
    cir["bars"].append(("nodes:I_odd_4", "nodes:I_eve_4"))

    # even
    cir["nodes"]["I_eve_3"] = {"pos": [sx+2*dx-1, sy + 3*dy + 4]}
    cir["bars"].append(("nodes:I_eve_4", "nodes:I_eve_3"))
    cir["bars"].append(("relays:EVE-3/coil0", "nodes:I_eve_3"))

    cir["nodes"]["I_eve_2l"] = {"pos": [sx+2*dx-1, sy + 2*dy + 4 + 1]}
    cir["bars"].append(("nodes:I_eve_3", "nodes:I_eve_2l"))
    cir["bars"].append(("relays:EVE-2/nop", "nodes:I_eve_2l"))

    cir["nodes"]["I_eve_2"] = {"pos": [sx+2*dx-1, sy + 2*dy + 4]}
    cir["bars"].append(("nodes:I_eve_2l", "nodes:I_eve_2"))
    cir["bars"].append(("relays:EVE-2/coil0", "nodes:I_eve_2"))

    cir["nodes"]["I_eve_1"] = {"pos": [sx+2*dx-1, sy + 1*dy + 4]}
    cir["bars"].append(("nodes:I_eve_2", "nodes:I_eve_1"))
    cir["bars"].append(("relays:EVE-1/coil0", "nodes:I_eve_1"))

    cir["nodes"]["I_eve_0"] = {"pos": [sx+2*dx-1, sy + 0*dy + 4]}
    cir["bars"].append(("nodes:I_eve_1", "nodes:I_eve_0"))
    cir["bars"].append(("relays:EVE-0/coil0", "nodes:I_eve_0"))

    # Z right
    # =======
    cir["nodes"]["Z_abort_zo"] = {"pos": [sx+15, Z_y]}
    cir["nodes"]["Z_abort_zi"] = {"pos": [sx+14, Z_y]}
    cir["bars"].append(("nodes:Z_abort_zo", "nodes:Z_right"))

    if not abort_latch:
        cir["bars"].append(("nodes:Z_abort_zo", "nodes:Z_abort_zi"))

    cir["nodes"]["Z_eve_4"] = {"pos": [sx+2*dx+1, Z_y]}
    cir["bars"].append(("nodes:Z_abort_zi", "nodes:Z_eve_4"))
    cir["nodes"]["Z_eve_3"] = {"pos": [sx+2*dx+1, sy + 3*dy + 5]}
    cir["bars"].append(("nodes:Z_eve_4", "nodes:Z_eve_3"))
    cir["bars"].append(("relays:EVE-3/nop", "nodes:Z_eve_3"))

    cir["nodes"]["Z_eve_1"] = {"pos": [sx+2*dx+1, sy + 1*dy + 5]}
    cir["bars"].append(("nodes:Z_eve_3", "nodes:Z_eve_1"))
    cir["bars"].append(("relays:EVE-1/nop", "nodes:Z_eve_1"))

    # X left
    # ======
    cir = build.trace(
        cir,
        "nodes:X_left",
        [
            ("Xl_0", [sx + 1, X_y]),
            ("Xl_1", [sx + 1, sy + 2]),
            ("Xl_2", [sx + 4, sy + 2]),
            ("Xl_3", [sx + 4, sy + 5]),
        ],
        "relays:ODD-0/ncl",
    )

    # X right
    # =======
    cir = build.trace(
        cir,
        "nodes:X_right",
        [
            ("Xr_0", [sx + 2, X_y]),
            ("Xr_1", [sx + 2, sy + 1]),
            ("Xr_2", [sx + 5, sy + 1]),
            ("Xr_3", [sx + 5, sy + 6]),
            ("Xr_4", [sx + 4, sy + 6]),
            ("Xr_5", [sx + 4, sy + 2*dy + 5]),
        ],
        "relays:ODD-2/ncl",
    )

    # Y left
    # ======
    cir = build.trace(
        cir,
        "nodes:Y_left",
        [
            ("Yl_1", [sx - 2, Y_y]),
            ("Yl_2", [sx + 11, Y_y]),
            ("Yl_3", [sx + 11, sy + 3]),
            ("Yl_4", [sx + 14, sy + 3]),
            ("Yl_5", [sx + 14, sy + 5]),
        ],
        "relays:EVE-0/ncl",
    )

    # Y right
    # =======
    cir = build.trace(
        cir,
        "relays:EVE-2/in1",
        [
            ("Yr_0", [sx + 14, sy + 14]),
            ("Yr_1", [sx + 14, sy + 6]),
            ("Yr_3", [sx + 15, sy + 6]),
            ("Yr_4", [sx + 15, sy + 2]),
            ("Yr_5", [sx + 12, sy + 2]),
            ("Yr_6", [sx + 12, Y_y]),
        ],
        "nodes:Y_right",
    )

    if abort_latch:
        cir["nodes"]["RESET_down"] = {"pos": [sx+10, RESET_y]}
        cir["bars"].append(("nodes:RESET_left", "nodes:RESET_down"))
        cir["bars"].append(("nodes:RESET_down", "nodes:RESET_right"))

        cir["nodes"]["Sminus1_down"] = {"pos": [sx+5, Sminus1_y]}
        cir["bars"].append(("nodes:Sminus1_left", "nodes:Sminus1_down"))
        cir["bars"].append(("nodes:Sminus1_down", "nodes:Sminus1_right"))


        cir["relays"]["ABORT-0"] = {"pos": [sx + 5, sy + 30], "rot": 0}
        cir["relays"]["ABORT-1"] = {"pos": [sx +10, sy + 30], "rot": 0}

        cir["bars"].append(("relays:ABORT-1/nop", "nodes:RESET_down"))

        cir["nodes"]["Z_abort_zo_1"] = {"pos": [sx+15, Z_y + 8]}
        cir["nodes"]["Z_abort_zi_1"] = {"pos": [sx+14, Z_y + 3]}
        cir["bars"].append(("nodes:Z_abort_zi", "nodes:Z_abort_zi_1"))
        cir["bars"].append(("nodes:Z_abort_zi_1", "relays:ABORT-1/in1"))
        cir["bars"].append(("nodes:Z_abort_zo", "nodes:Z_abort_zo_1"))
        cir["bars"].append(("nodes:Z_abort_zo_1", "relays:ABORT-1/ncl"))

        cir["bars"].append(("relays:ABORT-0/nop", "nodes:Sminus1_down"))

        # GND
        # ---
        cir["bars"].append(("relays:ABORT-0/coil1", "nodes:GND_odd_4"))
        cir["bars"].append(("relays:ABORT-1/coil1", "nodes:GND_even_4"))

        # latch
        cir["bars"].append(("relays:ABORT-0/coil0", "relays:ABORT-0/in0"))

        # ABORT-0 and ABORT-1 run in sync, and ABORT-0 is latched so:
        cir = build.trace(
            cir,
            "relays:ABORT-0/in1",
            [
                ("abo_00", [sx + 9, sy + 30]),
                ("abo_01", [sx + 9, sy + 34])
            ],
            "relays:ABORT-1/coil0",
        )

    return cir
