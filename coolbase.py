from __future__ import annotations
from tacnodes import *

# BASE_FUNCS = {
#     "IO.out_int" : """
#     \t.text
#     \t.globl IO.out_int
#     IO.out_int:
#     \tpushq\t%rbp
#     \tmovq\t%rsp, %rbp
#     \tsubq\t$24, %rsp
#     \tmovq\t%rdi, -8(%rbp)
#     \tmovq\t%rsi, -16(%rbp)
#     \tleaq\t.LC0(%rip), %rdi
#     \txor\t%eax, %eax
#     \tcall\tprintf
#     \tmovq\t-8(%rbp), %rdi
#     \tmovq\t-16(%rbp), %rsi
#     \tmovq\t%rbp, %rsp
#     \tpopq\t%rbp
#     \tret
#     """,
#     "IO.out_string" : """
#     \t.text
#     \t.globl IO.out_string
#     IO.out_string:
#     \tpushq\t%rbp
#     \tmovq\t%rsp, %rbp
#     \tsubq\t$24, %rsp
#     \tmovq\t%rdi, -8(%rbp)
#     """
# }

def _build_io_outint() -> TacFunc:
    tacregs = [TacReg(i) for i in range(10)]
    tacfunc = TacFunc("IO.out_int", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacDeclare("SELF_TYPE", tacregs[2]))
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacDeclare("Int", tacregs[3]))
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # create the format string
    tacfunc.append(TacDeclare("String", tacregs[4]))
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
    tacregs = [TacReg(i) for i in range(100)]
    tacfunc = TacFunc("IO.out_string", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacDeclare("SELF_TYPE", tacregs[2]))
    tacfunc.append(TacStore(tacregs[0], tacregs[2]))
    tacfunc.append(TacDeclare("String", tacregs[3]))
    tacfunc.append(TacStore(tacregs[1], tacregs[3]))

    # load the string and print
    tacfunc.append(TacLoad(tacregs[3], tacregs[4], 3))
    tacfunc.append(TacCall("printf@PLT", [tacregs[4]], tacregs[5]))

    # return
    tacfunc.append(TacLoad(tacregs[2], tacregs[6]))
    tacfunc.append(TacRet(tacregs[6]))
    
    return tacfunc


IO_FUNCS:List[TacFunc] = [
    _build_io_outint(),
    _build_io_outstring()
    # _build_io_inint()
    # _build_io_instr()
]

OBJECT_FUNCS:List[TacFunc] = [
    # _build_io_outint()
    # _build_io_outstring()
    # _build_io_inint()
    # _build_io_outint()
]

INT_FUNCS:List[TacFunc] = [
    # _build_io_outint()
    # _build_io_outstring()
    # _build_io_inint()
    # _build_io_outint()
]

BOOL_FUNCS:List[TacFunc] = [
    # _build_io_outint()
    # _build_io_outstring()
    # _build_io_inint()
    # _build_io_outint()
]

STRING_FUNCS:List[TacFunc] = [
    # _build_io_outint()
    # _build_io_outstring()
    # _build_io_inint()
    # _build_io_outint()
]


BASE_CLASS_METHODS:Dict[str, List[TacFunc]] = {
    "IO" : IO_FUNCS,
    "Object" : OBJECT_FUNCS,
    "Int" : INT_FUNCS,
    "String" : STRING_FUNCS,
    "Bool" : BOOL_FUNCS
}