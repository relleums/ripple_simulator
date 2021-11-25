import numpy as np

def zeros(shape):
    return np.zeros(shape=shape, dtype=np.uint8)


BITS = 16

state = {
    "registers": {
        "A": {"bits": zeros(BITS), "bus": {"DAT": 0,}},
        "B": {"bits": zeros(BITS), "bus": {"DAT": 0, "ALX": 0}},
        "C": {"bits": zeros(BITS), "bus": {"DAT": 0, "ALY": 0}},
        "D": {"bits": zeros(BITS), "bus": {"DAT": 0,}},
        "Z": {"bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "ALZ": 0}},
        "T": {"bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "ALZ": 0}},
        "M": {"bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "X": {"bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "J": {"bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "I": {"bits": zeros(BITS), "bus": {"DAT": 0,}},
        "P": {"bits": zeros(BITS), "bus": {"ADR": 0, "ALZ": 0}},
    },
    "alu": {
        "flags": {"sum": 0, "carry": 0, "zero": 0},
        "bits": zeros(BITS),
    },
    "memory": {
        "bits": zeros(shape=(2 ** BITS, BITS)),
        "bus": {"DATA": 0},
    },
    "clock": {
        "halt": 1,
        "sequencer": zeros(24),
    },
}

FETCH_INCREMENT_CTRLSEQ = {
    #           0000 0000 0011 1111 1111 2222
    #           0123 4567 8901 2345 6789 0123
    "P___ADR": "_~~~ ____ ",
    "MEM___R": "_~~~ ____ ",
    "I___CLR": "_~__ ____ ",
    "I___DAT": "__~_ ____ ",
    "ADR_ALY": "_~~~ ____ ",
    "ALU_INC": "_~~~ ____ ",
    "Z___CLR": "_~__ ____ ",
    "Z___ALZ": "__~_ ____ ",

    "Z___ALZ": "____ _~__ ", # if not GOTO: MOVE Z to P via ALZ
    "P___CLR": "____ ~___ ",
    "P___ALZ": "____ _~__ ",

    "I___INT": "___~ ~~~~ ~~~~",

    # MOVE-DAT A B
    # 000'.dddd.'''b.ssss
    "B___CLR": "____ ~___ ",
    "B___DAT": "____ _~__ ",
    "A___DAT": "____ _~__ ",

    # SET A B
    # 001d.vvvv.vvvv.vvvv

    # MEM R A
    # 010'.''''.''''.rrrr
    "M___ADR": "____ _~~~ ",
    "MEM___R": "____ _~~~ ",
    "A___CLR": "____ _~__ ",
    "A___DAT": "____ __~_ ",

    # MEM W A
    # 011'.''''.''''.rrrr
    "M___ADR": "____ _~~~ ",
    "MEM___W": "____ _~~_ ",
    "A___DAT": "____ _~~~ ",

    # ALU
    # 100d.ffff.ffff.ffff
    # A = B + C
    "B___ALX": "____ _~~~ ",
    "C___ALY": "____ _~~~ ",
    "ALU_ADD": "____ _~~~ ",
    "T___CLR": "____ _~__ ",
    "T___ALZ": "____ __~_ ",
    "A___CLR": "____ _~__ ",
    "T___DAT": "____ __~_ ",
    "A___DAT": "____ __~_ ",

    # INC X
    # 110'.''''.''''.''''
    "X___ADR": "____ _~~~ ____ ",
    "ADR_ALY": "____ _~~~ ____ ",
    "ALU_ADD": "____ _~~~ ____ ",
    "T___CLR": "____ _~__ ____ ",
    "T___ALZ": "____ __~_ ____ ",
    "T___DAT": "____ ____ _~__ ",
    "X___CLR": "____ ____ ~___ ",
    "X___DAT": "____ ____ _~__ ",

    # GOTO
    # 101d.sczn.x'''.''''
    "Z___ADR": "____ _~~~ ____ ", # Z contains P+1, load MEM into M
    "MEM___R": "____ _~~~ ____ ",
    "M___CLR": "____ _~__ ____ ", # M or J
    "M___DAT": "____ __~_ ____ ", # M or J
    "ADR_ALY": "____ _~~~ ____ ",
    "ALU_INC": "____ _~~~ ____ ",
    "T___CLR": "____ _~__ ____ ",
    "T___ALZ": "____ __~_ ____ ", # T contains P+2

    "T___DAT": "____ ____ _~__ ", # MOVE T (P+2) to X via DAT
    "X___CLR": "____ ____ ~___ ", #
    "X___DAT": "____ ____ _~__ ", #

    "J___ADR": "____ ____ _~__ ", # MOVE J to P
    "P___CLR": "____ ____ ~___ ", #
    "P___ADR": "____ ____ _~__ ", #
    #    ^
    # OR |
    #    V
    "T___ADR": "____ ____ _~__ ", # MOVE T (P+2) to P
    "P___CLR": "____ ____ ~___ ", #
    "P___ADR": "____ ____ _~__ ", #

    # HALT
    # 111'.''''.''''.''''
}


def tick(state):
    assert not state["clock"]["halt"]:
    st = dict(state)






def get_bus(state, bus="DATA"):
    s = zeros(BITS)
    # registers
    for rkey in state["registers"]:
        if bus in state["registers"][rkey]["bus"]:
            if state["registers"][rkey]["bus"][bus]:
                s = np.logical_or(s, state["registers"]["bits"])
    if state["memory"]["bus"][bus]:
        s = np.logical_or(s, state["memory"]["bits"])
    return s


def print_state(state, high_symbol="|", low_symbol="."):
    hs = high_symbol
    ls = low_symbol
    s = ""
    # sequencer
    # ---------
    rr = "__sequencer__\n"
    rr += "    "
    seq = None
    for i, b in enumerate(state["clock"]["sequencer"]):
        if i % 4 == 0:
            rr += " "
        if b:
            rr += hs
            seq = i
        else:
            rr += ls
    rr += " "
    if seq:
        rr += "{: 3d}".format(seq)
    else:
        rr += "off"
    rr += "\n"
    s += rr

    # registers
    # ---------
    num_bits = len(state["registers"]["A"]["bits"])
    s += "__registers__" + " "*BITS + "int     uint      hex\n"
    for rkey in state["registers"]:
        rr = " [" + rkey
        rr += "]"
        for i in range(len(state["registers"][rkey]["bits"])):
            b = state["registers"][rkey]["bits"][num_bits - 1 - i]
            if i % 4 == 0:
                rr += " "
            if b:
                rr += hs
            else:
                rr += ls
        # signed integer
        # --------------
        int_val = word_to_int(word=state["registers"][rkey]["bits"])
        rr += "{: 8d} ".format(int_val)
        uint_val = word_to_uint(word=state["registers"][rkey]["bits"])
        rr += "{: 8d} ".format(uint_val)
        hex_val_str = hex(uint_val)[2:]
        rr += "    {:>4s} ".format(hex_val_str)
        rr += "\n"
        s += rr

    # data bus
    print(s)


CLOCK_DAT_FREE = 4  # first clock instruction can use Data-bus
CLOCK_ADR_FREE = 8  # first clock instruction can use Address-bus
CLOCK_INS_START = 4  # first clock for instruction to assert


def MOV_CTRLSEQ(sss=(0, 0, 0), ddd=(0, 0, 1), bus=0):
    regs = {
        (0, 0, 0): "A",
        (0, 0, 1): "B",
        (0, 1, 0): "C",
        (0, 1, 1): "D",
        (1, 0, 0): "X",
        (1, 0, 1): "M",
        (1, 1, 0): "J",
        (1, 1, 1): "P",
    }

    busses = {
        0: "Dat",
        1: "Adr",
    }

    SS_BusSel_ = "{:s}_{:s}Sel".format(regs[sss], busses[bus])
    DD_BusLoa_ = "{:s}_{:s}Loa".format(regs[ddd], busses[bus])

    seq = {
        #            0         1         2         3
        #            0123456789012345678901234567890
        SS_BusSel_: "____~~__",
        DD_BusLoa_: "____~___",
    }
    return ctrlseq_include_fetch_increment(ctrlseq=seq)


def ALU_CTRLSEQ(func=(0, 0, 0), d=0):

    dest = {
        0: "A",
        1: "D",
    }

    DD_DatLoa_ = "{:s}_DatLoa".format(dest[d])

    seq = {
        #            0         1         2         3
        #            0123456789012345678901234567890
        DD_DatLoa_: "_____~__",
        "F_AluSel": "____~~~_",
        "F_AluLoa": "_____~__",
    }
    return ctrlseq_include_fetch_increment(ctrlseq=seq)

def GOTO_CTRLSEQ(d,s,c,z,n,x, state):
    dest = {0: "M", 1: "J"}


def step(state, controls):
    n = dict(state)


def ctrlseq_extent(part_ctrlseq):
    ctrlseq = ctrlseq_extent_controls(part_ctrlseq)
    ctrlseq = ctrlseq_extent_clocks(ctrlseq)
    return ctrlseq


def ctrlseq_extent_controls(part_ctrlseq, all_control):
    out = dict(all_control)
    for key in out:
        out[key] = ""
    for key in part_ctrlseq:
        out[key] = part_ctrlseq[key]
    return out


def ctrlseq_extent_clocks(ctrlseq):
    out = dict(ctrlseq)
    max_len = ctrlseq_max_len(ctrlseq=ctrlseq)
    for key in ctrlseq:
        l = len(ctrlseq[key])
        diff = max_len - l
        ctrlseq[key] += "_" * diff
    return ctrlseq


def ctrlseq_include_fetch_increment(
    ctrlseq, fetch_increment_ctrlseq=FETCH_INCREMENT_CTRLSEQ
):
    fiseq = fetch_increment_ctrlseq
    ctrlseq = ctrlseq_extent(part_ctrlseq=ctrlseq)
    for key in fiseq:
        ctrlseq[key] = fiseq[key] + ctrlseq[key][len(fiseq[key]) :]
    return ctrlseq


def ctrlseq_max_len(ctrlseq):
    lengths = []
    for key in ctrlseq:
        lengths.append(len(ctrlseq[key]))
    return max(lengths)


def seq_str_to_int(seqstr):
    seq = []
    for s in seqstr:
        if s == "_":
            seq.append(0)
        else:
            seq.append(1)
    return seq


def word_to_str(word, sep=".", block=4):
    num_bits = len(word)
    s = ""
    l = 0
    for i in range(num_bits):
        l += 1
        b = word[i]
        assert b == 0 or b == 1
        s += "{:d}".format(b)
        if l % block == 0 and l != num_bits:
            s += "{:s}".format(sep)
    return s


def word_to_uint(word):
    num_bits = len(word)
    dec = 0
    B = int(num_bits)
    for i in range(num_bits):
        b = word[i]
        assert b == 0 or b == 1
        B = 2 ** i
        dec += B * b
    return dec


def word_to_int(word):
    """
    two complement
    """
    MSB = word[-1]
    if MSB:
        sign = 1
    else:
        sign = 0

    sub_word = np.array(word[0:-1])

    if sign:
        val = word_to_uint(word=np.logical_not(sub_word))
        max_val = (2 ** len(sub_word))
        return  val - max_val
    else:
        val = word_to_uint(word=sub_word)
        return val


FUNC = {
    "ADD": (0, 0, 0),
    "INC": (0, 0, 1),
    "AND": (0, 1, 0),
    "OR": (0, 1, 1),
    "XOR": (1, 0, 0),
    "NOT": (1, 0, 1),
    "SHL": (1, 1, 0),
}


def alu(B, C, func=FUNC["ADD"]):
    assert len(B) == len(C)
    width = len(B)
    assert len(func) == 3

    f = tuple(func)

    R = np.zeros(shape=width, dtype=np.int)
    Sum = 0
    Carry = 0

    if f == FUNC["ADD"]:
        c_in = 0
        for i in range(width):
            print(i, R, c_in)
            R[i], c_out = _full_adder(X=B[i], Y=C[i], Carry_in=c_in)
            c_in = int(c_out)
        Carry = c_out

    elif f == FUNC["INC"]:
        c_in = 1
        for i in range(width):
            R[i], c_out = _half_adder(X=B[i], Y=c_in)
            c_in = c_out
        Carry = c_out

    elif f == FUNC["AND"]:
        R = np.logical_and(B, C)
    elif f == FUNC["OR"]:
        R = np.logical_or(B, C)
    elif f == FUNC["XOR"]:
        R = np.logical_xor(B, C)
    elif f == FUNC["NOT"]:
        R = np.logical_not(B)
    elif f == FUNC["SHL"]:
        for b in range(width - 1):
            R[b + 1] = B[b]
        R[0] = B[b + 1]
    else:
        # Not supported
        pass

    Zero = int(np.all(R == 0))

    return R, (Zero, Carry, Sum)


def _full_adder(X, Y, Carry_in):
    S0, C0 = _half_adder(X, Y)
    S1, C1 = _half_adder(S0, Carry_in)
    Carry_out = int(np.logical_or(C0, C1))
    Sum = S1
    return Sum, Carry_out


def _half_adder(X, Y):
    Sum = int(np.logical_xor(X, Y))
    Carry_out = int(np.logical_and(X, Y))
    return Sum, Carry_out
