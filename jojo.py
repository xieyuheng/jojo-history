import inspect
import types
import importlib
import re

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
        self.body = list(body)
        self.lr = {}

    def jo_exe(self, rp, vm):
        vm.rs.append(RP(self))

class MACRO:
    def __init__(self, body):
        self.length = len(body)
        self.body = list(body)
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

    if has_para_list(parameters):
        top_of_ds = vm.ds.pop()
        if not isinstance(top_of_ds, list):
            print ("- exe_fun fail")
            print ("  when fun require a arg_list")
            print ("  the top of data stack is not a list")
            print ("  fun : {}".format(fun))
            print ("  top of data stack : {}".format(top_of_ds))
        arg_list = top_of_ds
    else:
        arg_list = []

    positional_para_length = get_positional_para_length(parameters)
    args = []
    i = 0
    while i < positional_para_length:
        args.append(vm.ds.pop())
        i = i + 1
    args.reverse()
    args.extend(arg_list)

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

def has_para_list(parameters):
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

def scan_symble_list(string):
    symbol_list = []
    i = 0
    length = len(string)
    while i < length:
        s = string[i]

        if space_p(s):
            i = i + 1

        elif delimiter_p(s):
            symbol_list.append(s)
            i = i + 1

        elif doublequote_p(s):
            doublequote_end_index = string.find('"', i+1)
            if doublequote_end_index == -1:
                print ("- scan_symble_list fail")
                print ("  doublequote mismatch")
                print ("  string : {}".format(string))
            end = doublequote_end_index + 1
            symbol = string[i:end]
            symbol_list.append(symbol)
            i = end

        else:
            end = find_end(string, i+1)
            symbol = string[i:end]
            symbol_list.append(symbol)
            i = end

    return symbol_list

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

def parse_sexp_list(symbol_list):
    length = len(symbol_list)
    i = 0
    sexp_list = []
    while i < length:
       s, i = parse_sexp(symbol_list, i)
       sexp_list.append(s)
    return sexp_list

def parse_sexp(symbol_list, i):
    symbol = symbol_list[i]
    if symbol == '(':
        return parse_sexp_cons_until_ket(symbol_list, i+1, ')')
    elif symbol == '[':
        s_cons, i1 = parse_sexp_cons_until_ket(symbol_list, i+1, ']')
        return (cons('begin', s_cons), i1)
    elif symbol == '{':
        s_cons, i1 = parse_sexp_cons_until_ket(symbol_list, i+1, '}')
        return (cons('clo', s_cons), i1)
    elif symbol == "'":
        s, i1 = parse_sexp(symbol_list, i+1)
        return (cons('quote', cons(s, null)), i1)
    elif symbol == "`":
        s, i1 = parse_sexp(symbol_list, i+1)
        return (cons('partquote', cons(s, null)), i1)
    else:
        return (symbol, i+1)

def parse_sexp_cons_until_ket(symbol_list, i, ket):
    symbol = symbol_list[i]
    if symbol == ket:
        return (null, i+1)
    else:
        s, i1 = parse_sexp(symbol_list, i)
        s_cons, i2 = \
            parse_sexp_cons_until_ket(symbol_list, i1, ket)
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


