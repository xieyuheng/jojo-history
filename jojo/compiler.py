from . vm import (
    VM, RP,
    GET, SET,
    JOJO, MSG, CLO,
    APPLY, IFTE,
    NEW,
    CALL,
)

from . sexp import (
    null, null_p,
    cons, cons_p,
    list_p,
    car, cdr,
)

import types
import sys
import importlib

def get_current_module():
    return sys.modules[__name__]

def get_jojo_name_list(sexp_list):
    jojo_name_list = []
    for sexp in sexp_list:
        if not cons_p(sexp):
            pass
        elif car(sexp) == '+jojo':
            body = cdr(sexp)
            jojo_name = car(body)
            jojo_name_list.append(jojo_name)
    return jojo_name_list

def compile_module(module_name, sexp_list) -> types.ModuleType:
    module = types.ModuleType(module_name)
    jojo_name_list = get_jojo_name_list(sexp_list)
    setattr(module, 'jojo_name_list', jojo_name_list)
    for sexp in sexp_list:
        if cons_p(sexp):
            keyword = car(sexp)
            fun = top_level_keyword_dict[keyword]
            fun(module, cdr(sexp))
    return module

def compile_jojo(module, body) -> JOJO:
    return JOJO(1, 2, add, 3, add)

top_level_keyword_dict = {}

def keyword(name):
    def decorator(fun):
        top_level_keyword_dict[name] = fun
        return fun
    return decorator

@keyword("import")
def k_import(module, body):
    module_name = car(body)
    imported_module = importlib.import_module(module_name)
    setattr(get_current_module(), module_name, imported_module)

@keyword("+jojo")
def plus_jojo(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, compile_jojo(module, cdr(body)))

def drop(a):
    return ()

def dup(a):
    return (a, a)

def over(a, b):
    return (a, b, a)

def tuck(a, b):
    return (b, a, b)

def swap(a, b):
    return (b, a)

def add(a, b):
    return a + b
