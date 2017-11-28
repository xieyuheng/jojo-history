import jojo
import sys
import readline

if __name__ == '__main__':
    if len(sys.argv) == 1:
        module = jojo.new_module('repl')
        jojo.merge_prim_dict(module)
        jojo.merge_module(module, jojo.core_module)
        print ("welcome to jojo's programming adventure in python ^-^/")
        jojo.module_repl(module)
    else:
        path = sys.argv[1]
        module = jojo.load("script", path)
