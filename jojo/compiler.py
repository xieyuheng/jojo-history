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
    setattr(module, 'jojo_name_list',
            get_jojo_name_list(sexp_list))
    setattr(module, 'imported_module_dict', {})
    for sexp in sexp_list:
        if cons_p(sexp):
            top_level_keyword = car(sexp)
            fun = top_level_keyword_dict[top_level_keyword]
            fun(module, cdr(sexp))
    return module

def compile_jo_list(module, body):
    jo_list = []
    sexp_list = body
    while not null_p(sexp_list):
        sexp = car(sexp_list)
        jo_list.extend(sexp_emit(module, sexp))
        sexp_list = cdr(sexp_list)
    return jo_list

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
    keyword = car(cons)
    fun = keyword_dict[keyword]
    return fun(module, cdr(cons))

def symbol_emit(module, symbol):

    if int_symbol_p(symbol):
        return [int(symbol)]

    if string_symbol_p(symbol):
        string = symbol[1:len(symbol)-1]
        return [string]

    if local_symbol_p(symbol):
        return [GET(symbol)]
    if set_local_symbol_p(symbol):
        symbol = symbol[:len(symbol)-1]
        return [SET(symbol)]

    if message_symbol_p(symbol):
        symbol = symbol[1:len(symbol)]
        return [MSG(symbol)]

    if symbol == 'apply':
        return [APPLY]
    if symbol == 'ifte':
        return [IFTE]
    if symbol == 'new':
        return [NEW]

    jojo_name_list = getattr(module, 'jojo_name_list')
    if symbol in jojo_name_list:
        return [CALL(module, symbol)]

    imported_module_dict = getattr(module, 'imported_module_dict')
    if symbol in imported_module_dict.keys():
        imported_module = imported_module_dict[symbol]
        return [imported_module]

    if symbol in prim_dict.keys():
        return [prim_dict[symbol]]

    print ("- symbol_emit fail")
    print ("  meet undefined symbol : {}".format(symbol))

def int_symbol_p(symbol):
    p = re.compile(r"-?[0-9]+\Z")
    if p.match(symbol):
        return True
    else:
        return False

def string_symbol_p(symbol):
    if len(symbol) <= 2:
        return False
    elif symbol[0] != '"':
        return False
    elif symbol[len(symbol)-1] != '"':
        return False
    else:
        return True

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
    imported_module_dict = getattr(module, 'imported_module_dict')
    imported_module_dict[module_name] = imported_module

@top_level_keyword("+jojo")
def plus_jojo(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, JOJO(compile_jo_list(module, cdr(body))))

keyword_dict = {}

def keyword(name):
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

@keyword('clo')
def k_clo(module, body):
    return [CLO(compile_jo_list(module, body))]

prim_dict = {}

def prim(name):
    def decorator(fun):
        prim_dict[name] = fun
        return fun
    return decorator

@prim('drop')
def drop(a):
    return ()

@prim('dup')
def dup(a):
    return (a, a)

@prim('over')
def over(a, b):
    return (a, b, a)

@prim('tuck')
def tuck(a, b):
    return (b, a, b)

@prim('swap')
def swap(a, b):
    return (b, a)

def add(a, b):
    return a + b

prim('add')(add)

@prim('sub')
def add(a, b):
    return a - b

@prim('equal?')
def equal_p(a, b):
    return a == b

@prim('eq?')
def eq_p(a, b):
    return a is b
