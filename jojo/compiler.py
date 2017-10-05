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

def list_to_stack(l):
    stack = []
    while not null_p(l):
        stack.append(car(l))
        l = cdr(l)
    return stack

def convert_jojo_name(name):
    char_list = []
    length = len(name)
    for s in name:
        if s == '-':
            char_list.append('_')
        elif s == '?':
            char_list.append('_p')
        else:
            char_list.append(s)
    return "".join(char_list)

def get_jojo_name_list(sexp_list):
    jojo_name_list = []
    for sexp in sexp_list:
        if not cons_p(sexp):
            pass
        elif car(sexp) == '+jojo':
            body = cdr(sexp)
            jojo_name = convert_jojo_name(car(body))
            jojo_name_list.append(jojo_name)
    return jojo_name_list

def get_macro_name_list(sexp_list):
    macro_name_list = []
    for sexp in sexp_list:
        if not cons_p(sexp):
            pass
        elif car(sexp) == '+macro':
            body = cdr(sexp)
            macro_name = convert_jojo_name(car(body))
            macro_name_list.append(macro_name)
    return macro_name_list

def compile_module(module_name, sexp_list):
    module = types.ModuleType(module_name)
    setattr(module, 'jojo_name_list',
            get_jojo_name_list(sexp_list))
    setattr(module, 'macro_name_list',
            get_macro_name_list(sexp_list))
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
    if keyword in keyword_dict.keys():
        fun = keyword_dict[keyword]
        return fun(module, cdr(cons))
    else:
        print("- cons_emit fail")
        print("  meet unknown keyword : {}".format(keyword))

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
        symbol = convert_jojo_name(symbol)
        return [MSG(symbol)]

    if symbol == 'apply':
        return [APPLY]
    if symbol == 'ifte':
        return [IFTE]
    if symbol == 'new':
        return [NEW]

    symbol = convert_jojo_name(symbol)

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
    if len(symbol) <= 1:
        return False
    if symbol[0] != ':':
        return False
    if symbol[len(symbol)-1] == '!':
        return False
    else:
        return True

def set_local_symbol_p(symbol):
    if len(symbol) <= 2:
        return False
    if symbol[0] != ':':
        return False
    if symbol[len(symbol)-1] != '!':
        return False
    else:
        return True

def message_symbol_p(symbol):
    p = re.compile(r"\.\S+\Z")
    if p.match(symbol):
        return True
    else:
        return False

top_level_keyword_dict = {}

def top_level_keyword(name):
    name = convert_jojo_name(name)
    def decorator(fun):
        top_level_keyword_dict[name] = fun
        return fun
    return decorator

@top_level_keyword("import")
def k_import(module, body):
    module_name = convert_jojo_name(car(body))
    imported_module = importlib.import_module(module_name)
    imported_module_dict = getattr(module, 'imported_module_dict')
    imported_module_dict[module_name] = imported_module

@top_level_keyword("+jojo")
def plus_jojo(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, JOJO(compile_jo_list(module, cdr(body))))

@top_level_keyword("+macro")
def plus_macro(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, MACRO(compile_jo_list(module, cdr(body))))

keyword_dict = {}

def keyword(name):
    name = convert_jojo_name(name)
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

@keyword('begin')
def k_begin(module, body):
    return compile_jo_list(module, body)

@keyword('clo')
def k_clo(module, body):
    return [CLO(compile_jo_list(module, body))]

@keyword('if')
def k_if(module, body):
    jo_list = compile_jo_list(module, body)
    jo_list.append(IFTE)
    return jo_list

@keyword('quote')
def k_quote(module, body):
    jo_list = list_to_stack(body)
    return jo_list

prim_dict = {}

def prim(name):
    name = convert_jojo_name(name)
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

@prim('add')
def add(a, b):
    return a + b

@prim('sub')
def add(a, b):
    return a - b

@prim('equal?')
def equal_p(a, b):
    return a == b

@prim('eq?')
def eq_p(a, b):
    return a is b

prim('null')(null)
prim('null?')(null_p)

prim('cons')(cons)
prim('cons?')(cons_p)

prim('list?')(list_p)

prim('car')(car)
prim('cdr')(cdr)


