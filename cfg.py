from __future__ import annotations
from cfgnodes import *
from optimizations import ConstantPropogator

class CFG(object):
    def __init__(self, tacfuncs:List[TacFunc]):
        self.cfg_list:List[CFGFunc] = []
        self.process_tacfuncs(tacfuncs)
    
    def process_tacfuncs(self, tacfuncs:List[TacFunc]) -> None:
        for tacfunc in tacfuncs:
            self.cfg_list.append(CFGFunc(tacfunc))

    def get_cfg_funcs(self) -> List[CFGFunc]:
        return self.cfg_list

    def debug_cfg(self) -> None:
        for cfg_func in self.cfg_list:
            print(repr(cfg_func))
            #cfg_func.print_interference()
    
    def debug_interference(self) -> None:
        for cfg_func in self.cfg_list:
            print(cfg_func.name)
            cfg_func.print_interference()
            print()
        pass 
    
    def optimize(self) -> None:
        self.set_dominators()
        #self.constant_propogate()
        #self.calc_interference()
        pass
    
    def calc_interference(self) -> None:
        for cfg in self.cfg_list:
            cfg.calc_interference()

    def set_dominators(self) -> None:
        for cfg in self.cfg_list:
            cfg.set_dominators()

    def alloc_regs(self) -> None:
        for cfg in self.cfg_list:
            cfg.alloc_regs()
        pass

    def resolve_stack_discipline(self) -> None:
        for cfg in self.cfg_list:
            cfg.resolve_stack_discipline()
    
    def to_tacfuncs(self) -> List[TacFunc]:
        return [i.to_tacfunc() for i in self.cfg_list]

    def build_interference_graph(self) -> None:
        # find the live ranges of each variable
        # for cfg in self.cfg_list:
        #     cfg.calc_liveness()
        pass

    def constant_propogate(self) -> None:
        for cfg in self.cfg_list:
            optimizer = ConstantPropogator(cfg)
            optimizer.optimize()
        pass

