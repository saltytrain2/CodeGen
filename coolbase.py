from __future__ import annotations
from tacnodes import *

def _build_io_outint() -> TacFunc:
    tacregs = [TacReg(i) for i in range(11)]
    tacfunc = TacFunc("IO.out_int", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacAlloc("Int", tacregs[2]))
    # tacfunc.append(TacAlloc("String", tacregs[4]))
    tacregs[2].isstack = True
    # tacregs[4].isstack = True
    tacfunc.append(TacStoreSelf(tacregs[0], tacregs[3]))
    tacfunc.append(TacStore(tacregs[1], tacregs[2]))

    # create the format string
    tacfunc.append(TacCreate("String", tacregs[4]))
    # tacfunc.append(TacStore(tacregs[5], tacregs[4]))
    # tacfunc.append(TacLoad(tacregs[4], tacregs[6]))
    tacfunc.append(TacLoadImm(TacStr("%d"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[4], 3))
    # tacfunc.append(TacStore(tacregs[6], tacregs[4]))

    # time to print to screen
    tacfunc.append(TacLoad(tacregs[4], tacregs[6], 3))
    tacfunc.append(TacLoad(tacregs[2], tacregs[7]))
    tacfunc.append(TacLoad(tacregs[7], tacregs[8], 3))
    tacfunc.append(TacSyscall("printf@PLT", [tacregs[6], tacregs[8]], tacregs[9]))

    # return
    tacfunc.append(TacRet(tacregs[3]))
    return tacfunc


def _build_io_outstring():
    tacregs = [TacReg(i) for i in range(7)]
    tacfunc = TacFunc("IO.out_string", [tacregs[0], tacregs[1]])

    # store the parameters
    tacfunc.append(TacAlloc("String", tacregs[2]))
    tacregs[2].isstack = True
    # tacregs[3].isstack = True
    tacfunc.append(TacStoreSelf(tacregs[0], tacregs[3]))
    tacfunc.append(TacStore(tacregs[1], tacregs[2]))

    # load the string and print
    tacfunc.append(TacLoad(tacregs[2], tacregs[4]))
    tacfunc.append(TacLoad(tacregs[4], tacregs[5], 3))
    tacfunc.append(TacSyscall("printf@PLT", [tacregs[5]], tacregs[6]))

    # return
    tacfunc.append(TacRet(tacregs[3]))
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
    return """\
\t.text
\t.section\t.rodata
.LCObort:
\t.asciz "abort\n"
\t.text
\t.globl Object.abort
Object.abort:
\tpushq\t%rbp
\tmovq\t.LCObort(%rip), %rdi
\txor\t%eax, %eax
\tcall\tprintf@PLT
\tmovq\tstdout(%rip), %rdi
\txor\t%edi, %edi
\tcall\texit@PLT
\tnop
\tpopq\t%rbp
\tret

    """

def _build_object_typename():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("Object.type_name", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc

def _build_object_copy():
    return """\
\t.text
\t.globl Object.copy
Object.copy:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$8, %rsi
\tpushq\t%rdi
\tsubq\t%rsi, %rsp
\tmovq\t8(%rdi), %rdi
\tcall\tcalloc
\tpopq\t%rdi
\tmovq\t$8, %rsi
\taddq\t%rsi, %rsp
\tmovq\t%rax, %rdx
\tmovq\t8(%rdx), %r9
\tmovq\t%rdx, %rcx
.Lcopy1:
\tmovq\t0(%rdi), %r10
\tmovq\t%r10, 0(%rcx)
\taddq\t%rsi, %rcx
\taddq\t%rsi, %rdi
\tdec\t%r9
\tjz\t.Lcopyend
\tjmp\t.Lcopy1
.Lcopyend:
\tpopq\t%rbp
\tret

"""
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("Object.copy", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_string_concat():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("String.concat", [tacregs[0], tacregs[1], tacregs[2]])

    
    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc


def _build_string_length():
    tacregs = [TacReg(i) for i in range(5)]
    tacfunc = TacFunc("String.length", [tacregs[0]])
    
    tacfunc.append(TacStoreSelf(tacregs[0], tacregs[1]))
    tacfunc.append(TacCreate("Int", tacregs[2]))
    tacfunc.append(TacLoad(tacregs[1], tacregs[3], 3))
    tacfunc.append(TacSyscall("strlen", [tacregs[3]], tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 3))
    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc


def _build_string_substr():
    tacregs = [TacReg(i) for i in range(3)]
    tacfunc = TacFunc("String.substr", [tacregs[0], tacregs[1]])

    zero_reg = tacregs[2]
    tacfunc.append(TacLoadImm(TacImm(0), zero_reg))
    tacfunc.append(TacRet(zero_reg))
    return tacfunc

def _build_io_new():
    tacregs = [TacReg(i) for i in range(7)]
    tacfunc = TacFunc("IO..new", None)

    # tacfunc.append(TacAlloc("IO", tacregs[0]))
    # tacregs[0].isstack = True
    tacfunc.append(TacLoadImm(TacImm(24), tacregs[0]))
    tacfunc.append(TacSyscall("malloc@PLT", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacStoreSelf(tacregs[1], tacregs[2]))

    tacfunc.append(TacLoadImm(TacImm(4), tacregs[3]))
    tacfunc.append(TacStore(tacregs[3], tacregs[2], 0))
    tacfunc.append(TacLoadImm(TacImm(3), tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 1))
    tacfunc.append(TacLoadImm(TacImmLabel("IO..vtable"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[2], 2))

    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

def _build_object_new():
    tacregs = [TacReg(i) for i in range(7)]
    tacfunc = TacFunc("Object..new", None)

    tacfunc.append(TacLoadImm(TacImm(24), tacregs[0]))
    tacfunc.append(TacSyscall("malloc@PLT", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacStoreSelf(tacregs[1], tacregs[2]))

    tacfunc.append(TacLoadImm(TacImm(3), tacregs[3]))
    tacfunc.append(TacStore(tacregs[3], tacregs[2], 0))
    tacfunc.append(TacLoadImm(TacImm(3), tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 1))
    tacfunc.append(TacLoadImm(TacImmLabel("Object..vtable"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[2], 2))

    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

def _build_int_new():
    tacregs = [TacReg(i) for i in range(8)]
    tacfunc = TacFunc("Int..new", None)

    # tacfunc.append(TacAlloc("Int", tacregs[0]))
    # tacregs[0].isstack = True
    tacfunc.append(TacLoadImm(TacImm(32), tacregs[0]))
    tacfunc.append(TacSyscall("malloc@PLT", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacStoreSelf(tacregs[1], tacregs[2]))

    tacfunc.append(TacLoadImm(TacImm(1), tacregs[3]))
    tacfunc.append(TacStore(tacregs[3], tacregs[2], 0))
    tacfunc.append(TacLoadImm(TacImm(4), tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 1))
    tacfunc.append(TacLoadImm(TacImmLabel("Int..vtable"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[2], 2))

    tacfunc.append(TacLoadImm(TacImm(0), tacregs[6]))
    tacfunc.append(TacStore(tacregs[6], tacregs[2], 3))

    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

def _build_string_new():
    tacregs = [TacReg(i) for i in range(8)]
    tacfunc = TacFunc("String..new", None)

    tacfunc.append(TacLoadImm(TacImm(32), tacregs[0]))
    tacfunc.append(TacSyscall("malloc@PLT", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacStoreSelf(tacregs[1], tacregs[2]))

    tacfunc.append(TacLoadImm(TacImm(2), tacregs[3]))
    tacfunc.append(TacStore(tacregs[3], tacregs[2], 0))
    tacfunc.append(TacLoadImm(TacImm(4), tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 1))
    tacfunc.append(TacLoadImm(TacImmLabel("String..vtable"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[2], 2))

    tacfunc.append(TacLoadImm(TacStr(""), tacregs[6]))
    tacfunc.append(TacStore(tacregs[6], tacregs[2], 3))

    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

def _build_bool_new():
    tacregs = [TacReg(i) for i in range(8)]
    tacfunc = TacFunc("Bool..new", None)

    tacfunc.append(TacLoadImm(TacImm(32), tacregs[0]))
    tacfunc.append(TacSyscall("malloc@PLT", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacStoreSelf(tacregs[1], tacregs[2]))

    tacfunc.append(TacLoadImm(TacImm(0), tacregs[3]))
    tacfunc.append(TacStore(tacregs[3], tacregs[2], 0))
    tacfunc.append(TacLoadImm(TacImm(4), tacregs[4]))
    tacfunc.append(TacStore(tacregs[4], tacregs[2], 1))
    tacfunc.append(TacLoadImm(TacImmLabel("Bool..vtable"), tacregs[5]))
    tacfunc.append(TacStore(tacregs[5], tacregs[2], 2))

    tacfunc.append(TacLoadImm(TacImm(0), tacregs[6]))
    tacfunc.append(TacStore(tacregs[6], tacregs[2], 3))

    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

def _build_main():
    tacregs = [TacReg(i) for i in range(8)]
    tacfunc = TacFunc("main", None)

    tacfunc.append(TacCreate("Main", tacregs[0]))
    tacfunc.append(TacCall("Main.main", [tacregs[0]], tacregs[1]))
    tacfunc.append(TacLoadImm(TacImm(0), tacregs[2]))
    tacfunc.append(TacRet(tacregs[2]))
    return tacfunc

IO_FUNCS:List[TacFunc] = [
    _build_io_inint(),
    _build_io_instring(),
    _build_io_outint(),
    _build_io_outstring(),
    _build_io_new()
]

OBJECT_FUNCS:List[TacFunc] = [
    _build_object_abort(),
    _build_object_copy(),
    _build_object_typename(),
    _build_object_new()
]

INT_FUNCS:List[TacFunc] = [_build_int_new()]

BOOL_FUNCS:List[TacFunc] = [_build_bool_new()]

STRING_FUNCS:List[TacFunc] = [
    _build_string_concat(),
    _build_string_length(),
    _build_string_substr(),
    _build_string_new()
]

MAIN_METHOD = _build_main()


BASE_CLASS_METHODS:Dict[str, List[TacFunc]] = {
    "IO" : IO_FUNCS,
    "Object" : OBJECT_FUNCS,
    "Int" : INT_FUNCS,
    "String" : STRING_FUNCS,
    "Bool" : BOOL_FUNCS
}

# def _build_x86_io_outint() -> str:
#     return """\
#     \t.text
#     \t.section\t.rodata
#     .LBI1:
#     \t.asciz "%d"
#     \t.text
#     \t.globl IO.out_int
#     IO.out_int:
#     \tpushq\t%rbp
#     \tmovq\t%rsp, %rbp
#     \tsubq\t$16, %rsp
#     \tmovq\t%rsi, 0(%rbp)
#     \tmovq\t%
#     """
    
#     pass

# def _build_x86_bool_new() -> str:
#     return """\
#     \t.text
#     \t.globl Bool..new
#     Bool..new:
#     \tpushq\t%rbp
#     \tmovq\t%rsp, %rbp
#     \tmovq\t$32, %rdi
#     \tmovq
#     """

def _build_eq_helper() -> str:
    return """\
\t.text
\t.globl eq_helper
eq_helper:
\tpushq\t%rbp
\tcmpq\t%rdi, %rsi
\tje\teq_true
\txor\t%r15, %r15
\tcmpq\t%rsi, %r15
\tje\teq_false
\tcmpq\t%rdi, %r15
\tje\teq_false
\tmovq\t0(%rdi), %r14
\tmovq\t0(%rsi), %r13
\taddq\t%r14, %r13
\tcmpq\t%r13, %r15
\tje\teq_bool
\tmovq\t$2, %r15
\tcmpq\t%r13, %r15
\tje\teq_int
\tmovq\t$4, %r15
\tcmpq\t%r13, %r15
\tje\teq_string
\tcmp\t%rsi, %rdi
\tje\teq_true
eq_false:
\tcall\tBool..new
\tjmp\teq_end
eq_true:
\tcall\tBool..new
\tmovq\t$1, %r15
\tmovq\t%r15, 24(%rax)
\tjmp\teq_end
eq_bool:
eq_int:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcmpq\t%rdi, %rsi
\tje\teq_true
\tjmp\teq_false
eq_string:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcall\tstrcmp
\tcmp\t$0, %eax
\tje\teq_true
\tjmp\teq_false
eq_end:
\tpopq\t%rbp
\tret

    """

def _build_lt_helper() -> str:
    return """\
\t.text
\t.globl lt_helper
lt_helper:
\tpushq\t%rbp
\txor\t%r15, %r15
\tcmpq\t%rsi, %r15
\tje\tlt_false
\tcmpq\t%rdi, %r15
\tje\tlt_false
\tmovq\t0(%rdi), %r14
\tmovq\t0(%rsi), %r13
\taddq\t%r14, %r13
\tcmpq\t%r13, %r15
\tje\tlt_bool
\tmovq\t$2, %r15
\tcmpq\t%r13, %r15
\tje\tlt_int
\tmovq\t$4, %r15
\tcmpq\t%r13, %r15
\tje\tlt_string
lt_false:
\tcall\tBool..new
\tjmp\tlt_end
lt_true:
\tcall\tBool..new
\tmovq\t$1, %r15
\tmovq\t%r15, 24(%rax)
\tjmp\teq_end
lt_bool:
lt_int:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcmpl\t%edi, %esi
\tjl\tlt_true
\tjmp\tlt_false
lt_string:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcall\tstrcmp
\tcmp\t$0, %eax
\tjl\tlt_true
\tjmp\tlt_false
lt_end:
\tpopq\t%rbp
\tret

    """

def _build_le_helper() -> str:
    return """\
\t.text
\t.globl le_helper
le_helper:
\tpushq\t%rbp
\tcmpq\t%rdi, %rsi
\tje\tle_true
\txor\t%r15, %r15
\tcmpq\t%rsi, %r15
\tje\tle_false
\tcmpq\t%rdi, %r15
\tje\tle_false
\tmovq\t0(%rdi), %r14
\tmovq\t0(%rsi), %r13
\taddq\t%r14, %r13
\tcmpq\t%r13, %r15
\tje\tle_bool
\tmovq\t$2, %r15
\tcmpq\t%r13, %r15
\tje\tle_int
\tmovq\t$4, %r15
\tcmpq\t%r13, %r15
\tje\tle_string
\tcmp\t%rsi, %rdi
\tje\teq_true
le_false:
\tcall\tBool..new
\tjmp\tle_end
le_true:
\tcall\tBool..new
\tmovq\t$1, %r15
\tmovq\t%r15, 24(%rax)
\tjmp\tle_end
le_bool:
le_int:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcmpl\t%edi, %esi
\tjle\tle_true
\tjmp\tle_false
le_string:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcall\tstrcmp
\tcmp\t$0, %eax
\tjle\tle_true
\tjmp\tle_false
le_end:
\tpopq\t%rbp
\tret

    """

HELPERS = [_build_lt_helper(), _build_le_helper(), _build_eq_helper()]