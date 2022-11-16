from __future__ import annotations
from tacnodes import *

def _build_io_outint() -> TacFunc:
    tacregs = [TacReg(i) for i in range(11)]
    tacfunc = TacFunc("IO.out_int", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacAlloc("SELF_TYPE", tacregs[2]))
    tacfunc.append(TacAlloc("Int", tacregs[3]))
    tacfunc.append(TacAlloc("String", tacregs[4]))
    tacregs[2].isstack = True
    tacregs[3].isstack = True
    tacregs[4].isstack = True
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # create the format string
    tacfunc.append(TacCreate("String", tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[4]))
    tacfunc.append(TacLoad(tacregs[4], tacregs[6]))
    tacfunc.append(TacLoadImm(TacStr("%d"), tacregs[7]))
    tacfunc.append(TacStore(tacregs[7], tacregs[6], 3))
    tacfunc.append(TacStore(tacregs[6], tacregs[4]))

    # time to print to screen
    tacfunc.append(TacLoad(tacregs[4], tacregs[8], 3))
    tacfunc.append(TacLoad(tacregs[3], tacregs[9], 3))
    tacfunc.append(TacSyscall("printf@PLT", [tacregs[8], tacregs[9]], tacregs[10]))

    # return
    tacfunc.append(TacLoad(tacregs[2], tacregs[9]))
    tacfunc.append(TacRet(tacregs[9]))
    
    return tacfunc


def _build_io_outstring():
    tacregs = [TacReg(i) for i in range(7)]
    tacfunc = TacFunc("IO.out_string", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacAlloc("SELF_TYPE", tacregs[2]))
    tacfunc.append(TacAlloc("String", tacregs[3]))
    tacregs[2].isstack = True
    tacregs[3].isstack = True
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # load the string and print
    tacfunc.append(TacLoad(tacregs[3], tacregs[4], 3))
    tacfunc.append(TacSyscall("printf@PLT", [tacregs[4]], tacregs[5]))

    # return
    tacfunc.append(TacLoad(tacregs[2], tacregs[6]))
    tacfunc.append(TacRet(tacregs[6]))
    
    return tacfunc


def _build_io_inint():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("IO.in_int", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_io_instring():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc

def _build_object_abort():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("Object.abort", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc

def _build_object_typename():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("Object.type_name", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc

def _build_object_copy():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("Object.copy", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_string_concat():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("String.concat", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_string_length():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("String.length", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_string_substr():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("String.substr", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


IO_FUNCS:List[TacFunc] = [
    _build_io_inint(),
    _build_io_instring(),
    _build_io_outint(),
    _build_io_outstring()
]

OBJECT_FUNCS:List[TacFunc] = [
    _build_object_abort(),
    _build_object_copy(),
    _build_object_typename()
]

INT_FUNCS:List[TacFunc] = []

BOOL_FUNCS:List[TacFunc] = []

STRING_FUNCS:List[TacFunc] = [
    _build_string_concat(),
    _build_string_length(),
    _build_string_substr(),
]


BASE_CLASS_METHODS:Dict[str, List[TacFunc]] = {
    "IO" : IO_FUNCS,
    "Object" : OBJECT_FUNCS,
    "Int" : INT_FUNCS,
    "String" : STRING_FUNCS,
    "Bool" : BOOL_FUNCS
}