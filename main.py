from collections import defaultdict
from deserialize import *
from coolast import *
from tac import Tac
from cfg import CFG
from codegen import CodeGen
import sys


def main(argv):
    cl_type_file = argv[1]
    with open(cl_type_file, 'r') as file:
        ast_lines = [line.rstrip("\n\r") for line in reversed(file.readlines())]

    class_map, impl_map, parent_map, _ = read_ast(ast_lines)
    tac = Tac(class_map, impl_map, parent_map)
    tac.tacgen()
    cfg = CFG(tac.get_tacfuncs())
    cfg.calc_interference()
    cfg.optimize()
    cfg.alloc_regs()
    cfg.debug_cfg()
    #cfg.debug_interference()
    cgen = CodeGen(impl_map, cfg.to_tacfuncs())
    #print(cgen.gen_x86())
    #cfg.build_interference_graph()

    with open(cl_type_file[:-8] + ".s", "w") as file:
        file.write(cgen.gen_x86())

if __name__ == '__main__':
    main(sys.argv)
