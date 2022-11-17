from __future__ import annotations
from tacnodes import *

def _build_io_outint() -> TacFunc:
    return """\
\t.text
\t.section\t.rodata
.LIOINT:
\t.asciz "%ld"
\t.text
\t.globl IO.out_int
IO.out_int:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t24(%rsi), %rsi
\tmovq\t$8, %rcx
\tpushq\t%rdi
\tsubq\t%rcx, %rsp
\tmovq\t.LIOINT(%rip), %rdi
\tcall\tprintf@PLT
\tmovq\t$8, %rcx
\taddq\t%rcx, %rsp
\tpopq\t%rax
\tpopq\t%rbp
\tret
"""

def _build_io_outstring():
    return """\
\t.text
\t.globl IO.out_string
IO.out_string:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tpushq\t%rdi
\tmovq\t24(%rdi), %rdi
\tmovq\t$8, %rcx
\tsubq\t%rcx, %rsp
\tcall\tprintf@PLT
\tmovq\t$8, %rcx
\taddq\t%rcx, %rsp
\tpopq\t%rax
\tpopq\t%rbp
\tret

    """


def _build_io_inint():
    return """\
\t.text
\t.globl IO.in_int
IO.in_int:
\txor %eax, %eax
\tret

    """


def _build_io_instring():
    return """\
\t.text
\t.globl IO.in_string
IO.in_string:
\txor %eax, %eax
\tret
    
    """

def _build_object_abort():
    return """\
\t.text
\t.section\t.rodata
.LCObort:
\t.asciz "abort\\n"
\t.text
\t.globl Object.abort
Object.abort:
\tpushq\t%rbp
\tmovq\t.LCObort(%rip), %rdi
\txor\t%eax, %eax
\tcall\tprintf@PLT
\txor\t%edi, %edi
\tcall\texit@PLT
\tnop
\tpopq\t%rbp
\tret

    """

def _build_object_typename():
    return """\
\t.text
\t.globl Object.type_name
Object.type_name:
\tpushq\t%rbp
\tpushq\t%rdi
\tmovq\t$8, %rcx
\tsubq\t%rcx, %rsp
\tcall\tString..new
\tmovq\t$8, %rcx
\taddq\t%rcx, %rsp
\tpopq\t%rdi
\tmovq\t16(%rdi), %r8
\tmovq\t0(%r8), %r8
\tmovq\t%r8, 24(%rax)
\tpopq\t%rbp
\tret

"""

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


def _build_string_concat():
    return """\
\t.text
\t.globl String.concat
String.concat:
\txor %eax, %eax
\tret

    """


def _build_string_length():
    return """\
\t.text
\t.globl String.length
String.length:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tpushq\t%rdi
\tmovq\t$8, %rcx
\tsubq\t%rcx, %rsp
\tcall\tInt..new
\tmovq\t$8, %rcx
\taddq\t%rcx, %rsp
\tpopq\t%rsi
\tmovq\t%rax, %r9
\tmovq\t24(%rsi), %rdi
\txor\t%eax, %eax
\trepne\tscasb
\tmovq\t24(%rsi), %rsi
\tsubq\t%rsi, %rdi
\tmovq\t%rdi, 24(%r9)
\tmovq\t%r9, %rax
\tpopq\t%rbp
\tret

    """


def _build_string_substr():
    return """\
\t.text
\t.globl String.substr
String.substr:
\txor %eax, %eax
\tret

    """

def _build_io_new():
    return """\
\t.text
\t.globl IO..new
IO..new:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$24, %rdi
\tcall\tmalloc@PLT
\tmovq\t$4, %rdi
\tmovq\t%rdi, 0(%rax)
\tdec\t%rdi
\tmovq\t%rdi, 8(%rax)
\tmovq\tIO..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tpopq\t%rbp
\tret
    """

def _build_object_new():
    return """\
\t.text
\t.globl Object..new
Object..new:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$24, %rdi
\tcall\tmalloc@PLT
\tmovq\t$3, %rdi
\tmovq\t%rdi, 0(%rax)
\tmovq\t%rdi, 8(%rax)
\tmovq\tObject..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tpopq\t%rbp
\tret

    """

def _build_int_new():
    return """\
\t.text
\t.globl Int..new
Int..new:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$32, %rdi
\tcall\tmalloc@PLT
\tmovq\t$1, %rdi
\tmovq\t%rdi, 0(%rax)
\tmovq\t$4, %rdi
\tmovq\t%rdi, 8(%rax)
\tmovq\tInt..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\txor\t%edi, %edi
\tmovq\t%rdi, 24(%rax)
\tpopq\t%rbp
\tret

    """

def _build_string_new():
    return """\
\t.text
\t.section\t.rodata
.LStringNew:
\t.asciz ""
\t.text
\t.globl String..new
String..new:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$32, %rdi
\tcall\tmalloc@PLT
\tmovq\t$2, %rdi
\tmovq\t%rdi, 0(%rax)
\tmovq\t$4, %rdi
\tmovq\t%rdi, 8(%rax)
\tmovq\tString..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tmovq\t.LStringNew(%rip), %rdi
\tmovq\t%rdi, 24(%rax)
\tpopq\t%rbp
\tret

    """

def _build_bool_new():
    return """\
\t.text
\t.globl Bool..new
Bool..new:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t$32, %rdi
\tcall\tmalloc@PLT
\txor\t%edi, %edi
\tmovq\t%rdi, 0(%rax)
\tmovq\t$4, %rdi
\tmovq\t%rdi, 8(%rax)
\tmovq\tBool..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\txor\t%edi, %edi
\tmovq\t%rdi, 24(%rax)
\tpopq\t%rbp
\tret

    """

def _build_main():
    return """\
\t.text
\t.globl main
main:
\tcall\tMain..new
\tmovq\t%rax, %rdi
\tcall\tMain.main
\txor\t%edi, %edi
\tcall\texit
\tnop
\tret

    """

def _build_eq_helper() -> str:
    return """\
\t.text
\t.globl eq_helper
eq_helper:
\tpushq\t%rbp
\tcmpq\t%rdi, %rsi
\tje\teq_true
\txor\t%rcx, %rcx
\tcmpq\t%rsi, %rcx
\tje\teq_false
\tcmpq\t%rdi, %rcx
\tje\teq_false
\tmovq\t0(%rdi), %r8
\tmovq\t0(%rsi), %r9
\taddq\t%r8, %r9
\tcmpq\t%r9, %rcx
\tje\teq_bool
\tmovq\t$2, %rcx
\tcmpq\t%r9, %rcx
\tje\teq_int
\tmovq\t$4, %rcx
\tcmpq\t%r9, %rcx
\tje\teq_string
\tcmp\t%rsi, %rdi
\tje\teq_true
eq_false:
\tcall\tBool..new
\tjmp\teq_end
eq_true:
\tcall\tBool..new
\tmovq\t$1, %rcx
\tmovq\t%rcx, 24(%rax)
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
\txor\t%rcx, %rcx
\tcmpq\t%rsi, %rcx
\tje\tlt_false
\tcmpq\t%rdi, %rcx
\tje\tlt_false
\tmovq\t0(%rdi), %r8
\tmovq\t0(%rsi), %r9
\taddq\t%r8, %r9
\tcmpq\t%r9, %rcx
\tje\tlt_bool
\tmovq\t$2, %rcx
\tcmpq\t%r9, %rcx
\tje\tlt_int
\tmovq\t$4, %rcx
\tcmpq\t%r9, %rcx
\tje\tlt_string
lt_false:
\tcall\tBool..new
\tjmp\tlt_end
lt_true:
\tcall\tBool..new
\tmovq\t$1, %rcx
\tmovq\t%rcx, 24(%rax)
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
\txor\t%rcx, %rcx
\tcmpq\t%rsi, %rcx
\tje\tle_false
\tcmpq\t%rdi, %rcx
\tje\tle_false
\tmovq\t0(%rdi), %r8
\tmovq\t0(%rsi), %r9
\taddq\t%r8, %r9
\tcmpq\t%r9, %rcx
\tje\tle_bool
\tmovq\t$2, %rcx
\tcmpq\t%r9, %rcx
\tje\tle_int
\tmovq\t$4, %rcx
\tcmpq\t%r9, %rcx
\tje\tle_string
\tcmp\t%rsi, %rdi
\tje\teq_true
le_false:
\tcall\tBool..new
\tjmp\tle_end
le_true:
\tcall\tBool..new
\tmovq\t$1, %rcx
\tmovq\t%rcx, 24(%rax)
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

HELPERS = [
    _build_io_outint(),
    _build_io_outstring(),
    _build_io_inint(),
    _build_io_instring(),
    _build_object_abort(),
    _build_object_copy(),
    _build_object_typename(),
    _build_string_concat(),
    _build_string_length(),
    _build_string_substr(),
    _build_bool_new(),
    _build_io_new(),
    _build_int_new(),
    _build_object_new(),
    _build_string_new(),
    _build_eq_helper(),
    _build_lt_helper(),
    _build_le_helper(), 
    _build_main()
]