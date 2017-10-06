import inspect
import types
import importlib
import re
import sys
import os

def get_signature(fun):
    try:
        return inspect.signature(fun)
    except ValueError:
        return False

def fun_p(x):
    if (isinstance(x, types.LambdaType) or
        isinstance(x, types.MethodType)):
        return True
    elif (isinstance(x, types.BuiltinFunctionType) or
          isinstance(x, types.BuiltinMethodType)):
        return get_signature(x)
    else:
        return False

def class_p(x):
    if not inspect.isclass(x):
        return False
    elif x == type:
        return False
    else:
        return True

vect = list
stack = list

class RP:
    def __init__(self, fun):
        self.cursor = 0
        self.length = fun.length
        self.body = fun.body
        self.lr = fun.lr.copy()

class VM:
    def __init__(self, ds, rs):
        self.ds = ds
        self.rs = rs

    def exe(self):
        return exe(self)

def push_result_to_vm(result, vm):
    if type(result) == tuple:
        vm.ds.extend(result)
    elif result == None:
        pass
    else:
        vm.ds.append(result)

class GET:
    def __init__(self, name):
        self.name = name

    def jo_exe(self, rp, vm):
        value = rp.lr[self.name]
        vm.ds.append(value)

class SET:
    def __init__(self, name):
        self.name = name

    def jo_exe(self, rp, vm):
        value = vm.ds.pop()
        rp.lr[self.name] = value

class JOJO:
    def __init__(self, body):
        self.length = len(body)
        self.body = vect(body)
        self.lr = {}

    def jo_exe(self, rp, vm):
        vm.rs.append(RP(self))

class MACRO:
    def __init__(self, body):
        self.length = len(body)
        self.body = vect(body)
        self.lr = {}

    def jo_exe(self, rp, vm):
        vm.rs.append(RP(self))

class CLO:
    def __init__(self, body):
        self.body = body

    def jo_exe(self, rp, vm):
        new_jojo = JOJO(self.body)
        new_jojo.lr = rp.lr
        vm.ds.append(new_jojo)

class APPLY:
    @classmethod
    def jo_exe(cls, rp, vm):
        clo = vm.ds.pop()
        clo.jo_exe(rp, vm)

class IFTE:
    @classmethod
    def jo_exe(self, rp, vm):
        clo2 = vm.ds.pop()
        clo1 = vm.ds.pop()
        test = vm.ds.pop()
        if test:
            vm.rs.append(RP(clo1))
        else:
            vm.rs.append(RP(clo2))

class MSG:
    def __init__(self, message):
        self.message = message

    def jo_exe(self, rp, vm):
        o = vm.ds.pop()
        fun = getattr(o, self.message)
        exe_jo(fun, rp, vm)

class NEW:
    @classmethod
    def jo_exe(self, rp, vm):
        c = vm.ds.pop()
        if not class_p(c):
            print ("- NEW.jo_exe fail")
            print ("  argument is not a class : {}".format(c))
        exe_fun(c, vm)

class CALL:
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def jo_exe(self, rp, vm):
        jo = getattr(self.module, self.name)
        exe_jo(jo, rp, vm)

def exe(vm):
    while vm.rs != []:
        exe_one_step(vm)
        print (vm.ds)
    print ("- exe end")
    return vm

def exe_one_step(vm):
    rp = vm.rs.pop()
    jo = rp.body[rp.cursor]

    # handle tail call
    if rp.cursor >= rp.length - 1:
       pass
    else:
       rp.cursor = rp.cursor + 1
       vm.rs.append(rp)

    # dispatching
    exe_jo(jo, rp, vm)

def exe_jo(jo, rp, vm):
    if fun_p(jo):
        exe_fun(jo, vm)
    elif hasattr(jo, "jo_exe"):
        jo.jo_exe(rp, vm)
    else:
        vm.ds.append(jo)

def exe_fun(fun, vm):
    signature = get_signature(fun)

    if not signature:
        print ("- exe_fun fail to get signature")
        print ("  fun : {}".format(fun))

    parameters = signature.parameters

    if has_para_dict(parameters):
        arg_dict = get_default_arg_dict(parameters)
        top_of_ds = vm.ds.pop()
        if not isinstance(top_of_ds, dict):
            print ("- exe_fun fail")
            print ("  when fun require a arg_dict")
            print ("  the top of data stack is not a dict")
            print ("  fun : {}".format(fun))
            print ("  top of data stack : {}".format(top_of_ds))
        arg_dict.update(top_of_ds)
    else:
        arg_dict = None

    if has_para_vect(parameters):
        top_of_ds = vm.ds.pop()
        if not isinstance(top_of_ds, vect):
            print ("- exe_fun fail")
            print ("  when fun require a arg_vect")
            print ("  the top of data stack is not a vect")
            print ("  fun : {}".format(fun))
            print ("  top of data stack : {}".format(top_of_ds))
        arg_vect = top_of_ds
    else:
        arg_vect = []

    positional_para_length = get_positional_para_length(parameters)
    args = []
    i = 0
    while i < positional_para_length:
        args.append(vm.ds.pop())
        i = i + 1
    args.reverse()
    args.extend(arg_vect)

    if arg_dict == None:
        result = fun(*args)
    else:
        result = fun(*args, **arg_dict)

    push_result_to_vm(result, vm)

def get_positional_para_length(parameters):
    n = 0
    for v in parameters.values():
        if (v.kind == inspect.Parameter.POSITIONAL_ONLY or
            v.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD):
            n = n + 1
    return n

def has_para_vect(parameters):
    for v in parameters.values():
        if (v.kind == inspect.Parameter.VAR_POSITIONAL):
            return True
    return False

def has_para_dict(parameters):
    for v in parameters.values():
        if (v.kind == inspect.Parameter.KEYWORD_ONLY or
            v.kind == inspect.Parameter.VAR_KEYWORD):
            return True
    return False

def get_default_arg_dict(parameters):
    default_dict = {}
    for v in parameters.values():
        if (v.kind == inspect.Parameter.KEYWORD_ONLY and
            v.default != inspect.Parameter.empty):
            default_dict[v.name] = v.default
    return default_dict

def scan_string_vect(string):
    string_vect = []
    i = 0
    length = len(string)
    while i < length:
        s = string[i]

        if space_p(s):
            i = i + 1

        elif delimiter_p(s):
            string_vect.append(s)
            i = i + 1

        elif doublequote_p(s):
            doublequote_end_index = string.find('"', i+1)
            if doublequote_end_index == -1:
                print ("- scan_string_vect fail")
                print ("  doublequote mismatch")
                print ("  string : {}".format(string))
            end = doublequote_end_index + 1
            string_vect.append(string[i:end])
            i = end

        else:
            end = find_end(string, i+1)
            string_vect.append(string[i:end])
            i = end

    return string_vect

def find_end(string, begin):
    length = len(string)
    i = begin
    while True:
       if i == length:
           return i
       s = string[i]
       if space_p(s) or delimiter_p(s) or doublequote_p(s):
           return i
       i = i + 1

def space_p(s):
    return s.isspace()

def delimiter_p(s):
    return (s == '(' or
            s == ')' or
            s == '[' or
            s == ']' or
            s == '{' or
            s == '}' or
            s == ',' or
            s == '`' or
            s == "'")

def doublequote_p(s):
    return s == '"'

class Null:
    pass

null = Null()

def null_p(x):
    return x == null

class Cons:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

def cons(car, cdr):
    if list_p(cdr):
        return Cons(car, cdr)
    else:
        print ("- cons fail")
        print ("  cdr of cons must be a cons or null")
        print ("  cdr : {}".format(cdr))

def cons_p(x):
    return isinstance(x, Cons)

def list_p(x):
    return null_p(x) or cons_p(x)

def cdr(x):
    return x.cdr

def car(x):
    return x.car

def parse_sexp_vect(string_vect):
    length = len(string_vect)
    i = 0
    sexp_vect = []
    while i < length:
       s, i = parse_sexp(string_vect, i)
       sexp_vect.append(s)
    return sexp_vect

def parse_sexp(string_vect, i):
    string = string_vect[i]
    if string == '(':
        return parse_sexp_cons_until_ket(string_vect, i+1, ')')
    elif string == '[':
        s_cons, i1 = parse_sexp_cons_until_ket(string_vect, i+1, ']')
        return (cons('begin', s_cons), i1)
    elif string == '{':
        s_cons, i1 = parse_sexp_cons_until_ket(string_vect, i+1, '}')
        return (cons('clo', s_cons), i1)
    elif string == "'":
        s, i1 = parse_sexp(string_vect, i+1)
        return (cons('quote', cons(s, null)), i1)
    elif string == "`":
        s, i1 = parse_sexp(string_vect, i+1)
        return (cons('partquote', cons(s, null)), i1)
    else:
        return (string, i+1)

def parse_sexp_cons_until_ket(string_vect, i, ket):
    string = string_vect[i]
    if string == ket:
        return (null, i+1)
    else:
        s, i1 = parse_sexp(string_vect, i)
        s_cons, i2 = \
            parse_sexp_cons_until_ket(string_vect, i1, ket)
        return (cons(s, s_cons), i2)

def write(x):
    print(x, end="")

def write_sexp(s):
    if null_p(s):
        write ("null")
    elif cons_p(s):
        write ("(")
        write_sexp_cons(s)
        write (")")
    else:
        write (s)

def write_sexp_cons(s_cons):
    if null_p(s_cons):
        pass
    elif null_p(cdr(s_cons)):
        write_sexp(car(s_cons))
    else:
        write_sexp(car(s_cons))
        write (" ")
        write_sexp_cons(cdr(s_cons))

def list_length(l):
    if null_p(l):
        return 0
    else:
        return list_length(cdr(l)) + 1

def list_ref(l, i):
    if null_p(l):
        print ("- list_ref fail")
        print ("  index greater then length of list")
    elif i == 0:
        return car(l)
    else:
        return list_ref(cdr(l), i-1)

def list_append(ante, succ):
    if null_p(ante):
        return succ
    else:
        return cons(car(ante),
                    list_append(cdr (ante), succ))

def tail_cons(ante, value):
    return list_append(ante, cons(value, null))

def list_to_vect(l):
    stack = []
    while not null_p(l):
        stack.append(car(l))
        l = cdr(l)
    return stack

def get_jojo_name_vect(sexp_vect):
    jojo_name_vect = []
    for sexp in sexp_vect:
        if not cons_p(sexp):
            pass
        elif car(sexp) == '+jojo':
            body = cdr(sexp)
            jojo_name = car(body)
            jojo_name_vect.append(jojo_name)
    return jojo_name_vect

def get_macro_name_vect(sexp_vect):
    macro_name_vect = []
    for sexp in sexp_vect:
        if not cons_p(sexp):
            pass
        elif car(sexp) == '+macro':
            body = cdr(sexp)
            macro_name = car(body)
            macro_name_vect.append(macro_name)
    return macro_name_vect

def compile_module(module_name, sexp_vect):
    module = types.ModuleType(module_name)
    setattr(module, 'jojo_name_vect',
            get_jojo_name_vect(sexp_vect))
    setattr(module, 'macro_name_vect',
            get_macro_name_vect(sexp_vect))
    setattr(module, 'imported_module_dict', {})
    for sexp in sexp_vect:
        if cons_p(sexp):
            top_level_keyword = car(sexp)
            fun = top_level_keyword_dict[top_level_keyword]
            fun(module, cdr(sexp))
    return module

def sexp_vect_emit(module, sexp_vect):
    jo_vect = []
    while not null_p(sexp_vect):
        sexp = car(sexp_vect)
        jo_vect.extend(sexp_emit(module, sexp))
        sexp_vect = cdr(sexp_vect)
    return jo_vect

def sexp_emit(module, sexp):
    if null_p(sexp):
        return null_emit(module, sexp)
    elif cons_p(sexp):
        return cons_emit(module, sexp)
    else:
        return string_emit(module, sexp)

def null_emit(module, sexp):
    return [null]

def cons_emit(module, cons):
    keyword = car(cons)

    if keyword in keyword_dict.keys():
        fun = keyword_dict[keyword]
        return fun(module, cdr(cons))

    macro_name_vect = getattr(module, "macro_name_vect")

    if keyword in macro_name_vect:
        if not hasattr(module, keyword):
            print ("- cons_emit fail")
            print ("  must define a macro before using it")
            print ("  macro name : {}".format(keyword))
            return
        else:
            macro = getattr(module, keyword)
            vm = vm([cdr(cons)],
                    [RP(macro)])
            vm = vm.exe()
            new_cons = vm.ds[0]
            return cons_emit(module, new_cons)

    else:
        print("- cons_emit fail")
        print("  meet unknown keyword : {}".format(keyword))
        return

def string_emit(module, string):

    if int_string_p(string):
        return [int(string)]

    if doublequoted_string_p(string):
        string = string[1:len(string)-1]
        return [string]

    if local_string_p(string):
        return [GET(string)]
    if set_local_string_p(string):
        string = string[:len(string)-1]
        return [SET(string)]

    if message_string_p(string):
        string = string[1:len(string)]
        return [MSG(string)]

    if string == 'apply':
        return [APPLY]
    if string == 'ifte':
        return [IFTE]
    if string == 'new':
        return [NEW]
    if string == ',':
        return []

    jojo_name_vect = getattr(module, 'jojo_name_vect')
    if string in jojo_name_vect:
        return [CALL(module, string)]

    imported_module_dict = getattr(module, 'imported_module_dict')
    if string in imported_module_dict.keys():
        imported_module = imported_module_dict[string]
        return [imported_module]

    if string in prim_dict.keys():
        return [prim_dict[string]]

    print ("- string_emit fail")
    print ("  meet undefined string : {}".format(string))

def int_string_p(string):
    p = re.compile(r"-?[0-9]+\Z")
    if p.match(string):
        return True
    else:
        return False

def doublequoted_string_p(string):
    if len(string) <= 2:
        return False
    elif string[0] != '"':
        return False
    elif string[len(string)-1] != '"':
        return False
    else:
        return True

def local_string_p(string):
    if len(string) <= 1:
        return False
    if string[0] != ':':
        return False
    if string[len(string)-1] == '!':
        return False
    else:
        return True

def set_local_string_p(string):
    if len(string) <= 2:
        return False
    if string[0] != ':':
        return False
    if string[len(string)-1] != '!':
        return False
    else:
        return True

def message_string_p(string):
    p = re.compile(r"\.\S+\Z")
    if p.match(string):
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
    setattr(module, jojo_name, JOJO(sexp_vect_emit(module, cdr(body))))

@top_level_keyword("+macro")
def plus_macro(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name, MACRO(sexp_vect_emit(module, cdr(body))))

@top_level_keyword("note")
def top_level_note(module, body):
    pass

keyword_dict = {}

def keyword(name):
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

@keyword('begin')
def k_begin(module, body):
    return sexp_vect_emit(module, body)

@keyword('clo')
def k_clo(module, body):
    return [CLO(sexp_vect_emit(module, body))]

@keyword('if')
def k_if(module, body):
    jo_vect = sexp_vect_emit(module, body)
    jo_vect.append(IFTE)
    return jo_vect

@keyword('quote')
def k_quote(module, body):
    jo_vect = list_to_vect(body)
    return jo_vect

@keyword('cond')
def k_cond(module, body):
    pass

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

@prim('add')
def add(a, b):
    return a + b

@prim('sub')
def sub(a, b):
    return a - b

@prim('mul')
def mul(a, b):
    return a * b

@prim('true')
def true():
    return True

@prim('false')
def false():
    return False

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

prim('sexp-write')(write_sexp)
prim('sexp-list-write')(write_sexp_cons)

prim('list-length')(list_length)
prim('list-ref')(list_ref)
prim('list-append')(list_append)
prim('tail-cons')(tail_cons)



def create_module(name, path):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        print ("- create_module fail")
        print ("  path does not exist")
        print ("  path : {}".format(path))
        return

    if not os.path.isfile(path):
        print ("- create_module fail")
        print ("  path is not file")
        print ("  path : {}".format(path))
        return

    with open(path, "r") as f:
        code = f.read()
        sexp_vect = parse_sexp_vect(scan_string_vect(code))
        module = compile_module(name, sexp_vect)

    module.__file__ = path

    return module


