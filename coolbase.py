from __future__ import annotations
from tacnodes import *

def _build_io_outint() -> TacFunc:
    tacregs = [TacReg(i) for i in range(10)]
    tacfunc = TacFunc("IO.out_int", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacDeclare("SELF_TYPE", tacregs[2]))
    tacregs[2].isstack = True
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacDeclare("Int", tacregs[3]))
    tacregs[3].isstack = True
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # create the format string
    tacfunc.append(TacDeclare("String", tacregs[4]))
    tacregs[4].isstack = True
    tacfunc.append(TacCreate("String", tacregs[5]))
    tacfunc.append(TacStore(TacStr("%d"), tacregs[5], 3))
    tacfunc.append(TacStore(tacregs[5], tacregs[4]))

    # time to print to screen
    tacfunc.append(TacLoad(tacregs[4], tacregs[6], 3))
    tacfunc.append(TacLoad(tacregs[3], tacregs[7], 3))
    tacfunc.append(TacCall("printf@PLT", [tacregs[6], tacregs[7]], tacregs[8]))

    # return
    tacfunc.append(TacLoad(tacregs[2], tacregs[9]))
    tacfunc.append(TacRet(tacregs[9]))
    
    return tacfunc


def _build_io_outstring():
    tacregs = [TacReg(i) for i in range(7)]
    tacfunc = TacFunc("IO.out_string", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacDeclare("SELF_TYPE", tacregs[2]))
    tacregs[2].isstack = True
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacDeclare("String", tacregs[3]))
    tacregs[3].isstack = True
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # load the string and print
    tacfunc.append(TacLoad(tacregs[3], tacregs[4], 3))
    tacfunc.append(TacCall("printf@PLT", [tacregs[4]], tacregs[5]))

    # return
    tacfunc.append(TacLoad(tacregs[2], tacregs[6]))
    tacfunc.append(TacRet(tacregs[6]))
    
    return tacfunc


def _build_io_inint():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_int", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc


def _build_io_instring():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc

def _build_object_abort():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc

def _build_object_typename():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc

def _build_object_copy():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc


def _build_string_concat():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc


def _build_string_length():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
    return tacfunc


def _build_string_substr():
    tacregs = [TacReg(i) for i in range(2)]
    tacfunc = TacFunc("IO.in_string", [tacregs[0], tacregs[1]])

    tacfunc.append(TacRet(TacImm(0)))
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