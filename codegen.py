from tacnodes import *
from cfgnodes import CFGFunc
from typing import List
from collections import defaultdict


class LabelAllocator(object):
    def __init__(self):
        self.cur_label_num = 0

    def emit_label(self) -> str:
        label = ".L" + str(self.cur_label_num)
        self.cur_label_num += 1
        return label


class StringAllocator(object):
    def __init__(self):
        self.string_map:Dict[str, str] = defaultdict(str)
        self.string_num = 0

    def add_string(self, string_name:str) -> str:
        label = ".LC" + self.string_num
        self.string_map[label] = string_name
        return label

    def gen_x86_strings(self, asm:List[str]):
        for label in self.string_map:
            asm.append("\t.text\n\t.section\t.rodata\n")
            asm.append(f"{label}\n")
            asm.append(f"\t.asciz \"{self.string_map[label]}\"\n")


class CodeGen(object):
    def __init__(self, impl_map:List[ImplMapEntry], tacfuncs:List[TacFunc]):
        self.impl_map = impl_map
        self.tacfuncs = tacfuncs
        self.reg_allocator = RegisterAllocator()
        self.label_allocator = LabelAllocator()
        self.string_allocator = StringAllocator()
    
    def gen_x86(self) -> str:
        # generate the code assembly code for the file
        asm:List[str] = []
        
        # generate the vtables
        for impl_map_entry in self.impl_map:
            gen_x86_vtable(asm, impl_map_entry)

        for tacfunc in self.tacfuncs:
            gen_x86_tacfunc(asm, tacfunc)

        # now generate the string labels
        self.string_allocator.gen_x86(asm)

        return "".join(asm)
    
    def gen_x86_vtable(self, asm:List[str], impl_map_entry:ImplMapEntry):
        class_name = impl_map_entry.class_name
        asm.append(f"\t.data\n\t.globl {class_name}.vtable\n")
        asm.append(f"{class_name}..vtable:\n")
        
        # next two entries are for the class string and the constructor
        str_label = self.string_allocator.add_string(class_name)
        asm.append(f"\t.quad {str_label}\n")
        asm.append(f"\t.quad {clas_name}..new\n")

        # now for all the methods
        for method in impl_map_entry.method_list:
            asm.append(f"\t.quad {method.get_name()}\n")

    def gen_x86_tacfunc(self, asm:List[str], tacfunc:TacFunc):
        # set up the function prologue and label
        asm.append("\t.text\n")
        asm.append("\t.globl {tacfunc.name}\n")
        asm.append("\t{tacfunc.name}:\n")
        asm.append("\tpushq\t%rbp\n")
        asm.append("\tmovq\t%rsp, %rbp\n")

        # allocate all space on the stack
        offset = 0
        for inst in tacfunc.inst_list:
            if not isinstance(inst, TacAlloc):
                break
            offset += 8
        asm.append("\tsubq\t${offset}, %rsp\n")
        
        # push all the callee saved registers into the stack
        #callee_regs = ["%rbx", "%r12", "%r13", "%r14", "%r15"]
        #for reg in callee_regs:
        #    asm.append(f"\tpushq\t{reg}\n")

        for inst in tacfunc.inst_list:
            self.gen_x86_inst(asm, inst)
        
        # pop all the callee saved registers off the stack
        while callee_regs:
            asm.append(f"\tpopq\t{callee_regs.pop()}\n")
        # return address handling
        asm.append("\tmovq\t%rbp, %rsp\n")
        asm.append("\tpopq\t%rbp\n")
        asm.append("\nret\n")

    def gen_x86_inst(self, asm:List[str], inst:TacInst) -> str:
        if isinstance(inst, TacLabel):
            asm.append(f"{self.label_allocator.emit_label()}:\n")
        # TODO I currently assume that rax and r11 are trash registers and will never be allocated to variables
        elif isinstance(inst, TacAdd):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r11\n")
            asm.append(f"\taddl\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r11, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacSub):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r11\n")
            asm.append(f"\tsubl\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r11, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacMul):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %r11\n")
            asm.append(f"\timull\t{inst.src1.get_preg_32_str()}, {inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t{inst.src2.get_preg_32_str()}, {inst.dest.get_preg_32_str()}\n")
            asm.append(f"\tmovq\t%r11, {inst.src2.get_preg_str()}\n")
        elif isinstance(inst, TacDiv):
            asm.append("\tmovq\t%rdx, %r11\n")
            asm.append("\txor\t%edx, %edx\n")
            asm.append(f"\tmovl\t{inst.src1.get_preg_32_str()}, %eax\n")
            asm.append(f"\tidivl\t{inst.src2.get_preg_32_str()}\n")
            asm.append(f"\tmovl\t%eax, {inst.dest.get_preg_32_str()}\n")
            asm.append("\tmovq\t%r11, %rdx\n")
        elif isinstance(inst, TacLoad):
            mem_reg = inst.src.get_preg_str() if inst.src.isstack else f"{inst.offset}({inst.src.get_preg_str()})"
            asm.append(f"\tmovq\tmem_reg, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacStore):
            mem_reg = inst.dest.get_preg_str() if inst.dest.isstack else f"{inst.offset}({inst.dest.get_preg_str()})"
            asm.append(f"\tmovq\tmem_reg, {offset_str}({inst.src.get_preg_str()})\n")
        elif isinstance(inst, TacCall):
            # TODO assume that all clobbered registers are getting clobbered
            save_regs = inst.save_regs
            stack = []
            for reg in save_regs:
                asm.append(f"\tpushq\t{reg.get_name()}\n")
                stack.append(reg.get_name())

            # move the parameters into the registers
            param_regs = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
            for i, param in enumerate(inst.args):
                if i < 6:
                    asm.append(f"\tmovq\t{}, {param_regs[i]}\n")
                    pass
                elif param.isstack:
                    asm.append(f"\tmovq\t{param.get_preg_str()}, %r11\n")
                    asm.append(f"\tpushq\t%r11\n")
                    stack.append("%r11\n")
                else:
                    asm.append(f"\tpushq\t{param.get_preg_str()}\n")
                    stack.append(f"%{param.get_preg_str()}\n")

            # get the vtable
            # there should only be a . in the function name if this is a static dispatch
            if "." in inst.func:
                class_name = inst.func[:inst.func.index(".")]
                asm.append(f"\tmovq\t${class_name}..vtable, %r11\n")
            else:
                asm.append(f"\tmovq\t%rdi, %r11\n")
            asm.append(f"\tcall\t*%r11\n")

            # pop off everything in the stack
            while stack:
                asm.append(f"\tpopq\t{stack.pop()}\n")
        elif isinstance(inst, TacRet):
            asm.append(f"\tmovq\t{inst.get_preg_str()}, %rax\n")
        elif isinstance(inst, TacSyscall):
            pass 
        
