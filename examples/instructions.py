import numpy as np
import io

def zeros(shape):
    return np.zeros(shape=shape, dtype=np.uint8)


BITS = 16

state = {
    "registers": {
        "ALX": {"reg": "...", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "ALY": {"reg": "...", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "ALZ": {"reg": "...", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "ALZ": 0}},

        "A__": {"reg": "000", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "SH1": 0}},
        "B__": {"reg": "001", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "SH2": 0}},
        "C__": {"reg": "010", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "SH1": 0}},
        "D__": {"reg": "011", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0, "SH2": 0}},

        "M__": {"reg": "100", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "X__": {"reg": "101", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "J__": {"reg": "110", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},
        "P__": {"reg": "111", "bits": zeros(BITS), "bus": {"DAT": 0, "ADR": 0}},

        "I__": {"reg": "...", "bits": zeros(BITS), "bus": {"DAT": 0,}},
        "MMA": {"reg": "...", "bits": zeros(BITS), "bus": {"ADR": 0,}},
        "MMD": {"reg": "...", "bits": zeros(BITS), "bus": {"DAT": 0,}},
    },
    "alu": {"flags": {"sign": 0, "carry": 0, "zero": 0}, "bits": zeros(BITS),},
    "memory": {
        "bits": zeros(shape=(512, BITS)),
    },
    "clock": {
        "halt": 1,
        "sequencer": zeros(24),
    },
}

ALU_FFF = {
    "NOTX": "0000",
    "AND_": "0001",
    "NAND": "0010",
    "OR__": "0011",

    "NOR_": "0100",
    "XNOR": "0110",
    "INCX": "0111",
    "ADD_": "1010",

    "-y*_": "1001",
    "X-1_": "1000",
    "X-Y_": "1011",

    "SLx_": "1100",
    "SRx_": "1101",
    "SCLx": "1110",
    "SCRx": "1111",
}

FETCH_INCREMENT_CTRLSEQ = {
    #            0000 0000 0011 1111 1111 2222
    #            0123 4567 8901 2345 6789 0123
    "ALY_CLR": " ~___ ____ ", # Copy P into ALY and MMA
    "MMA_CLR": " ~___ ____ ",
    "P___ADR": " _~__ ____ ",
    "ALY_ADR": " _~__ ____ ",
    "MMA_ADR": " _~__ ____ ",
    "MEM___R": " _~~~ ____ ", # Fetch
    "I___CLR": " __~_ ____ ",
    "MMD_DAT": " ___~ ____ ",
    "I___DAT": " ___~ ____ ",
    "ALU_INC": " _~~~ ____ ", # increment
    "ALZ_CLR": " _~__ ____ ", # save P+1 in ALZ
    "ALZ_ALZ": " __~_ ____ ",
    "P___CLR": " __~_ ____ ", # Copy P+1 into P
    "ALZ_ADR": " ___~ ____ ",
    "P___ADR": " ___~ ____ ",

    "I___INT": " ___~ ~~~~ ",

    # COPY-DAT ALZ B
    # 0000.ddds.ss--.----
    "B___CLR": "____ ~___ ",
    "B___DAT": "____ _~__ ",
    "ALZ_DAT": "____ _~__ ",
    "C___CLR": "____ ~___ ",
    "C___DAT": "____ _~__ ",
    "M___DAT": "____ _~__ ",

    # SET B C
    # 0001.dvvv.vvvv.vvvv
    "B___CLR": "____ ~___ ",
    "B___VVV": "____ _~~~ ",

    # MEM READ A
    # 0010.dd''.''''.''''
    "MMA_CLR": " ____ ~___ ", # Copy M into MEM-ADR-register
    "M___ADR": " ____ _~__ ",
    "MMA_ADR": " ____ _~__ ",
    "MEM____": " ____ __~~ ", # Fetch
    "A___CLR": " ____ __~_ ",
    "MMD_DAT": " ____ ___~ ", # Copy MEM-DAT into destination (A)
    "A___DAT": " ____ ___~ ",

    # MEM WRITE A
    # 0011.''''.''''.'ddd
    "MMA_CLR": " ____ ~___ ", # Copy M into MEM-ADR-register
    "M___ADR": " ____ _~__ ",
    "MMA_ADR": " ____ _~__ ",
    "MMD_CLR": " ____ ~___ ",
    "A___DAT": " ____ _~__ ",
    "MMD_DAT": " ____ _~__ ",
    "MEM___W": " ____ __~~ ",

    # ALU
    # 0100.xxyy.zzZ'.ffff
    # 0100.bbcc.dd1'.ffff
    # If 'Z' == 0, do not copy output to zz. Use for example to test: A == B
    # D = B + C
    "ALX_CLR": "____ ~___ ", # Copy B into ALX via DAT
    "B___DAT": "____ _~__ ",
    "ALX_DAT": "____ _~__ ",
    "ALY_CLR": "____ ~___ ", # Copy C into ALY via ADR
    "C___ADR": "____ _~__ ",
    "ALY_ADR": "____ _~__ ",
    "ALU_FFF": "____ _~~~ ",
    "ALZ_CLR": "____ _~__ ",
    "ALZ_ALZ": "____ __~_ ", # Result in ALZ
    "D___CLR": "____ __~_ ",
    "ALZ_DAT": "____ ___~ ", # Copy ALZ into D via DAT
    "D___DAT": "____ ___~ ",

    # GOTO
    # 0110.''''.''''.sczn
    "ALY_CLR": " ____ ~___ ", # Copy P+1 into ALY and MMA
    "MMA_CLR": " ____ ~___ ",
    "P___ADR": " ____ _~__ ",
    "ALY_ADR": " ____ _~__ ",
    "MMA_ADR": " ____ _~__ ",
    "MEM___R": " ____ _~~~ ", # Fetch
    "J___CLR": " ____ __~_ ", # M or J
    "MMD_DAT": " ____ ___~ ",
    "J___DAT": " ____ ___~ ", # M or J
    "ALU_INC": " ____ _~~~ ", # increment
    "ALZ_CLR": " ____ _~__ ", # save P+2 in ALZ
    "ALZ_ALZ": " ____ __~_ ",
    "ALZ_ADR": " ____ ___~ ",

    "X___CLR": " ____ __~_ ", # Copy P+2 into X
    "X___ADR": " ____ ___~ ",

    "P___CLR": " ____ __~_ ", # Copy P+2 into P (optional)
    "P___ADR": " ____ ___~ ",
    #    ^
    # OR |
    #    V
    "P___CLR": " ____ __~_ ", # Copy J into P
    "P___DAT": " ____ ___~ ",
    "J___DAT": " ____ ___~ ",

    # INC X
    # 0111.''''.''''.''''
    "ALX_CLR": "____ ~___ ", # Copy X into ALX via ADR
    "X___ADR": "____ _~__ ",
    "ALX_ADR": "____ _~__ ",
    "ALU_INC": "____ _~~~ ", # INC
    "ALZ_CLR": "____ _~__ ",
    "ALZ_ALZ": "____ __~_ ", # Result in ALZ
    "X___CLR": "____ __~_ ",
    "ALZ_ADR": "____ ___~ ", # COPY ALZ into X
    "X___ADR": "____ ___~ ",


    # SHR AB (for multiplication and division)
    # 1000.cr''.''''.''''
    # if 'c', cyclic
    # if 'r': shift-right CD <- AB
    # else:   shift-left  AB <- CD
    "C___CLR": "____ ~___ ", # Copy-shift-left A <- C and B <- D
    "D___CLR": "____ ~___ ",
    # OR
    "A___CLR": "____ ~___ ", # Copy-shift-right C <- A and D <- B
    "B___CLR": "____ ~___ ",

    "A___SH1": "____ _~__ ",
    "C___SH1": "____ _~__ ",
    "B___SH2": "____ _~__ ",
    "D___SH2": "____ _~__ ",

    "A___CLR": "____ __~_ ",
    "B___CLR": "____ __~_ ",
    # OR
    "C___CLR": "____ __~_ ",
    "D___CLR": "____ __~_ ",

    "A___DAT": "____ ___~ ",
    "C___DAT": "____ ___~ ",
    "B___ADR": "____ ___~ ",
    "D___ADR": "____ ___~ ",

    # MUL
    # 1001.
    "ALY_CLR": "____ ~___ ", # COPY ALY <- A
    "ALY_DAT": "____ _~__ ",
    "A___DAT": "____ _~__ ",
    # if B_LSB
    "ALU ADD": "____ _~~~ ",
    "ALZ CLR": "____ _~__ ",
    "ALZ ALZ": "____ __~_ ",
    "A___CLR": "____ __~_ ",
    "ALZ DAT": "____ ___~ ",
    "A___DAT": "____ ___~ ",

    # HALT
    # 1111.''''.''''.''''
}


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
    num_bits = len(state["registers"]["ALZ"]["bits"])
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

    print("__memory__")
    print(print_memory(mem=state["memory"]["bits"]))


def print_memory(mem, num_words_in_row = 16):
    num_words, num_bits = mem.shape
    ss = io.StringIO()
    for iword in range(num_words):
        if iword == 0:
            ss.write("{:4d} | ".format(iword + 1))
        word = word_to_uint(mem[iword, :])
        word_str = "{:04x}".format(word)
        ss.write(word_str)
        if iword > 0 and (iword + 1) % num_words_in_row == 0:
            ss.write("\n")
            ss.write("{:4d} | ".format(iword + 1))
        else:
            ss.write(" ")
    ss.seek(0)
    return ss.read()


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
