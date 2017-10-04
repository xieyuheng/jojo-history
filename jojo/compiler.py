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
import re

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

def compile_module(module_name, sexp_list):
    module = types.ModuleType(module_name)
    jojo_name_list = get_jojo_name_list(sexp_list)
    setattr(module, 'jojo_name_list', jojo_name_list)
    for sexp in sexp_list:
        if cons_p(sexp):
            top_level_keyword = car(sexp)
            fun = top_level_keyword_dict[top_level_keyword]
            fun(module, cdr(sexp))
    return module

def compile_jojo(module, body) -> JOJO:
    jo_list = []
    sexp_list = body
    while not null_p(sexp_list):
        sexp = car(sexp_list)
        jo_list.extend(sexp_emit(module, sexp))
        sexp_list = cdr(sexp_list)
    return JOJO(*jo_list)

def sexp_emit(module, sexp):
    if null_p(sexp):
        return null_emit(module, sexp)
    elif cons_p(sexp):
        return cons_emit(module, sexp)
    else:
        return symbol_emit(module, sexp)

def null_emit(module, sexp):
    return [null]

def cons_emit(module, cons):
    keyword = car(sexp)
    fun = keyword_dict[keyword]
    return fun(module, cdr(cons))

# (+jojo jo-compile (-> :jo --)
#   (cond
#     [:jo int-jo?] [:jo jo->int emit-lit]
#     [:jo local-jo?]     [:jo jo-emit-local]
#     [:jo set-local-jo?] [:jo jo-emit-set-local]
#     [:jo dynamic-local-jo?]     [:jo jo-emit-dynamic-local]
#     [:jo set-dynamic-local-jo?] [:jo jo-emit-set-dynamic-local]
#     [:jo field-jo?]     [:jo jo-emit-field]
#     [:jo set-field-jo?] [:jo jo-emit-set-field]
#     [:jo comma eq?] []
#     else [:jo jo-emit]))

def symbol_emit(module, symbol):
    if int_symbol_p(symbol):
        return [int(symbol)]
    elif local_symbol_p(symbol):
        return [GET(symbol)]
    elif set_local_symbol_p(symbol):
        symbol = symbol[:len(symbol)-1]
        return [SET(symbol)]
    elif message_symbol_p(symbol):
        symbol = symbol[:len(symbol)-1]
        return [MSG(symbol)]

    jojo_name_list = getattr(module, 'jojo_name_list')
    if (0 != jojo_name_list.count(symbol)):
        return [CALL(module, symbol)]
    else:
        return [getattr(sys.modules[__name__], symbol)]

def int_symbol_p(symbol):
    p = re.compile(r"-?[0-9]+\Z")
    if p.match(symbol):
        return True
    else:
        return False

def local_symbol_p(symbol):
    p = re.compile(r":\S+\Z")
    if p.match(symbol):
        return True
    else:
        return False

def set_local_symbol_p(symbol):
    p = re.compile(r":\S+!\Z")
    if p.match(symbol):
        return True
    else:
        return False

def message_symbol_p(symbol):
    p = re.compile(r"\.\S+\Z")
    if p.match(symbol):
        return True
    else:
        return False

top_level_keyword_dict = {}

def top_level_keyword(name):
    def decorator(fun):
        top_level_keyword_dict[name] = fun
        return fun
    return decorator

@top_level_keyword("import")
def k_import(module, body):
    module_name = car(body)
    imported_module = importlib.import_module(module_name)
    setattr(get_current_module(), module_name, imported_module)

@top_level_keyword("+jojo")
def plus_jojo(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, compile_jojo(module, cdr(body)))

keyword_dict = {}

def keyword(name):
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

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
