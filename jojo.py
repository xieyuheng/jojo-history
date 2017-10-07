import inspect
import types
import importlib
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

Vect = list

def vect_p(x):
    return type(x) == Vect

def string_p(x):
    return type(x) == str

class JOJO_ERROR(Exception):
    pass

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

def exe(vm):
    while vm.rs != []:
        exe_one_step(vm)
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
        raise JOJO_ERROR()

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
            raise JOJO_ERROR()
        arg_dict.update(top_of_ds)
    else:
        arg_dict = None

    if has_para_vect(parameters):
        top_of_ds = vm.ds.pop()
        if not vect_p(top_of_ds):
            print ("- exe_fun fail")
            print ("  when fun require a arg_vect")
            print ("  the top of data stack is not a vect")
            print ("  fun : {}".format(fun))
            print ("  top of data stack : {}".format(top_of_ds))
            raise JOJO_ERROR()
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

class JOJO:
    def __init__(self, body):
        self.length = len(body)
        self.body = Vect(body)
        self.lr = {}

    def jo_exe(self, rp, vm):
        vm.rs.append(RP(self))

class MACRO:
    def __init__(self, body):
        self.length = len(body)
        self.body = Vect(body)
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
    def jo_exe(self, rp, vm):
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

class CALL:
    def __init__(self, module, name):
        self.module = module
        self.name = name

    def jo_exe(self, rp, vm):
        jo = getattr(self.module, self.name)
        exe_jo(jo, rp, vm)

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

class MARK:
    @classmethod
    def jo_exe(self, rp, vm):
        vm.ds.append(self)

class COLLECT_VECT:
    @classmethod
    def jo_exe(self, rp, vm):
        vect = []
        while True:
            value = vm.ds.pop()
            if value == MARK:
                break
            else:
                vect.append(value)
        vect.reverse()
        vm.ds.append(vect)

class VECT_SPREAD:
    @classmethod
    def jo_exe(self, rp, vm):
        vect = vm.ds.pop()
        for value in vect:
            vm.ds.append(value)

class COLLECT_LIST:
    @classmethod
    def jo_exe(self, rp, vm):
        def recur(rest):
            value = vm.ds.pop()
            if value == MARK:
                return rest
            else:
                return recur(cons(value, rest))
        vm.ds.append(recur(null))

class LIST_SPREAD:
    @classmethod
    def jo_exe(self, rp, vm):
        def recur(l):
            if null_p(l):
                pass
            else:
                vm.ds.append(car(l))
                recur(cdr(l))
        recur(vm.ds.pop())

class DATA_PRED:
    def __init__(self, data):
        self.data = data

    def jo_exe(self, rp, vm):
        x = vm.ds.pop()
        vm.ds.append(type(x) == self.data)

class NEW:
    @classmethod
    def jo_exe(self, rp, vm):
        x = vm.ds.pop()
        if not class_p(x):
            print ("- NEW.jo_exe fail")
            print ("  argument is not a class : {}".format(x))
            raise JOJO_ERROR()
        if JOJO_DATA in x.__bases__:
            data_dict = {}
            for field_name in x.reversed_field_name_vect:
                data_dict[field_name] = vm.ds.pop()
            data_instance = x(data_dict)
            vm.ds.append(data_instance)
        else:
            exe_fun(x, vm)

class MSG:
    def __init__(self, message):
        self.message = message

    def jo_exe(self, rp, vm):
        o = vm.ds.pop()
        fun = getattr(o, self.message)
        exe_jo(fun, rp, vm)

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
                raise JOJO_ERROR()
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
        raise JOJO_ERROR()

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

def filter_name_vect(keyword, sexp_vect):
    name_vect = []
    for sexp in sexp_vect:
        if not cons_p(sexp):
            pass
        elif car(sexp) == keyword:
            body = cdr(sexp)
            name = car(body)
            name_vect.append(name)
    return name_vect

def compile_module(module_name, sexp_vect):
    module = types.ModuleType(module_name)
    setattr(module, 'jojo_name_vect',
            filter_name_vect('+jojo', sexp_vect))
    setattr(module, 'macro_name_vect',
            filter_name_vect('+macro', sexp_vect))
    setattr(module, 'imported_module_dict', {})
    for sexp in sexp_vect:
        if cons_p(sexp):
            top_level_keyword = car(sexp)
            fun = top_level_keyword_dict[top_level_keyword]
            fun(module, cdr(sexp))
    return module

def sexp_list_emit(module, sexp_list):
    jo_vect = []
    while not null_p(sexp_list):
        sexp = car(sexp_list)
        jo_vect.extend(sexp_emit(module, sexp))
        sexp_list = cdr(sexp_list)
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

    if keyword in macro_dict.keys():
        fun = macro_dict[keyword]
        new_sexp = fun(cdr(cons))
        return sexp_emit(module, new_sexp)

    macro_name_vect = getattr(module, 'macro_name_vect')
    if keyword in macro_name_vect:
        if not hasattr(module, keyword):
            print ("- cons_emit fail")
            print ("  must define a macro before using it")
            print ("  macro name : {}".format(keyword))
            raise JOJO_ERROR()
        else:
            macro = getattr(module, keyword)
            vm = vm([cdr(cons)],
                    [RP(macro)])
            vm = vm.exe()
            new_sexp = vm.ds[0]
            return sexp_emit(module, new_sexp)

    else:
        print("- cons_emit fail")
        print("  meet unknown keyword : {}".format(keyword))
        raise JOJO_ERROR()

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

    if string == 'mark':
        return [MARK]
    if string == 'collect-vect':
        return [COLLECT_VECT]
    if string == 'vect-spread':
        return [VECT_SPREAD]
    if string == 'collect-list':
        return [COLLECT_LIST]
    if string == 'list-spread':
        return [LIST_SPREAD]

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
    raise JOJO_ERROR()

def int_string_p(string):
    length = len(string)
    if length == 0:
        return False
    elif string[0] == '-':
        return nat_string_p(string[1:length-1])
    else:
        return nat_string_p(string)

def nat_string_p(string):
    return string.isdecimal()

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
    elif string[0] != ':':
        return False
    elif string[len(string)-1] == '!':
        return False
    else:
        return True

def set_local_string_p(string):
    if len(string) <= 2:
        return False
    elif string[0] != ':':
        return False
    elif string[len(string)-1] != '!':
        return False
    else:
        return True

def message_string_p(string):
    if len(string) <= 1:
        return False
    elif string[0] != '.':
        return False
    else:
        return True

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

@prim('int-write')
def int_write(i):
    write(i)

@prim('true')
def true():
    return True

@prim('false')
def false():
    return False

@prim('not')
def p_not(b):
    return not b

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

@prim('string-write')
def string_write(string):
    write(string)

prim('vect?')(vect_p)

def vect_copy(vect):
    return vect[:]

@prim('vect->sexp')
def vect_to_sexp(vect):
    if vect == []:
        return null
    elif not vect_p(vect):
        return vect
    else:
        return cons(vect_to_sexp(vect[0]),
                    vect_to_sexp(vect[1:]))

@prim('vect->list')
def vect_to_list(vect):
    if vect == []:
        return null
    else:
        return cons(vect[0], vect_to_list(vect[1:]))

@prim('list->vect')
def list_to_vect(l):
    vect = []
    while not null_p(l):
        vect.append(car(l))
        l = cdr(l)
    return vect

@prim('list-length')
def list_length(l):
    if null_p(l):
        return 0
    else:
        return list_length(cdr(l)) + 1

@prim('list-ref')
def list_ref(l, i):
    if null_p(l):
        print ("- list_ref fail")
        print ("  index greater then length of list")
        raise JOJO_ERROR()
    elif i == 0:
        return car(l)
    else:
        return list_ref(cdr(l), i-1)

@prim('list-append')
def list_append(ante, succ):
    if null_p(ante):
        return succ
    else:
        return cons(car(ante),
                    list_append(cdr (ante), succ))

@prim('tail-cons')
def tail_cons(ante, value):
    return list_append(ante, cons(value, null))

prim('print')(write)

@prim('newline')
def newline():
    print ("")

prim('nl')(newline)

@prim('space')
def newline():
    write(" ")

top_level_keyword_dict = {}

def top_level_keyword(name):
    def decorator(fun):
        top_level_keyword_dict[name] = fun
        return fun
    return decorator

@top_level_keyword("note")
def top_level_note(module, body):
    pass

@top_level_keyword("import")
def k_import(module, body):
    module_name = car(body)
    imported_module = importlib.import_module(module_name)
    imported_module_dict = getattr(module, 'imported_module_dict')
    imported_module_dict[module_name] = imported_module

@top_level_keyword("+jojo")
def plus_jojo(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name,
            JOJO(sexp_list_emit(module, cdr(body))))

@top_level_keyword("+macro")
def plus_macro(module, body):
    jojo_name = car(body)
    setattr(module, jojo_name,
            MACRO(sexp_list_emit(module, cdr(body))))

class JOJO_DATA:
    pass

def create_data_class(data_name, field_name_vect):
    rev = vect_copy(field_name_vect)
    rev.reverse()
    def init(self, kwargs):
        self.__dict__.update(kwargs)
    def update_ns(ns):
        ns.update({
            '__init__' : init,
            'field_name_vect': field_name_vect,
            'reversed_field_name_vect': rev,
        })
    return types.new_class(
        data_name,
        bases = (JOJO_DATA, ),
        kwds = None,
        exec_body = update_ns)

@top_level_keyword("+data")
def plus_data(module, body):
    data_name = car(body)

    field_name_vect = []
    for string in list_to_vect(cdr(body)):
        if message_string_p(string):
            string = string[1:len(string)]
            field_name_vect.append(string)

    data = create_data_class(data_name, field_name_vect)
    data.__module__ = module

    jojo_name_vect = getattr(module, 'jojo_name_vect')

    jojo_name_vect.append(data_name)
    setattr(module, data_name, data)

    constructor_name = data_name[1:-1]
    jojo_name_vect.append(constructor_name)
    setattr(module, constructor_name, JOJO([data, NEW]))

    predicate_name = "".join([constructor_name, "?"])
    jojo_name_vect.append(predicate_name)
    setattr(module, predicate_name, DATA_PRED(data))

keyword_dict = {}

def keyword(name):
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

@keyword('begin')
def k_begin(module, body):
    return sexp_list_emit(module, body)

@keyword('clo')
def k_clo(module, body):
    return [CLO(sexp_list_emit(module, body))]

@keyword('if')
def k_if(module, body):
    jo_vect = sexp_list_emit(module, body)
    jo_vect.append(IFTE)
    return jo_vect

@keyword('quote')
def k_quote(module, body):
    jo_vect = list_to_vect(body)
    return jo_vect

@keyword('partquote')
def k_partquote(module, sexp_list):
    jo_vect = []
    while not null_p(sexp_list):
        sexp = car(sexp_list)
        jo_vect.extend(k_partquote_one(module, sexp))
        sexp_list = cdr(sexp_list)
    return jo_vect

def k_partquote_one(module, sexp):
    if cons_p(sexp):
        if car(sexp) == '@':
            return sexp_list_emit(module, cdr(sexp))
        else:
            jo_vect = []
            jo_vect.extend([MARK])
            jo_vect.extend(k_partquote(module, sexp))
            jo_vect.extend([COLLECT_LIST])
            return jo_vect
    else:
        return [sexp]

@keyword('->')
def k_arrow(module, sexp_list):
    jo_vect = []
    while not null_p(sexp_list):
        sexp = car(sexp_list)
        if not string_p(sexp):
            pass
        elif sexp == '--':
            break
        elif local_string_p(sexp):
            jo_vect.append(SET(sexp))
        else:
            pass
        sexp_list = cdr(sexp_list)
    jo_vect.reverse()
    return jo_vect

@keyword('list')
def k_list(module, sexp_list):
    jo_vect = []
    jo_vect.extend([MARK])
    jo_vect.extend(sexp_list_emit(module, sexp_list))
    jo_vect.extend([COLLECT_LIST])
    return jo_vect

@keyword('vect')
def k_vect(module, sexp_list):
    jo_vect = []
    jo_vect.extend([MARK])
    jo_vect.extend(sexp_list_emit(module, sexp_list))
    jo_vect.extend([COLLECT_VECT])
    return jo_vect

macro_dict = {}

def macro(name):
    def decorator(fun):
        macro_dict[name] = fun
        return fun
    return decorator

@macro('cond')
def k_cond(body):
    def recur(rest):
        if list_length(rest) == 2:
            q = list_ref(rest, 0)
            a = list_ref(rest, 1)
            if q == 'else':
                return a
            else:
                return vect_to_sexp(
                    ['begin',
                     q, ['clo', a],
                     ['clo',
                      ['quote', body],
                      'report-cond-mismatch'],
                     'ifte'])
        else:
            q = list_ref(rest, 0)
            a = list_ref(rest, 1)
            return vect_to_sexp(
                ['begin',
                 q, ['clo', a],
                 ['clo', recur(cdr(cdr(rest)))],
                 'ifte'])
    return recur(body)

@prim('report-cond-mismatch')
def report_cond_mismatch(body):
    print ("- cond mismatch")
    write ("  body : ")
    write_sexp(body)
    print ("")
    raise JOJO_ERROR()

def load(path):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        print ("- load fail")
        print ("  path does not exist")
        print ("  path : {}".format(path))
        raise JOJO_ERROR()

    if not os.path.isfile(path):
        print ("- load fail")
        print ("  path is not file")
        print ("  path : {}".format(path))
        raise JOJO_ERROR()

    with open(path, "r") as f:
        code = f.read()
        sexp_vect = parse_sexp_vect(scan_string_vect(code))
        module = compile_module(path, sexp_vect)

    module.__file__ = path

    return module

def run(data_stack, jojo_dict):
    data_stack = vect_copy(data_stack)
    for jojo in jojo_dict:
        run_one(data_stack, jojo)
    return data_stack

def run_one(data_stack, jojo):
    vm = VM(data_stack,
            [RP(jojo)])
    vm = vm.exe()
