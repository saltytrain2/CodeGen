from tacnodes import *
from cfgnodes import CFGFunc, FixedRegisterAllocator
from typing import List
from collections import defaultdict
from coolbase import HELPERS


class LabelAllocator(object):
    def __init__(self):
        self.cur_label_num = 0
        self.label_map:Dict[TacLabel, str] = defaultdict(str)

    def emit_label(self, taclabel:TacLabel) -> str:
        label = self.label_map[taclabel]
        
        if not label:
            label = ".L" + str(self.cur_label_num)
            self.cur_label_num += 1
        return label


class StringAllocator(object):
    def __init__(self):
        self.string_map:Dict[str, str] = defaultdict(str)
        self.string_num = 0

    def add_string(self, string_name:str) -> str:
        label = self.string_map[string_name]
        if not label:
            label = ".LC" + str(self.string_num)
            self.string_map[string_name] = label
            self.string_num += 1

        return label

    def gen_x86_strings(self, asm:List[str]):
        for string_name in self.string_map:
            asm.append("\t.text\n\t.section\t.rodata\n")
            asm.append(f"{self.string_map[string_name]}:\n")
            asm.append(f"\t.asciz \"{string_name}\"\n")


class CodeGen(object):
    def __init__(self, impl_map:List[ImplMapEntry], tacfuncs:List[TacFunc]):
        self.impl_map = impl_map
        self.tacfuncs = tacfuncs
        self.reg_allocator = FixedRegisterAllocator()
        self.label_allocator = LabelAllocator()
        self.string_allocator = StringAllocator()
    
    def gen_x86(self) -> str:
        # generate the code assembly code for the file
        asm:List[str] = []
        
        # generate the vtables
        for impl_map_entry in self.impl_map:
            self.gen_x86_vtable(asm, impl_map_entry)

        for tacfunc in self.tacfuncs:
            self.gen_x86_tacfunc(asm, tacfunc)

        # now generate the string labels
        self.string_allocator.gen_x86_strings(asm)
        
        # builtin methods
        asm.extend(HELPERS)
        return "".join(asm)
    
    def gen_x86_vtable(self, asm:List[str], impl_map_entry:ImplMapEntry):
        class_name = impl_map_entry.class_name
        asm.append(f"\t.text\n\t.globl {class_name}..vtable\n")
        asm.append(f"{class_name}..vtable:\n")
        
        # next two entries are for the class string and the constructor
        str_label = self.string_allocator.add_string(class_name)
        asm.append(f"\t.quad {str_label}\n")
        asm.append(f"\t.quad {class_name}..new\n")

        # now for all the methods
        for method in impl_map_entry.method_list:
            asm.append(f"\t.quad {method.parent}.{method.get_name()}\n")

    def gen_x86_tacfunc(self, asm:List[str], tacfunc:TacFunc):
        # set up the function prologue and label
        asm.append("\t.text\n")
        asm.append(f"\t.globl {tacfunc.name}\n")
        asm.append(f"{tacfunc.name}:\n")
        asm.append("\tpushq\t%rbp\n")
        asm.append("\tmovq\t%rsp, %rbp\n")

        # allocate all space on the stack
        asm.append(f"\tsubq\t${tacfunc.stack_space}, %rsp\n")

        for inst in tacfunc.insts:
            self.gen_x86_inst(asm, inst)
        
        asm.append("\tmovq\t%rbp, %rsp\n")
        asm.append("\tpopq\t%rbp\n")
        asm.append("\tret\n\n")

    def gen_x86_inst(self, asm:List[str], inst:TacInst) -> str:
        if isinstance(inst, TacLabel):
            asm.append(f"{self.label_allocator.emit_label(inst)}:\n")
        # TODO I currently assume that rax and r11 are trash registers and will never be allocated to variables
        elif isinstance(inst, TacAdd):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r13\n")
            asm.append(f"\taddl\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r13, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacSub):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r13\n")
            asm.append(f"\tsubl\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r13, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacMul):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r13\n")
            asm.append(f"\timull\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r13, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacDiv):
            asm.append("\tmovq\t%rdx, %r13\n")
            asm.append("\tmovq\t%rax, %r15\n")
            asm.append("\txor\t%edx, %edx\n")
            asm.append(f"\tmovl\t{inst.src1.get_preg_32_str()}, %eax\n")
            asm.append(f"\tidivl\t{inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t%eax, {inst.dest.get_preg_32_str()}\n")
            asm.append("\tmovq\t%r13, %rdx\n")
            asm.append("\tmovq\t%r15, %rax\n")
        elif isinstance(inst, TacLoad):
            mem_reg = inst.src.get_preg_str() if inst.offset is None else f"{inst.offset*8}({inst.src.get_preg_str()})"
            asm.append(f"\tmovq\t{mem_reg}, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacStore):
            mem_reg = inst.dest.get_preg_str() if inst.offset is None else f"{inst.offset*8}({inst.dest.get_preg_str()})"
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, {mem_reg}\n")
        elif isinstance(inst, TacLoadImm):
            dest = inst.dest.get_preg_str()
            if isinstance(inst.imm, TacImmLabel):
                asm.append(f"\tleaq\t{inst.imm.val}(%rip), {dest}\n")
            elif isinstance(inst.imm, TacStr):
                str_label = self.string_allocator.add_string(inst.imm.val)
                asm.append(f"\tleaq\t{str_label}(%rip), {dest}\n")
            elif isinstance(inst.imm, TacImm):
                asm.append(f"\tmovq\t${inst.imm.val}, {dest}\n")
        elif isinstance(inst, (TacCall, TacSyscall, TacCreate)):
            # TODO assume that all clobbered registers are getting clobbered
            stack:List[str] = []
            for reg in inst.save_regs:
                asm.append(f"\tpushq\t{reg.get_name()}\n")
                stack.append(reg.get_name())

            # move the parameters into place
            param_registers = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
            params = list(reversed(inst.args))
            i = 0
            while params and i < 6:
                param = params.pop()
                asm.append(f"\tmovq\t{param.get_preg_str()}, {param_registers[i]}\n")
                i += 1
            
            # if there are any leftover parameters, push them onto the stack
            for param in params:
                if param.isstack:
                    asm.append(f"\tmovq\t{param.get_preg_str()}, %r15\n")
                    asm.append("\tpushq\t%r15\n")
                    stack.append("%r15")
                else:
                    asm.append(f"\tpushq\t{param.get_preg_str()}\n")
                    stack.append(param.get_preg_str())
            
            # 16 byte align the pushes
            if len(stack) & 1:
                asm.append("\tpushq\t%r15\n")
                stack.append("%r15")

            # get the vtable
            # there should only be a . in the function name if this is a static dispatch
            if isinstance(inst, TacSyscall):
                if "printf" in inst.func:
                    asm.append("\txor\t%eax, %eax\n")
                asm.append(f"\tcall\t{inst.func}\n")
            elif isinstance(inst, TacCreate):
                if inst.object == "SELF_TYPE":
                    asm.append(f"\tmovq\t16(%rdi), %r12\n")
                    asm.append(f"\tmovq\t8(%r12), %r12\n")
                    asm.append(f"\tcall\t*%r12\n")
                else:
                    asm.append(f"\tcall\t{inst.object}..new\n")
            elif "." in inst.func:
                asm.append(f"\tcall\t{inst.func}\n")
            else:
                asm.append(f"\tmovq\t16(%rdi), %r12\n")
                asm.append(f"\tmovq\t${inst.offset}, %r13\n")
                asm.append(f"\taddq\t%r13, %r12\n")
                asm.append(f"\tcall\t*%r12\n")

            # pop off everything in the stack
            while stack:
                asm.append(f"\tpopq\t{stack.pop()}\n")
            
            if inst.dest.get_preg != PReg("%rax"):
                asm.append(f"\tmovq\t%rax, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacRet):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, %rax\n")
        elif isinstance(inst, TacCmp):
            asm.append(f"\tcmpq\t{inst.src1.get_preg_str()}, {inst.src2.get_preg_str()}\n")
            pass
        elif isinstance(inst, TacBr):
            if inst.cond is None:
                asm.append(f"\tjmp\t{self.label_allocator.emit_label(inst.true_label)}\n")
                return
            
            if inst.cond == TacCmpOp.EQ:
                asm.append(f"\tje\t{self.label_allocator.emit_label(inst.true_label)}\n")
            elif inst.cond == TacCmpOp.NE:
                asm.append(f"\tjne\t{self.label_allocator.emit_label(inst.true_label)}\n")
            asm.append(f"\tjmp\t{self.label_allocator.emit_label(inst.false_label)}\n")
        elif isinstance(inst, TacStoreSelf):
            asm.append(f"\tmovq\t{inst.self_obj.get_preg_str()}, %rdi\n")
        elif isinstance(inst, TacNot):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, %r15\n")
            asm.append(f"\txor\t%r15, 1\n")
            asm.append(f"\tmovq\t%r15, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacNegate):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, %r15\n")
            asm.append(f"\tneg\t%r15\n")
            asm.append(f"\tmovq\t%r15, {inst.dest.get_preg_str()}\n")        