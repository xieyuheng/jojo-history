import inspect
import types

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
