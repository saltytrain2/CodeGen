from tacnodes import *
from cfgnodes import CFGFunc, FixedRegisterAllocator
from typing import List
from collections import defaultdict
from coolbase import HELPERS


class LabelAllocator(object):
    def __init__(self):
        self.cur_label_num = 0
        self.label_map:Dict[TacLabel, str] = defaultdict(str)
        self.cur_function = None
    
    def set_function(self, func_name:str) -> None:
        self.cur_function = func_name
        self.label_map.clear()

    def emit_label(self, taclabel:TacLabel) -> str:
        label = self.label_map[taclabel]
        
        if label == "":
            label = ".L" + str(self.cur_label_num)
            self.cur_label_num += 1
            self.label_map[taclabel] = label
        return label


class StringAllocator(object):
    def __init__(self):
        self.string_map:Dict[str, str] = defaultdict(str)
        self.error_string_map:Dict[str, str] = defaultdict(str)
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
            # cool strings differ slightly than how normal strings are processed
            raw_string = string_name.replace("\\", "\\\\").replace("\\\\\"", "\\\\\\\"")
            asm.append(f"\t.text\n\t.globl {self.string_map[string_name]}\n")
            asm.append(f"{self.string_map[string_name]}:\n")
            asm.append(f"\t.asciz \"{raw_string}\"\n")



class CodeGen(object):
    def __init__(self, impl_map:List[ImplMapEntry], tacfuncs:List[TacFunc]):
        self.impl_map = impl_map
        self.tacfuncs = tacfuncs
        self.reg_allocator = FixedRegisterAllocator()
        self.label_allocator = LabelAllocator()
        self.string_allocator = StringAllocator()
        self.stack_alignment = 0
    
    def gen_x86(self) -> str:
        # generate the code assembly code for the file
        asm:List[str] = []
        
        # generate the vtables
        for impl_map_entry in self.impl_map:
            self.gen_x86_vtable(asm, impl_map_entry)

        for tacfunc in self.tacfuncs:
            self.label_allocator.set_function(tacfunc.name)
            self.gen_x86_tacfunc(asm, tacfunc)
        
        # now generate the string labels
        self.string_allocator.gen_x86_strings(asm)
        
        # builtin methods
        asm.extend(HELPERS)
        return "".join(asm)
    
    def gen_x86_vtable(self, asm:List[str], impl_map_entry:ImplMapEntry):
        class_name = impl_map_entry.class_name
        asm.append(f"\t.data\n\t.globl {class_name}..vtable\n")
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
        assert tacfunc.stack_space % 8 == 0
        self.stack_alignment = int(tacfunc.stack_space / 8) + len(tacfunc.callee_saved)

        for callee_saved in tacfunc.callee_saved:
            asm.append(f"\tpushq\t{callee_saved.get_name()}\n")

        for inst in tacfunc.insts:
            self.gen_x86_inst(asm, inst)

        for callee_saved in reversed(tacfunc.callee_saved):
            asm.append(f"\tpopq\t{callee_saved.get_name()}\n")
        
        asm.append("\tmovq\t%rbp, %rsp\n")
        asm.append("\tpopq\t%rbp\n")
        asm.append("\tret\n\n")

    def gen_x86_inst(self, asm:List[str], inst:TacInst) -> str:
        if isinstance(inst, TacLabel):
            asm.append(f"{self.label_allocator.emit_label(inst)}:\n")
        elif isinstance(inst, TacDeclare):
            asm.append(f"\tmovq\t$0, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacAdd):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %rax\n")
            asm.append(f"\taddq\t{inst.src1.get_preg_str()}, %rax\n")
            asm.append(f"\tmovq\t%rax, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacSub):
            asm.append(f"\tmovq\t{inst.src1.get_preg_str()}, %rax\n")
            asm.append(f"\tsubq\t{inst.src2.get_preg_str()}, %rax\n")
            asm.append(f"\tmovq\t%rax, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacMul):
            asm.append(f"\tmovq\t{inst.src2.get_preg_str()}, %rax\n")
            asm.append(f"\timull\t{inst.src1.get_preg_32_str()}, %eax\n")
            asm.append(f"\tsalq\t$32, %rax\n")
            asm.append(f"\tsarq\t$32, %rax\n")
            asm.append(f"\tmovq\t%rax, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacDiv):
            asm.append("\tmovq\t%rdx, %r11\n")
            asm.append(f"\tmovq\t{inst.src1.get_preg_str()}, %rax\n")
            asm.append("\txor\t%edx, %edx\n")
            asm.append("\tcdq\n")
            if inst.src2.get_preg() == PReg("%rdx"):
                asm.append("\tidivl\t%r11d\n")
            else:
                asm.append(f"\tidivl\t{inst.src2.get_preg_32_str()}\n")
            asm.append("\tmovq\t%r11, %rdx\n")
            asm.append(f"\tmovq\t%rax, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacLoad):
            mem_reg = inst.src.get_preg_str() if inst.offset is None else f"{inst.offset*8}({inst.src.get_preg_str()})"
            asm.append(f"\tmovq\t{mem_reg}, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacStore):
            mem_reg = inst.dest.get_preg_str() if inst.offset is None else f"{inst.offset*8}({inst.dest.get_preg_str()})"
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, {mem_reg}\n")
        elif isinstance(inst, TacLoadPrim):
            asm.append(f"\tmovq\t24({inst.src.get_preg_str()}), {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacStorePrim):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, 24({inst.dest.get_preg_str()})\n")
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
            stack:List[str] = []
            for reg in inst.save_regs:
                asm.append(f"\tpushq\t{reg.get_name()}\n")
                stack.append(reg.get_name())

            # move the parameters into place
            self.move_params(asm, inst.args, stack)
            
            # 16 byte align the pushes
            if (self.stack_alignment + len(stack)) & 1:
                asm.append("\tsubq\t$8, %rsp\n")

            # get the vtable
            # there should only be a . in the function name if this is a static dispatch
            if isinstance(inst, TacSyscall):
                if "printf" in inst.func:
                    asm.append("\txor\t%eax, %eax\n")
                asm.append(f"\tcall\t{inst.func}\n")
            elif isinstance(inst, TacCreate):
                if inst.object != "SELF_TYPE":
                    asm.append(f"\tcall\t{inst.object}..new\n")
                else:
                    asm.append(f"\tmovq\t16({inst.self_reg.get_preg_str()}), %rax\n")
                    asm.append("\tmovq\t8(%rax), %rax\n")
                    asm.append("\tcall\t*%rax\n")
            elif "." in inst.func:
                asm.append(f"\tleaq\t{inst.func.split('.')[0]}..vtable(%rip), %rax\n")
                asm.append(f"\tmovq\t{inst.offset}(%rax), %rax\n")
                asm.append(f"\tcall\t*%rax\n")
            else:
                asm.append(f"\tmovq\t16(%rdi), %rax\n")
                asm.append(f"\tmovq\t{inst.offset}(%rax), %rax\n")
                asm.append(f"\tcall\t*%rax\n")

            # pop off everything in the stack
            if (self.stack_alignment + len(stack)) & 1:
                asm.append("\taddq\t$8, %rsp\n")
            while stack:
                asm.append(f"\tpopq\t{stack.pop()}\n")
            
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
            asm.append(f"\tmovq\t{inst.self_obj.get_preg_str()}, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacNot):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, {inst.dest.get_preg_str()}\n")
            asm.append(f"\txor\t$1, {inst.dest.get_preg_str()}\n")
        elif isinstance(inst, TacNegate):
            asm.append(f"\tmovq\t{inst.src.get_preg_str()}, {inst.dest.get_preg_str()}\n")
            asm.append(f"\tneg\t{inst.dest.get_preg_str()}\n")  
        elif isinstance(inst, TacUnreachable):
            asm.append(f"\tnop\n")

    def move_params(self, asm: List[str], params: List[TacReg], stack: List[PReg]) -> None:
        param_registers = ["%rdi", "%rsi", "%rdx", "%rcx", "%r8", "%r9"]
        stack_params = params[6:]
        for param in reversed(stack_params):
            if param.isstack:
                asm.append(f"\tmovq\t{param.get_preg_str()}, %r11\n")
                asm.append("\tpushq\t%r11\n")
                stack.append("%r11")
            else:
                asm.append(f"\tpushq\t{param.get_preg_str()}\n")
                stack.append(param.get_preg_str())

        reg_params = params[:6]
        param_map = {arg.get_preg_str():param_registers[i] for i, arg in enumerate(reg_params) if arg.get_preg_str() != param_registers[i]}

        while param_map:
            can_add = []
            for key, value in param_map.items():
                if value not in param_map.keys():
                    can_add.append((key, value))

            for key, value in can_add:
                asm.append(f"\tmovq\t{key}, {value}\n")
                del param_map[key]
        pass