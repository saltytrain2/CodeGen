from __future__ import annotations
from tacnodes import *

def _build_io_outint() -> TacFunc:
    return """\
\t.text
\t.section\t.rodata
.LIOINT:
\t.asciz "%d"
\t.text
\t.globl IO.out_int
IO.out_int:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t24(%rsi), %rsi
\tpushq\t%rdi
\tsubq\t$8, %rsp
\tleaq\t.LIOINT(%rip), %rdi
\txor\t%eax, %eax
\tcall\tprintf@PLT
\taddq\t$8, %rsp
\tpopq\t%rax
\tmovq\t%rbp, %rsp
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
\tmovq\t24(%rsi), %rdi
\tsubq\t$8, %rsp
\tcall\tcooloutstr
\taddq\t$8, %rsp
\tpopq\t%rax
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """


def _build_io_inint():
    return """\
\t.text
\t.section\t.rodata
.LCIOININT:
\t.asciz " %ld"
\t.text
\t.globl IO.in_int
IO.in_int:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tpushq\t%rdi
\tsubq\t$8, %rsp
\tcall\tInt..new
\taddq\t$8, %rsp
\tpushq\t%rax
\tmovq\t$1, %rsi
\tmovq\t$4096, %rdi
\tcall\tcalloc
\tmovq\t%rax, %rdi
\tmovq\t$4096, %rsi
\tmovq\tstdin(%rip), %rdx
\tcall\tfgets
\tmovq\t%rax, %rdi
\tcmpq\t$0, %rdi
\tje\t.LIEND
\tleaq\t.LCIOININT(%rip), %rsi
\tsubq\t$16, %rsp
\tmovq\t%rsp, %rdx
\txor\t%eax, %eax
\tcall\tsscanf
\tpopq\t%rdi
\taddq\t$8, %rsp
\tmovq\t$0, %rsi
\tcmpq\t$2147483647, %rdi
\tcmovg\t%rsi, %rdi
\tcmpq\t$-2147483648, %rdi
\tcmovl\t%rsi, %rdi
.LIEND:
\tpopq\t%rax
\tpopq\t%rdx
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """


def _build_io_instring():
    return """\
\t.text
\t.globl IO.in_string
IO.in_string:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tcall\tcoolgetstr
\tpushq\t%rax
\tsubq\t$8, %rsp
\tcall\tString..new
\taddq\t$8, %rsp
\tpopq\t%rdi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
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
\tmovq\t%rsp, %rbp
\tleaq\t.LCObort(%rip), %rdi
\txor\t%eax, %eax
\tcall\tprintf@PLT
\txor\t%edi, %edi
\tcall\texit@PLT
\tnop
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """

def _build_object_typename():
    return """\
\t.text
\t.globl Object.type_name
Object.type_name:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tpushq\t%rdi
\tsubq\t$8, %rsp
\tcall\tString..new
\taddq\t$8, %rsp
\tpopq\t%rdi
\tmovq\t16(%rdi), %r8
\tmovq\t0(%r8), %r8
\tmovq\t%r8, 24(%rax)
\tmovq\t%rbp, %rsp
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
\tmovq\t$8, %rsi
\taddq\t%rsi, %rsp
\tpopq\t%rdi
\tmovq\t%rax, %rdx
\tmovq\t8(%rdi), %r9
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
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """


def _build_string_concat():
    return """\
\t.text
\t.globl String.concat
String.concat:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcall\tcoolstrcat
\tpushq\t%rax
\tsubq\t$8, %rsp
\tcall\tString..new
\taddq\t$8, %rsp
\tpopq\t%rdi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """


def _build_string_length():
    return """\
\t.text
\t.globl String.length
String.length:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t24(%rdi), %rdi
\txor\t%eax, %eax
\tcall\tcoolstrlen
\tpushq\t%rax
\tsubq\t$8, %rsp
\tcall\tInt..new
\taddq\t$8, %rsp
\tpopq\t%rdi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """


def _build_string_substr():
    return """\
\t.text
\t.section\t.rodata
.LCSE:
\t.asciz "ERROR: 0: Exception: String.substr out of range\\n"
\t.text
\t.globl String.substr
String.substr:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tmovq\t24(%rdx), %rdx
\tcall\tcoolsubstr
\tcmpq\t$0, %rax
\tjne\t.LSG
\tleaq\t.LCSE(%rip), %rdi
\tcall\tprintf@PLT
\txor\t%edi, %edi
\tcall\texit@PLT
\tnop
.LSG:
\tpushq\t%rax
\tsubq\t$8, %rsp
\tcall\tString..new
\taddq\t$8, %rsp
\tpopq\t%rdi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
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
\tleaq\tIO..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tmovq\t%rbp, %rsp
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
\tleaq\tObject..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tmovq\t%rbp, %rsp
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
\tleaq\tInt..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\txor\t%edi, %edi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
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
\tleaq\tString..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\tleaq\t.LStringNew(%rip), %rdi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
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
\tleaq\tBool..vtable(%rip), %rdi
\tmovq\t%rdi, 16(%rax)
\txor\t%edi, %edi
\tmovq\t%rdi, 24(%rax)
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """

def _build_main():
    return """\
\t.text
\t.globl main
main:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
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
\tmovq\t%rsp, %rbp
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
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """

def _build_lt_helper() -> str:
    return """\
\t.text
\t.globl lt_helper
lt_helper:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
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
\tjmp\tlt_end
lt_bool:
lt_int:
\tmovq\t24(%rdi), %rdi
\tmovq\t24(%rsi), %rsi
\tcmpl\t%esi, %edi
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
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """

def _build_le_helper() -> str:
    return """\
\t.text
\t.globl le_helper
le_helper:
\tpushq\t%rbp
\tmovq\t%rsp, %rbp
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
\tje\tle_true
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
\tcmpl\t%esi, %edi
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
\tmovq\t%rbp, %rsp
\tpopq\t%rbp
\tret

    """

def _build_cooloutstr():
    return """\
\t.text
\t.globl cooloutstr
\t.type\tcooloutstr, @function
cooloutstr:
.LFB0:
\t.cfi_startproc
\tpushq   %rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq    %rsp, %rbp
\t.cfi_def_cfa_register 6
\tsubq    $32, %rsp
\tmovq    %rdi, -24(%rbp)
\tmovl    $0, -4(%rbp)
\tjmp     .LCOS2
.LCOS5:
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\tcmpb    $92, %al
\tjne     .LCOS3
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    $1, %rax
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\tcmpb    $110, %al
\tjne     .LCOS3
\tmovq    stdout(%rip), %rax
\tmovq    %rax, %rsi
\tmovl    $10, %edi
\tcall    fputc
\taddl    $2, -4(%rbp)
\tjmp     .LCOS2
.LCOS3:
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\tcmpb    $92, %al
\tjne     .LCOS4
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    $1, %rax
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\tcmpb    $116, %al
\tjne     .LCOS4
\tmovq    stdout(%rip), %rax
\tmovq    %rax, %rsi
\tmovl    $9, %edi
\tcall    fputc
\taddl    $2, -4(%rbp)
\tjmp     .LCOS2
.LCOS4:
\tmovq    stdout(%rip), %rdx
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\tmovsbl  %al, %eax
\tmovq    %rdx, %rsi
\tmovl    %eax, %edi
\tcall    fputc
\taddl    $1, -4(%rbp)
.LCOS2:
\tmovl    -4(%rbp), %eax
\tcltq
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\ttestb   %al, %al
\tjne     .LCOS5
\tmovq    stdout(%rip), %rax
\tmovq    %rax, %rdi
\tcall    fflush
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE0:
\t.size   cooloutstr, .-cooloutstr

"""

def _build_coolstrlen():
    return """\
\t.text
\t.globl coolstrlen
\t.type   coolstrlen, @function
coolstrlen:
.LFB1:
\t.cfi_startproc
\tpushq   %rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq    %rsp, %rbp
\t.cfi_def_cfa_register 6
\tmovq    %rdi, -24(%rbp)
\tmovl    $0, -4(%rbp)
\tjmp     .LCSL7
.LCSL8:
\tmovl    -4(%rbp), %eax
\taddl    $1, %eax
\tmovl    %eax, -4(%rbp)
.LCSL7:
\tmovl    -4(%rbp), %eax
\tmov     %eax, %eax
\taddq    -24(%rbp), %rax
\tmovzbl  (%rax), %eax
\ttestb   %al, %al
\tjne     .LCSL8
\tmovl    -4(%rbp), %eax
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE1:
\t.size   coolstrlen, .-coolstrlen
        
        """

def _build_coolstrcat():
    return """\
\t.text
\t.section\t.rodata
\t.LCSCC0:
\t.asciz "%s%s"
\t.text
\t.globl coolstrcat
\t.type\tcoolstrcat, @function
coolstrcat:
.LFB2:
\t.cfi_startproc
\tpushq   %rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq    %rsp, %rbp
\t.cfi_def_cfa_register 6
\tpushq   %rbx
\tsubq    $40, %rsp
\tmovq    %rdi, -40(%rbp)
\tmovq    %rsi, -48(%rbp)
\tcmpq    $0, -40(%rbp)
\tjne     .LCSC10
\t.cfi_offset 3, -24
\tmovq    -48(%rbp), %rax
\tjmp     .LCSC11
.LCSC10:
\tcmpq    $0, -48(%rbp)
\tjne     .LCSC12
\tmovq    -40(%rbp), %rax
\tjmp     .LCSC11
.LCSC12:
\tmovq    -40(%rbp), %rax
\tmovq    %rax, %rdi
\tcall    coolstrlen
\tmovl    %eax, %ebx
\tmovq    -48(%rbp), %rax
\tmovq    %rax, %rdi
\tcall    coolstrlen
\tleal    (%rbx,%rax), %eax
\taddl    $1, %eax
\tmovl    %eax, -20(%rbp)
\tmovl    -20(%rbp), %eax
\tcltq
\tmovl    $1, %esi
\tmovq    %rax, %rdi
\tcall    calloc
\tmovq    %rax, -32(%rbp)
\tleaq    .LCSCC0(%rip), %rdx
\tmovl    -20(%rbp), %eax
\tmovslq  %eax, %rbx
\tmovq    -48(%rbp), %rsi
\tmovq    -40(%rbp), %rcx
\tmovq    -32(%rbp), %rax
\tmovq    %rsi, %r8
\tmovq    %rbx, %rsi
\tmovq    %rax, %rdi
\tmovl    $0, %eax
\tcall    snprintf
\tmovq    -32(%rbp), %rax
.LCSC11:
\taddq    $48, %rsp
\tpopq    %rbx
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE2:
\t.size   coolstrcat, .-coolstrcat
"""
    pass


def _build_coolsubstr():
    return """\
\t.text
\t.globl coolsubstr
\t.type\tcoolsubstr, @function
coolsubstr:
.LFB4:
\t.cfi_startproc
\tpushq\t%rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq\t%rsp, %rbp
\t.cfi_def_cfa_register 6
\tsubq\t$48, %rsp
\tmovq\t%rdi, -24(%rbp)
\tmovq\t%rsi, -32(%rbp)
\tmovq\t%rdx, -40(%rbp)
\tmovq\t-24(%rbp), %rax
\tmovq\t%rax, %rdi
\tcall\tcoolstrlen
\tmovl\t%eax, -4(%rbp)
\tcmpq\t$0, -32(%rbp)
\tjs\t.LCSS22
\tcmpq\t$0, -40(%rbp)
\tjs\t.LCSS22
\tmovq\t-40(%rbp), %rax
\tmovq\t-32(%rbp), %rdx
\taddq\t%rax, %rdx
\tmovl\t-4(%rbp), %eax
\tcltq
\tcmpq\t%rax, %rdx
\tjle\t.LCSS23
.LCSS22:
\tmovl\t$0, %eax
\tjmp \t.LCSS24
.LCSS23:
\tmovq\t-40(%rbp), %rdx
\tmovq\t-32(%rbp), %rax
\taddq\t-24(%rbp), %rax
\tmovq\t%rdx, %rsi
\tmovq\t%rax, %rdi
\tcall\tstrndup
.LCSS24:
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE4:
\t.size\tcoolsubstr, .-coolsubstr
\t

    """

def _build_coolgetstr():
    return """\
\t.text
\t.section\t.rodata
.LCGSC1:
\t.asciz ""
\t.text
\t.globl coolgetstr
\t.type\tcoolgetstr, @function
coolgetstr:
.LFB3:
\t.cfi_startproc
\tpush\t%rbp
\t.cfi_def_cfa_offset 16
\t.cfi_offset 6, -16
\tmovq\t%rsp, %rbp
\t.cfi_def_cfa_register 6
\tsubq\t$32, %rsp
\tmovl\t$1, %esi
\tmovl\t$40960, %edi
\tcall\tcalloc
\tmovq\t%rax, -16(%rbp)
\tmovl\t$0, -4(%rbp)
.LCGS20:
\tmovq\tstdin(%rip), %rax
\tmovq\t%rax, %rdi
\tcall\tfgetc
\tmovl\t%eax, -20(%rbp)
\tcmpl\t$-1, -20(%rbp)
\tje\t.LCGS14
\tcmpl\t$10, -20(%rbp)
\tjne\t.LCGS15
.LCGS14:
\tcmpl\t$0, -4(%rbp)
\tje\t.LCGS16
\tleaq\t.LCGSC1(%rip), %rax
\tjmp \t.LCGS17
.LCGS16:
\tmovq\t-16(%rbp), %rax
\tjmp \t.LCGS17
.LCGS15:
\tcmpl\t$0, -20(%rbp)
\tjne \t.LCGS18
\tmovl\t$1, -4(%rbp)
\tjmp \t.LCGS20
.LCGS18:
\tmovq\t-16(%rbp), %rax
\tmovq\t%rax, %rdi
\tcall\tcoolstrlen
\tmov\t%eax, %eax
\taddq\t-16(%rbp), %rax
\tmovl\t-20(%rbp), %edx
\tmovb\t%dl, (%rax)
\tjmp\t.LCGS20
.LCGS17:
\tleave
\t.cfi_def_cfa 7, 8
\tret
\t.cfi_endproc
.LFE3:
\t.size   coolgetstr, .-coolgetstr
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
    _build_main(),
    _build_cooloutstr(),
    _build_coolstrlen(),
    _build_coolstrcat(),
    _build_coolsubstr(),
    _build_coolgetstr()
]