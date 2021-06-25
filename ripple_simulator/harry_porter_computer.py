import numpy as np
from . import build
from . import logic


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
                "nodes/gnd-bit-{:02d}".format(bit),
                "nodes/gnd-bit-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd-bit-{:02d}".format(bit),
                "relays/bit-{:02d}/coil1".format(bit),
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
                "nodes/hold-{:02d}".format(bit),
                "nodes/hold-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/hold-{:02d}".format(bit),
                "relays/bit-{:02d}/nop".format(bit),
            )
        )

    # bit latch
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/bit-{:02d}/in0".format(bit),
                "relays/bit-{:02d}/coil0".format(bit),
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
                "nodes/gnd-ena-{:02d}".format(bit),
                "nodes/gnd-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/gnd-ena-{:02d}".format(bit),
                "relays/ena-dat-{:02d}/coil1".format(bit),
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
                "nodes/ena-ena-{:02d}".format(bit),
                "nodes/ena-ena-{:02d}".format(bit + 1),
            )
        )
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "nodes/ena-ena-{:02d}".format(bit),
                "relays/ena-dat-{:02d}/coil0".format(bit),
            )
        )

    # bit to enable
    for bit in range(num_bits):
        cir["bars"].append(
            (
                "relays/ena-dat-{:02d}/in1".format(bit),
                "relays/bit-{:02d}/in0".format(bit),
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
            ("relays/ena-dat-{:02d}/nop".format(bit), "nodes/" + node_name,)
        )

    # indicator lamps
    for bit in range(num_bits):
        lamp_name = "LAMP{:02d}".format(bit)
        lamp_con_node = "lam-{:02d}".format(bit)
        cir["nodes"][lamp_name] = {"pos": [ox + 4 + bit * 7, 3], "lamp": True}
        cir["nodes"][lamp_con_node] = {"pos": [ox + 1 + bit * 7, 3]}

        cir["bars"].append(
            ("relays/bit-{:02d}/in1".format(bit), "nodes/" + lamp_con_node,)
        )
        cir["bars"].append(
            ("nodes/" + lamp_con_node, "nodes/" + lamp_name)
        )

    # lamp gnd
    for bit in range(num_bits):
        cir["nodes"]["gnd-lmp-{:02d}".format(bit)] = {
            "pos": [ox + 5 + bit * 7, 2]
        }
    for bit in range(num_bits - 1):
        cir["bars"].append(
            (
                "nodes/gnd-lmp-{:02d}".format(bit),
                "nodes/gnd-lmp-{:02d}".format(bit + 1),
            )
        )

    cir["nodes"]["HOLD"] = {"pos": [ox, 8], "name": "HOLD"}
    cir["bars"].append(("nodes/HOLD", "nodes/hold-00"))

    cir["nodes"]["ENABLE"] = {"pos": [ox, 13], "name": "ENABLE"}
    cir["bars"].append(("nodes/ENABLE", "nodes/ena-ena-00"))

    cir["relays"]["LOAD-NOT-HOLD"] = {"pos": [1, 4], "rot": 1}
    cir["relays"]["LOAD-NOT-SELECT"] = {"pos": [1, 9], "rot": 1}
    cir["relays"]["LOAD-NOT-SELECT-2"] = {"pos": [1, 14], "rot": 1}

    # V
    cir = build.trace(cir, "nodes/V", [("vv0", [1, 3])], "relays/LOAD-NOT-HOLD/in0")
    cir["bars"].append(("relays/LOAD-NOT-HOLD/in0", "relays/LOAD-NOT-SELECT/in1"))
    cir["bars"].append(("relays/LOAD-NOT-SELECT/in0", "relays/LOAD-NOT-SELECT-2/in1"))

    # GND
    cir["nodes"]["gnd-2-2"] = {"pos": [2, 2]}
    cir["bars"].append(("nodes/GND", "nodes/gnd-2-2"))

    cir["nodes"]["gnd-2-1"] = {"pos": [2, 1]}
    cir["bars"].append(("nodes/gnd-2-2", "nodes/gnd-2-1"))
    cir["bars"].append(("relays/LOAD-NOT-HOLD/coil1", "nodes/gnd-2-1"))

    cir["nodes"]["gnd-2-6"] = {"pos": [2, 6]}
    cir["bars"].append(("nodes/gnd-2-2", "nodes/gnd-2-6"))
    cir["bars"].append(("relays/LOAD-NOT-SELECT/coil1", "nodes/gnd-2-6"))

    # GND to bits
    cir["nodes"]["gnd-2-7"] = {"pos": [2, 7]}
    cir["bars"].append(("nodes/gnd-2-6", "nodes/gnd-2-7"))
    cir["bars"].append(("nodes/gnd-bit-00", "nodes/gnd-2-7"))

    cir["nodes"]["gnd-2-11"] = {"pos": [2, 11]}
    cir["bars"].append(("nodes/gnd-2-7", "nodes/gnd-2-11"))
    cir["bars"].append(("relays/LOAD-NOT-SELECT-2/coil1", "nodes/gnd-2-11"))

    # GND to enable
    cir["nodes"]["gnd-2-12"] = {"pos": [2, 12]}
    cir["bars"].append(("nodes/gnd-2-11", "nodes/gnd-2-12"))
    cir["bars"].append(("nodes/gnd-ena-00", "nodes/gnd-2-12"))

    # GND lamps
    cir["bars"].append(("nodes/gnd-2-2", "nodes/gnd-lmp-00"))

    # LOAD
    cir["nodes"]["load-4-8"] = {"pos": [4, 8]}
    cir["bars"].append(("nodes/LOAD", "nodes/load-4-8"))
    cir = build.trace(cir, "relays/LOAD-NOT-SELECT/coil0", [("nn0", [4, 9])], "nodes/load-4-8")
    cir = build.trace(cir, "relays/LOAD-NOT-HOLD/coil0", [["nn1", [4, 4]]], "nodes/load-4-8")
    cir = build.trace(cir, "relays/LOAD-NOT-HOLD/ncl", [("hh0", [7, 1])], "nodes/HOLD")

    # SELECT

    cir["bars"].append(("nodes/SELECT", "nodes/ENABLE"))
    cir = build.trace(cir, "nodes/ENABLE", [("en-7-11", [7, 11])], "relays/LOAD-NOT-SELECT-2/ncl")

    cir = build.trace(
        cir, "relays/LOAD-NOT-SELECT/ncl", [
            ("sl-00", [6, 5]),
            ("sl-01", [3, 5]),
            ("sl-02", [3, 14]),
        ], "relays/LOAD-NOT-SELECT-2/coil0"
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
                    "nodes/gnd-ena-adr-{:02d}".format(bit),
                    "nodes/gnd-ena-adr-{:02d}".format(bit + 1),
                )
            )
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "nodes/gnd-ena-adr-{:02d}".format(bit),
                    "relays/ena-adr-{:02d}/coil1".format(bit),
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
                    "nodes/ena-ena-adr-{:02d}".format(bit),
                    "nodes/ena-ena-adr-{:02d}".format(bit + 1),
                )
            )
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "nodes/ena-ena-adr-{:02d}".format(bit),
                    "relays/ena-adr-{:02d}/coil0".format(bit),
                )
            )

        # bit to ena-adr
        for bit in range(num_bits):
            cir["bars"].append(
                (
                    "relays/ena-adr-{:02d}/in1".format(bit),
                    "relays/ena-dat-{:02d}/in0".format(bit),
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
                ("relays/ena-adr-{:02d}/nop".format(bit), "nodes/" + node_name,)
            )


    return cir


def make_clock(periode):
    cir = build.empty_circuit()

    cir = build.bar_x(cir=cir, pos=[1, 4], length=33, name="A", label=True)
    cir = build.bar_x(cir=cir, pos=[5, 5], length=16, name="A-GND", label=False)

    cir = build.bar_x(cir=cir, pos=[5, 7], length=31, name="B", label=True)
    cir = build.bar_x(cir=cir, pos=[5, 8], length=16, name="B-GND", label=False)

    cir = build.bar_x(cir=cir, pos=[5, 10], length=30, name="C", label=True)
    cir = build.bar_x(cir=cir, pos=[5, 11], length=16, name="C-GND", label=False)

    cir = build.bar_x(cir=cir, pos=[5, 13], length=24, name="D", label=True)
    cir = build.bar_x(cir=cir, pos=[5, 14], length=16, name="D-GND", label=False)


    cir = build.bar_x(cir=cir, pos=[1, 30], length=35, name="V", label=True)
    cir = build.bar_x(cir=cir, pos=[1, 28], length=35, name="GND", label=True)

    cir = build.bar_x(
        cir=cir, pos=[1, 17], length=11, name="CLOCK", label=True
    )
    cir = build.bar_x(cir=cir, pos=[1, 26], length=3, name="FRZ", label=True)

    # Freeze
    # ======

    cir["relays"]["frz1"] = {"pos": [5, 31], "rot": 2, "comment": "Prevent backdriving thr FRZ-line"}
    cir = build.trace(cir, "relays/frz1/coil0", [("frz1-coil0", [4, 27])], "nodes/FRZ04",)
    cir = build.trace(cir, "relays/frz1/coil1", [("frz1-gnd", [3, 27])], "nodes/GND03",)
    cir = build.trace(cir, "relays/frz1/in0", [], "nodes/V05",)

    cir = build.bar_x(cir=cir, pos=[2, 25], length=5, name="latch_BAR")
    cir["bars"].append(("relays/latch_A/nop", "nodes/latch_BAR"))
    cir["bars"].append(("relays/latch_C/nop", "nodes/latch_BAR07"))
    cir["bars"].append(("relays/frz1/nop", "nodes/latch_BAR05"))

    # latch A
    cir["relays"]["latch_A"] = {"pos": [2, 19], "rot": 0}
    #cir["bars"].append(("relays/latch_A/nop", "nodes/FRZ02"))
    cir["bars"].append(("relays/latch_A/coil0", "relays/latch_A/in0"))
    cir["bars"].append(("nodes/A02", "relays/latch_A/in0"))

    # latch C
    cir["relays"]["latch_C"] = {"pos": [7, 19], "rot": 0}
    #cir["bars"].append(("relays/latch_C/nop", "nodes/FRZ07"))
    cir["bars"].append(("relays/latch_C/coil0", "relays/latch_C/in0"))
    cir["bars"].append(("nodes/C07", "relays/latch_C/in0"))

    cir = build.bar_x(cir=cir, pos=[5, 22], length=5, name="latch_GND")
    cir["bars"].append(("nodes/latch_GND", "relays/latch_A/coil1"))
    cir["bars"].append(("nodes/latch_GND10", "relays/latch_C/coil1"))
    cir = build.trace(cir, "relays/latch_C/coil1", [("latch_C-GND00", [11, 23])], "nodes/GND11")

    # XOR(C, D)
    # =========
    cir["relays"]["xorc"] = {"pos": [12, 19], "rot": 0}
    cir["relays"]["xord"] = {"pos": [15, 31], "rot": 2}
    cir["bars"].append(("relays/xorc/ncl", "relays/xord/nop"))
    cir = build.trace(cir, "relays/xorc/nop", [], "relays/xord/ncl",)
    cir = build.trace(
        cir, "relays/xorc/in0", [], "nodes/CLOCK12"
    )

    cir = build.trace(
        cir, "relays/xord/in0", [], "nodes/V15"
    )

    cir = build.trace(
        cir, "relays/xorc/coil0", [("xorc", [13, 23]),], "nodes/C13"
    )
    cir = build.trace(
        cir, "relays/xord/coil0", [("xord", [14, 27]),], "nodes/D14"
    )
    # GND
    cir = build.trace(
        cir, "relays/xorc/coil1", [("xorc-gnd", [16, 23]),], "nodes/GND16"
    )
    cir = build.trace(
        cir, "relays/xord/coil1", [("xord-gnd", [13, 27]),], "nodes/GND13"
    )

    # Cycler
    # ======

    # CYCLER AD(B, C)
    # ---------------
    cir["relays"]["cycleAD-B"] = {"pos": [25, 31], "rot": 2}
    cir["relays"]["cycleAD-C"] = {"pos": [25, 24], "rot": 2}

    cir = build.trace(
        cir,
        "relays/cycleAD-C/coil1",
        [("cycADgnd0", [23, 20]), ("cycADgnd1", [23, 27]),],
        "relays/cycleAD-B/coil1",
    )
    cir["bars"].append(("nodes/cycADgnd1", "nodes/GND23"))

    cir["bars"].append(("nodes/V25", "relays/cycleAD-B/in0"))

    cir = build.trace(
        cir, "relays/cycleAD-B/coil0", [("cycAD-B0", [24, 27]),], "nodes/B24",
    )
    cir["bars"].append(("relays/cycleAD-B/ncl", "relays/cycleAD-C/in1"))

    cir = build.trace(
        cir, "relays/cycleAD-C/coil0", [("cycAD-C0", [26, 20]),], "nodes/C26",
    )
    cir["bars"].append(("relays/cycleAD-C/ncl", "nodes/A22"))
    cir["bars"].append(("relays/cycleAD-C/nop", "nodes/D25"))

    # CYCLER B(D, A)
    # --------------
    cir["relays"]["cycleB-D"] = {"pos": [30, 31], "rot": 2}
    cir["relays"]["cycleB-A"] = {"pos": [30, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays/cycleB-A/coil1",
        [("cycBgnd0", [28, 20]), ("cycBgnd1", [28, 27]),],
        "relays/cycleB-D/coil1",
    )
    cir["bars"].append(("nodes/cycBgnd1", "nodes/GND28"))
    cir["bars"].append(("nodes/V30", "relays/cycleB-D/in0"))

    cir = build.trace(
        cir, "relays/cycleB-D/coil0", [("cycB-D0", [29, 27]),], "nodes/D29",
    )
    cir["bars"].append(("relays/cycleB-D/ncl", "relays/cycleB-A/in1"))
    cir = build.trace(
        cir, "relays/cycleB-A/coil0", [("cycB-A0", [31, 20]),], "nodes/A31",
    )
    cir["bars"].append(("relays/cycleB-A/nop", "nodes/B30"))

    # CYCLER C(A, B)
    # --------------
    cir["relays"]["cycleC-A"] = {"pos": [35, 31], "rot": 2}
    cir["relays"]["cycleC-B"] = {"pos": [35, 24], "rot": 2}
    cir = build.trace(
        cir,
        "relays/cycleC-B/coil1",
        [("cycCgnd0", [33, 20]), ("cycCgnd1", [33, 27]),],
        "relays/cycleC-A/coil1",
    )
    cir["bars"].append(("nodes/cycCgnd1", "nodes/GND33"))
    cir["bars"].append(("nodes/V35", "relays/cycleC-A/in0"))

    cir = build.trace(
        cir, "relays/cycleC-A/coil0", [("cycC-A0", [34, 27]),], "nodes/A34",
    )
    cir["bars"].append(("relays/cycleC-A/ncl", "relays/cycleC-B/in1"))
    cir = build.trace(
        cir, "relays/cycleC-B/coil0", [("cycC-B0", [36, 20]),], "nodes/B36",
    )
    cir["bars"].append(("relays/cycleC-B/nop", "nodes/C35"))

    # capacitors
    # ==========

    CAP_X = 9
    cir["capacitors"]["CAP-A"] = {
        "pos": [CAP_X, 4],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-A", "nodes/A{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-B"] = {
        "pos": [CAP_X, 7],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-B", "nodes/B{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-C"] = {
        "pos": [CAP_X, 10],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-C", "nodes/C{:02d}".format(CAP_X)))

    cir["capacitors"]["CAP-D"] = {
        "pos": [CAP_X, 13],
        "rot": 0,
        "capacity": periode,
    }
    cir["bars"].append(("capacitors/CAP-D", "nodes/D{:02d}".format(CAP_X)))

    # lamps
    # =====
    LAM_X = 20
    cir["nodes"]["LAMP-A"] = {"pos": [LAM_X, 4 + 1], "lamp": True}
    cir["bars"].append(("nodes/LAMP-A", "nodes/A{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-B"] = {"pos": [LAM_X, 7 + 1], "lamp": True}
    cir["bars"].append(("nodes/LAMP-B", "nodes/B{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-C"] = {"pos": [LAM_X, 10 + 1], "lamp": True}
    cir["bars"].append(("nodes/LAMP-C", "nodes/C{:02d}".format(LAM_X)))

    cir["nodes"]["LAMP-D"] = {"pos": [LAM_X, 13 + 1], "lamp": True}
    cir["bars"].append(("nodes/LAMP-D", "nodes/D{:02d}".format(LAM_X)))

    return cir


def make_sequencer(num_steps):
    cir = build.empty_circuit()

    cir["nodes"]["V"] = {"pos": [0, 0], "name": "V"}
    cir["nodes"]["GND"] = {"pos": [0, 3], "name": "GND"}

    cir["nodes"]["CLOCK"] = {"pos": [0, 4], "name": "CLOCK"}


    cir["nodes"]["ANC"] = {"pos": [8, 6], "name": "ANC"}
    cir["nodes"]["UNC"] = {"pos": [5, 6], "name": "UNC"}

    cir["relays"]["clocker"] = {"pos": [5, 0], "rot": 0}

    cir["bars"].append(("relays/clocker/in0", "nodes/V"))
    cir["bars"].append(("relays/clocker/coil0", "nodes/CLOCK"))

    cir["bars"].append(("relays/clocker/nop", "nodes/UNC"))
    cir["bars"].append(("relays/clocker/ncl", "nodes/ANC"))


    cir["nodes"]["RESET"] = {"pos": [0, 14], "name": "RESET"}


    for t in range(num_steps):
        rname = "T{:02d}".format(t)
        cir["relays"][rname] = {"pos": [5 + 7*t, 15], "rot": 1}
        cir["bars"].append(("relays/"+rname+"/coil0", "relays/"+rname+"/in0"))
        cir["nodes"][rname+"_sel"] = {"pos": [10 + 7*t, 14]}
        cir["bars"].append(("relays/"+rname+"/nop", "nodes/"+rname+"_sel"))


    for t in range(num_steps - 1):
        rname = "T{:02d}".format(t)
        next_rname = "T{:02d}".format(t + 1)
        cir["bars"].append(("nodes/"+rname+"_sel", "nodes/"+next_rname+"_sel"))

    cir["bars"].append(("nodes/RESET", "nodes/T00_sel"))




    return cir
