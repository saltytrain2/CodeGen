from __future__ import annotations
from cfgnodes import *

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
        pass
    
    def optimize(self) -> None:
        self.set_dominators()
        pass
    
    def calc_interference(self) -> None:
        for cfg in self.cfg_list:
            cfg.calc_interference()

    def set_dominators(self) -> None:
        for cfg in self.cfg_list:
            cfg.set_dominators()

    def alloc_regs(self) -> None:
        for cfg in self.cfg_list:
            cfg.precolor_regs()
            cfg.alloc_regs()
        pass
    
    def to_tacfuncs(self) -> List[TacFunc]:
        return [i.to_tacfunc() for i in self.cfg_list]

    def build_interference_graph(self) -> None:
        # find the live ranges of each variable
        # for cfg in self.cfg_list:
        #     cfg.calc_liveness()
        pass
