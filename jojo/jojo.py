import inspect
import types
import importlib
import sys
import os
import itertools
import collections
import operator
import traceback
import pprint
import time
import multiprocessing as mp
import queue
import random

def get_signature(fun):
    try:
        return inspect.signature(fun)
    except ValueError:
        return None

def fun_p(x):
    if (isinstance(x, types.LambdaType) or
        isinstance(x, types.MethodType)):
        return True
    elif (isinstance(x, types.BuiltinFunctionType) or
          isinstance(x, types.BuiltinMethodType)):
        if get_signature(x) == None:
            return False
        else:
            return True
    else:
        return False

def method_p(x):
    if isinstance(x, types.MethodType):
        return True
    elif isinstance(x, types.BuiltinMethodType):
        if get_signature(x) == None:
            return False
        else:
            return True
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

def fill_vect(value, length):
    vect = []
    i = 0
    while i < length:
        vect.append(value)
        i = i + 1
    return vect

def fill_tuple(value, length):
    return tuple(fill_vect(value, length))

class JOJO_ERROR(Exception):
    pass

def error():
    raise JOJO_ERROR()

class RP:
    def __init__(self, jojo):
        self.cursor = 0
        self.length = jojo.length
        self.body = jojo.body
        self.lr = jojo.lr.copy()

class VM:
    def __init__(self, ds, rs):
        self.ds = ds
        self.rs = rs

    def exe(self):
        length = len(self.rs)
        while len(self.rs) >= length:
            self.exe_one_step()
        return self

    def exe_one_step(self):
        rp = self.rs.pop()
        # handle empty closure
        if rp.length == 0:
            # one rp is finished
            return
        # get current jo
        jo = rp.body[rp.cursor]
        # handle tail call
        if rp.cursor >= rp.length - 1:
            # dispatching
            exe_jo(jo, rp, self)
            # one rp is finished
            return
        else:
            rp.cursor = rp.cursor + 1
            self.rs.append(rp)
            # dispatching
            exe_jo(jo, rp, self)

class VALUES:
    def __init__(self, *values):
        self.values = values

def exe_jo(jo, rp, vm):
    if fun_p(jo):
        exe_fun(jo, vm)
    elif hasattr(jo, "jo_exe"):
        jo.jo_exe(rp, vm)
    else:
        vm.ds.append(jo)

def exe_fun(fun, vm):
    signature = get_signature(fun)

    if signature == None:
        print("- exe_fun fail to get signature")
        print("  fun : {}".format(fun))
        error()

    parameters = signature.parameters

    if has_para_dict(parameters):
        arg_dict = get_default_arg_dict(parameters)
        top_of_ds = vm.ds.pop()
        if not isinstance(top_of_ds, dict):
            print("- exe_fun fail")
            print("  when fun require a arg_dict")
            print("  the top of data stack is not a dict")
            print("  fun : {}".format(fun))
            print("  top of data stack : {}".format(top_of_ds))
            error()
        arg_dict.update(top_of_ds)
    else:
        arg_dict = None

    if has_para_vect(parameters):
        top_of_ds = vm.ds.pop()
        if not vect_p(top_of_ds):
            print("- exe_fun fail")
            print("  when fun require a arg_vect")
            print("  the top of data stack is not a vect")
            print("  fun : {}".format(fun))
            print("  top of data stack : {}".format(top_of_ds))
            error()
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

def push_result_to_vm(result, vm):
    if type(result) == VALUES:
        vm.ds.extend(result.values)
    elif result == None:
        return
    else:
        vm.ds.append(result)

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

def get_positional_default_arg_dict(parameters):
    default_dict = {}
    for v in parameters.values():
        if ((v.kind == inspect.Parameter.POSITIONAL_ONLY or
             v.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD)
            and v.default != inspect.Parameter.empty):
            default_dict[v.name] = v.default
    return default_dict

class JOJO:
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

    def jo_print(self):
        p_print("(clo ")
        for jo in self.body[:-1]:
            jo_print(jo)
            space()
        jo_print(self.body[-1])
        p_print(")")

class APPLY:
    @classmethod
    def jo_exe(self, rp, vm):
        clo = vm.ds.pop()
        clo.jo_exe(rp, vm)

    @classmethod
    def jo_print(self):
        p_print("apply")

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

    @classmethod
    def jo_print(self):
        p_print("ifte")

class CALL_FROM_MODULE:
    def __init__(self, module_name, name):
        self.module_name = module_name
        self.name = name

    def jo_exe(self, rp, vm):
        module = sys.modules[self.module_name]
        jo = getattr(module, self.name)
        exe_jo(jo, rp, vm)

    def jo_print(self):
        # p_print("(call {} from {})".format(self.name, self.module.__name__))
        p_print(self.name)

class GET:
    def __init__(self, name):
        self.name = name

    def jo_exe(self, rp, vm):
        jo = rp.lr[self.name]
        exe_jo(jo, rp, vm)

    def jo_print(self):
        p_print(self.name)

class SET:
    def __init__(self, name):
        self.name = name

    def jo_exe(self, rp, vm):
        value = vm.ds.pop()
        rp.lr[self.name] = value

    def jo_print(self):
        p_print(self.name)
        p_print('!')

class MARK:
    @classmethod
    def jo_exe(self, rp, vm):
        vm.ds.append(self)

    @classmethod
    def jo_print(self):
        p_print("mark")

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

    @classmethod
    def jo_print(self):
        p_print("collect-vect")

class VECT_SPREAD:
    @classmethod
    def jo_exe(self, rp, vm):
        vect = vm.ds.pop()
        for value in vect:
            vm.ds.append(value)

    @classmethod
    def jo_print(self):
        p_print("vect-spread")

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

    @classmethod
    def jo_print(self):
        p_print("collect-list")

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

    @classmethod
    def jo_print(self):
        p_print("list-spread")

class DATA_PRED:
    def __init__(self, data_class):
        self.data_class = data_class

    def jo_exe(self, rp, vm):
        x = vm.ds.pop()
        vm.ds.append(type(x) == self.data_class)

    def jo_print(self):
        p_print(data_class.__name__)
        p_print('?')

class NEW:
    @classmethod
    def jo_exe(self, rp, vm):
        x = vm.ds.pop()
        if not class_p(x):
            print("- NEW.jo_exe fail")
            print("  argument is not a class : {}".format(x))
            error()
        else:
            exe_fun(x, vm)

    @classmethod
    def jo_print(self):
        p_print("new")

class MSG:
    def __init__(self, message):
        self.message = message

    def jo_exe(self, rp, vm):
        o = vm.ds.pop()
        v = getattr(o, self.message)
        if method_p(v):
            exe_fun(v, vm)
        else:
            exe_jo(v, rp, vm)

    def jo_print(self):
        p_print(".")
        p_print(self.message)

class SET_FIELD:
    def __init__(self, field_name):
        self.field_name = field_name

    def jo_exe(self, rp, vm):
        o = vm.ds.pop()
        v = vm.ds.pop()
        setattr(o, self.field_name, v)

    def jo_print(self):
        p_print(".")
        p_print(self.field_name)
        p_print("!")

class GENE:
    def __init__(self, arity, default_jojo):
        self.arity = arity
        self.default_jojo = default_jojo
        self.disp_dict = {}

    def jo_exe(self, rp, vm):
        value_vect = vm.ds[(- self.arity):]
        type_vect = []
        for value in value_vect:
            type_vect.append(type(value))

        type_tuple = tuple(type_vect)
        if type_tuple in self.disp_dict:
            jojo = self.disp_dict[type_tuple]
            jojo.jo_exe(rp, vm)
        else:
            self.default_jojo.jo_exe(rp, vm)

class CLEAR:
    @classmethod
    def jo_exe(self, rp, vm):
        vm.ds = []

    @classmethod
    def jo_print(self):
        p_print("clear")

class PRIMITIVE:
    def __init__(self, fun):
        self.fun = fun

    def jo_exe(self, rp, vm):
        vm.ds.append(self.fun)

    def jo_print(self):
        p_print(self.fun)

class Aid:
    def __init__(self, sid, key):
        self.sid = sid # natural number
        self.key = key
    def __eq__(self, other):
        return (self.sid == other.sid and
                self.key == other.key)
    def __hash__(self):
        return hash((self.sid, self.key))
    def __repr__(self):
        return "<aid:(sid:{}, key:{})>" \
            .format(self.sid, self.key)

class Actor:
    def __init__(self, scheduler, vm):
        self.scheduler = scheduler
        self.vm = vm
        self.ds = vm.ds
        self.rs = vm.rs
        self.mq = queue.Queue()
        self.aid = generate_aid(scheduler)
        scheduler.actor_dict[self.aid.key] = self
        scheduler.active_queue.put(self)

    def finished_p(self):
        return len(self.rs) == 0

    def exe_one_step(self):
        rp = self.rs.pop()
        # handle empty closure
        if rp.length == 0:
            # one rp is finished
            return
        # get current jo
        jo = rp.body[rp.cursor]
        # handle tail call
        if rp.cursor >= rp.length - 1:
            # dispatching
            act_jo(jo, rp, self)
            # one rp is finished
            return
        else:
            rp.cursor = rp.cursor + 1
            self.rs.append(rp)
            # dispatching
            act_jo(jo, rp, self)

def generate_aid(scheduler):
    sid = scheduler.sid
    key = scheduler._actor_counter
    scheduler._actor_counter = key + 1
    return Aid(sid, key)

def act_jo(jo, rp, actor):
    if hasattr(jo, "jo_act"):
        jo.jo_act(rp, actor)
    else:
        exe_jo(jo, rp, actor)
        actor.scheduler.active_queue.put(actor)

class RECEIVE:
    @classmethod
    def jo_act(self, rp, actor):
        if not actor.mq.empty():
            value = actor.mq.get()
            actor.ds.append(value)
            actor.scheduler.active_queue.put(actor)
        else:
            actor.scheduler.waiting_set.add(actor.aid)
            # do not put the actor back to active_queue

    @classmethod
    def jo_exe(self, rp, vm):
        print("- receive fail")
        print("  can not use 'receive' in sequential code")
        error()

    @classmethod
    def jo_print(self):
        p_print("receive")

class SEND:
    @classmethod
    def jo_act(self, rp, actor):
        body = actor.ds.pop()
        aid = actor.ds.pop()
        message = Message(aid, body)
        sche = actor.scheduler
        sche.out_queue.put(message)
        sche.active_queue.put(actor)

    @classmethod
    def jo_exe(self, rp, vm):
        print("- send fail")
        print("  can not use 'send' in sequential code")
        error()

    @classmethod
    def jo_print(self):
        p_print("send")

class SPAWN:
    @classmethod
    def jo_act(self, rp, actor):
        clo = actor.ds.pop()
        meta_message = MetaMessage("spawn", {
            'aid' : actor.aid,
            'clo' : clo,
        })
        actor.scheduler.meta_out_queue.put(meta_message)
        actor.scheduler.spawning_set.add(actor.aid)
        # do not put the actor back to active_queue

    @classmethod
    def jo_exe(self, rp, vm):
        print("- spawn fail")
        print("  can not use 'spawn' in sequential code")
        error()

    @classmethod
    def jo_print(self):
        p_print("spawn")

class ACTION:
    @classmethod
    def jo_exe(self, rp, vm):
        clo = vm.ds.pop()
        random_sid = generate_random_sid()
        channel = global_channel_vect[random_sid]
        meta_message = MetaMessage("action", {
            'clo'  : clo,
        })
        channel.meta_in_queue.put(meta_message)

    @classmethod
    def jo_print(self):
        p_print("action")

class Channel:
    def __init__(self):
        self.in_queue = mp.Queue()
        self.meta_in_queue = mp.Queue()

class MetaMessage:
    def __init__(self, head, body):
        self.head = head
        self.body = body

class Scheduler:
    def __init__(self, channel_vect, sid):
        self.sid = sid
        self.channel_vect = channel_vect

        self.channel = self.channel_vect[sid]
        self.in_queue = self.channel.in_queue
        self.meta_in_queue = self.channel.meta_in_queue

        self.out_queue = queue.Queue()
        self.meta_out_queue = queue.Queue()

        self.active_queue = queue.Queue()
        self.actor_dict = dict()
        self.waiting_set = set() # of aid
        self.spawning_set = set() # of aid

        self._actor_counter = 0

def sche_start(sche):
    while True:
        send_meta_out_queue(sche)
        process_meta_in_queue(sche)
        send_out_queue(sche)
        distribute_in_queue(sche)
        schedule(sche)

def send_meta_out_queue(sche):
    while not sche.meta_out_queue.empty():
        meta_message = sche.meta_out_queue.get()
        if meta_message.head == "spawn":
            meta_request = MetaMessage("spawn-request", {
                'aid' : meta_message.body['aid'],
                'clo' : meta_message.body['clo'],
            })
            random_sid = generate_random_sid()
            random_channel = sche.channel_vect[random_sid]
            random_channel.meta_in_queue.put(meta_request)

def process_meta_in_queue(sche):
    while not sche.meta_in_queue.empty():
        meta_message = sche.meta_in_queue.get()

        if meta_message.head == "spawn-request":
            old_aid = meta_message.body['aid']
            clo = meta_message.body['clo']
            jojo = JOJO(clo.body)
            rp = RP(jojo)
            vm = VM([], [rp])
            actor = Actor(sche, vm)
            new_aid = actor.aid
            meta_response = MetaMessage("spawn-response", {
                'old_aid' : old_aid,
                'new_aid' : new_aid,
            })
            channel = sche.channel_vect[old_aid.sid]
            channel.meta_in_queue.put(meta_response)

        elif meta_message.head == "spawn-response":
            old_aid = meta_message.body['old_aid']
            new_aid = meta_message.body['new_aid']
            old_actor = sche.actor_dict[old_aid.key]
            if old_aid in sche.spawning_set:
                sche.spawning_set.remove(old_aid)
                sche.active_queue.put(old_actor)
                old_actor.ds.append(new_aid)
            else:
                print("- spawn-response sent to wrong actor")
                error()

        elif meta_message.head == "action":
            clo = meta_message.body['clo']
            jojo = JOJO(clo.body)
            rp = RP(jojo)
            vm = VM([], [rp])
            actor = Actor(sche, vm)

def send_out_queue(sche):
    while not sche.out_queue.empty():
        message = sche.out_queue.get()
        channel = sche.channel_vect[message.aid.sid]
        channel.in_queue.put(message)

def distribute_in_queue(sche):
    while not sche.in_queue.empty():
        message = sche.in_queue.get()
        actor = sche.actor_dict[message.aid.key]
        if actor.aid in sche.waiting_set:
            sche.waiting_set.remove(actor.aid)
            sche.active_queue.put(actor)
            actor.ds.append(message.body)
        else:
            actor.mq.put(message.body)

def schedule(sche):
    i = 0
    qsize = sche.active_queue.qsize()
    while i < qsize:
        actor = sche.active_queue.get()
        if actor.finished_p():
            del sche.actor_dict[actor.aid.key]
        else:
            actor.exe_one_step()
        i = i + 1

class Message:
    def __init__(self, aid, body):
        self.aid = aid
        self.body = body

SCHE_NUMBER = mp.cpu_count()

def generate_random_sid():
    return random.randint(0, SCHE_NUMBER - 1)

global_channel_vect = []
for i in range(SCHE_NUMBER):
    global_channel_vect.append(Channel())

global_scheduler_vect = []
for i in range(SCHE_NUMBER):
    scheduler = Scheduler(global_channel_vect, i)
    global_scheduler_vect.append(scheduler)

global_process_vect = []
for scheduler in global_scheduler_vect:
    process = mp.Process(
        target = sche_start,
        args = [scheduler],
        daemon = True
    )
    global_process_vect.append(process)

def schedule_start():
    for process in global_process_vect:
        process.start()

def code_scan(string):
    string_vect = []
    i = 0
    length = len(string)
    while i < length:
        char = string[i]

        if space_p(char):
            i = i + 1

        elif char == ';':
            newline_index = string.find('\n', i+1)
            if newline_index == -1:
                break
            end = newline_index + 1
            i = end

        elif delimiter_p(char):
            string_vect.append(char)
            i = i + 1

        elif doublequote_p(char):
            doublequote_end_index = string.find('"', i+1)
            if doublequote_end_index == -1:
                print("- code_scan fail")
                print("  doublequote mismatch")
                print("  string : {}".format(string))
                error()
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
       char = string[i]
       if (space_p(char) or
           delimiter_p(char) or
           doublequote_p(char)):
           return i
       i = i + 1

def space_p(char):
    return char.isspace()

def delimiter_p(char):
    return (char == '(' or
            char == ')' or
            char == '[' or
            char == ']' or
            char == '{' or
            char == '}' or
            char == ',' or
            char == ';' or
            char == '`' or
            char == "'")

def doublequote_p(char):
    return char == '"'

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
    if null_p(cdr) or cons_p(cdr):
        return Cons(car, cdr)
    else:
        print("- cons fail")
        print("  cdr of cons must be a cons or null")
        print("  cdr : {}".format(cdr))
        error()

def cons_p(x):
    return isinstance(x, Cons)

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

def p_print(x):
    print(x, end="")
    sys.stdout.flush()

def sexp_print(s):
    if null_p(s):
        p_print("null")
    elif cons_p(s):
        p_print("(")
        sexp_list_print(s)
        p_print(")")
    else:
        p_print(s)

def sexp_list_print(s_cons):
    if null_p(s_cons):
        pass
    elif null_p(cdr(s_cons)):
        sexp_print(car(s_cons))
    else:
        sexp_print(car(s_cons))
        p_print(" ")
        sexp_list_print(cdr(s_cons))

def new_module(name):
    module = types.ModuleType(name)
    # for top level sexp
    module.vm = VM([], [])
    # for name can occur before been defined
    module.defined_name_set = set()
    sys.modules[name] = module
    return module

def jojo_define(module, name, value):
    module.defined_name_set.add(name)
    setattr(module, name, value)

def merge_prim_dict(module):
    for name, value in prim_dict.items():
        jojo_define(module, name, value)

def merge_module(module, src_module):
    for name in src_module.defined_name_set:
        jojo = getattr(src_module, name)
        jojo_define(module, name, jojo)

def merge_sexp_vect(module, sexp_vect):
    for sexp in sexp_vect:
        jo_vect = sexp_emit(module, sexp)
        module.vm.rs.append(RP(JOJO(jo_vect)))
        module.vm.exe()
    return module

def compile_module(name, sexp_vect):
    module = new_module(name)
    merge_prim_dict(module)
    merge_module(module, core_module)
    merge_sexp_vect(module, sexp_vect)
    return module

def compile_core_module(name, sexp_vect):
    module = new_module(name)
    merge_prim_dict(module)
    merge_sexp_vect(module, sexp_vect)
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
    # keyword can not have dot-in-name
    if keyword in keyword_dict.keys():
        fun = keyword_dict[keyword]
        return fun(module, cdr(cons))
    elif keyword in macro_dict.keys():
        fun = macro_dict[keyword]
        new_sexp = fun(cdr(cons))
        return sexp_emit(module, new_sexp)
    else:
        # a call to string_emit
        # handles dot-in-name in head of sexp
        vm = VM([cdr(cons)],
                [RP(JOJO(string_emit(module, keyword)))])
        vm.exe()
        new_sexp = vm.ds[0]
        return sexp_emit(module, new_sexp)

def string_emit(module, string):
    # special strings
    for p, e in string_emitter_vect:
        if p(string):
            return e(module, string)

    # dot in string
    if '.' in string:
        return dot_in_string_emit(module, string)

    # built-in keyword
    if string in key_jo_dict.keys():
        return key_jo_dict[string]

    # normal function call
    return [CALL_FROM_MODULE(module.__name__, string)]

def dot_in_string_emit(module, string):
    jo_vect = []
    string_vect = string.split('.')
    head_string = string_vect[0]
    if head_string == '':
        pass
    else:
        jo_vect.extend(string_emit(module, head_string))

    tail_string_vect = string_vect[1:]
    for s in tail_string_vect:
        s1 = '.' + s
        jo_vect.extend(string_emit(module, s1))

    return jo_vect

string_emitter_vect = []

def string_emitter(p):
    def decorator(emitter):
        string_emitter_vect.append((p, emitter))
        return emitter
    return decorator

def int_string_p(string):
    if not string_p(string):
        return False
    length = len(string)
    if length == 0:
        return False
    elif string[0] == '-':
        return nat_string_p(string[1:])
    else:
        return nat_string_p(string)

def nat_string_p(string):
    if not string_p(string):
        return False
    return string.isdecimal()

@string_emitter(int_string_p)
def int_string_emitter(module, string):
    return [int(string)]

def doublequoted_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 3:
        return False
    elif string[0] != '"':
        return False
    elif string[-1] != '"':
        return False
    else:
        return True

@string_emitter(doublequoted_string_p)
def doublequoted_string_emitter(module, string):
    string = string[1:-1]
    return [string]

def local_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 2:
        return False
    elif string.count('.') != 0:
        return False
    elif string.count(':') != 1:
        return False
    elif string[0] != ':':
        return False
    elif string[-1] == '!':
        return False
    else:
        return True

@string_emitter(local_string_p)
def local_string_emitter(module, string):
    return [GET(string)]

def set_local_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 3:
        return False
    elif string.count('.') != 0:
        return False
    elif string[0] != ':':
        return False
    elif string[-1] != '!':
        return False
    else:
        return True

@string_emitter(set_local_string_p)
def set_local_string_emitter(module, string):
    string = string[:-1]
    return [SET(string)]

def message_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 2:
        return False
    elif string[0] != '.':
        return False
    elif string.count('.') != 1:
        return False
    elif string[-1] == '!':
        return False
    else:
        return True

@string_emitter(message_string_p)
def message_string_emitter(module, string):
    string = string[1:]
    return [MSG(string)]

def set_message_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 2:
        return False
    elif string[0] != '.':
        return False
    elif string.count('.') != 1:
        return False
    elif string[-1] != '!':
        return False
    else:
        return True

@string_emitter(set_message_string_p)
def set_message_string_emitter(module, string):
    string = string[1:-1]
    return [SET_FIELD(string)]

prim_dict = {}

def prim(name):
    def decorator(fun):
        prim_dict[name] = fun
        return fun
    return decorator

@prim('drop')
def drop(a):
    return None

@prim('dup')
def dup(a):
    return VALUES(a, a)

@prim('over')
def over(a, b):
    return VALUES(a, b, a)

@prim('tuck')
def tuck(a, b):
    return VALUES(b, a, b)

@prim('swap')
def swap(a, b):
    return VALUES(b, a)

prim('Int')(int)

@prim('int?')
def int_p(x):
    return type(x) == int

@prim('inc')
def inc(a):
    return a + 1

@prim('dec')
def dec(a):
    return a - 1

@prim('add')
def add(a, b):
    return a + b

@prim('sub')
def sub(a, b):
    return a - b

@prim('mul')
def mul(a, b):
    return a * b

@prim('div')
def div(a, b):
    return a // b

@prim('mod')
def mod(a, b):
    return a % b

@prim('divmod')
def p_divmod(a, b):
    return VALUES(*divmod(a, b))

@prim('lt?')
def lt_p(a, b):
    return a < b

@prim('gt?')
def gt_p(a, b):
    return a > b

@prim('lteq?')
def lteq_p(a, b):
    return a <= b

@prim('gteq?')
def gteq_p(a, b):
    return a >= b

@prim('int-print')
def int_print(i):
    p_print(i)

prim('Bool')(bool)

@prim('true')
def true():
    return True

@prim('false')
def false():
    return False

@prim('not')
def p_not(b):
    return not b

@prim('and')
def p_and(a, b):
    return (a and b)

@prim('or')
def p_or(a, b):
    return (a or b)

@prim('eq?')
def eq_p(a, b):
    if string_p(a):
        return a == b
    else:
        return a is b

@prim('eqv?')
def eqv_p(a, b):
    return a == b

prim('null')(null)
prim('null?')(null_p)

prim('cons')(cons)
prim('cons?')(cons_p)

prim('car')(car)
prim('cdr')(cdr)

prim('sexp-print')(sexp_print)
prim('sexp-list-print')(sexp_list_print)

prim('code-scan')(code_scan)

prim('String')(str)

prim('string?')(string_p)

@prim('string-print')
def string_print(string):
    p_print(string)

@prim('string-length')
def string_length(string):
    return len(string)

@prim('string-ref')
def string_ref(string, index):
    return string[index]

@prim('string-append')
def string_append(string1, string2):
    return "".join([string1, string2])

@prim('string-slice')
def string_slice(string, begin, end):
    return string[begin:end]

@prim('string-empty?')
def string_empty_p(string):
    return len(string) == 0

@prim('string-eq?')
def string_eq_p(string1, string2):
    return string1 == string2

@prim('string->int')
def string_to_int(string):
    return int(string)

prim('int-string?')(int_string_p)
prim('local-string?')(local_string_p)

prim('Vect')(Vect)

prim('vect?')(vect_p)

@prim('vect-copy')
def vect_copy(vect):
    return vect[:]

@prim('vect-member?')
def vect_member_p(x, vect):
    return x in vect

@prim('vect-length')
def vect_length(vect):
    return len(vect)

@prim('vect-ref')
def vect_ref(vect, index):
    return vect[index]

@prim('vect-append')
def vect_append(vect1, vect2):
    vect1_copy = vect_copy(vect1)
    vect1_copy.extend(vect2)
    return vect1_copy

@prim('vect-zip-dict')
def vect_zip_dict(v1, v2):
    if len(v1) != len(v2):
        print("- vect_zip_dict fail")
        print("  length of vect1")
        print("    is not equal to length of vect2")
        print("  length of vect1 : {}".format(len(v1)))
        print("  length of vect2 : {}".format(len(v2)))
        print("  vect1 : {}".format(v1))
        print("  vect2 : {}".format(v2))
        error()
    d = {}
    for k, v in zip(v1, v2):
       d[k] = v
    return d

@prim('vect->sexp')
def vect_to_sexp(vect):
    if vect == []:
        return null
    elif not vect_p(vect):
        return vect
    else:
        return cons(vect_to_sexp(vect[0]),
                    vect_to_sexp(vect[1:]))

@prim('sexp->vect')
def sexp_to_vect(sexp):
    if string_p(sexp):
        return sexp
    sexp_vect = list_to_vect(sexp)
    result_vect = []
    for s in sexp_vect:
        result_vect.append(sexp_to_vect(s))
    return result_vect

Stack = Vect

prim('Stack')(Stack)

@prim('stack?')
def stack_p(x):
    return type(x) == Stack

@prim('stack-pop')
def stack_pop(stack):
    return stack.pop()

@prim('stack-push')
def stack_push(value, stack):
    stack.append(value)
    return stack

@prim('stack-drop')
def stack_drop(stack):
    stack.pop()
    return stack

@prim('stack-dup')
def stack_dup(stack):
    a = stack.pop()
    stack.append(a)
    return stack

@prim('stack-over')
def stack_over(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(b)
    stack.append(a)
    stack.append(b)
    return stack

@prim('stack-tuck')
def stack_tuck(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)
    stack.append(a)
    return stack

@prim('stack-swap')
def stack_swap(stack):
    a = stack.pop()
    b = stack.pop()
    stack.append(a)
    stack.append(b)
    return stack

@prim('stack-length')
def stack_length(stack):
    return len(stack)

@prim('stack-empty?')
def stack_empty_p(stack):
    return len(stack) == 0

prim('<null>')(Null)
prim('<cons>')(Cons)

@prim('list?')
def list_p(x):
    return null_p(x) or cons_p(x)

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

def list_length(l):
    if null_p(l):
        return 0
    else:
        return list_length(cdr(l)) + 1

def list_ref(l, i):
    if null_p(l):
        print("- list_ref fail")
        print("  index greater then length of list")
        error()
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

@prim('list-zip-dict')
def list_zip_dict(l1, l2):
    v1 = list_to_vect(l1)
    v2 = list_to_vect(l2)
    return vect_zip_dict(v1, v2)

Dict = dict

prim('Dict')(Dict)

@prim('dict?')
def dict_p(x):
    return type(x) == Dict

@prim('dict-copy')
def dict_copy(d):
    return d.copy()

@prim('vect->dict')
def vect_to_dict(vect):
    length = len(vect)
    if length % 2 != 0:
        print("- vect->dict fail")
        print("  length of vect must be even")
        print("  length : {}".format(length))
        print("  vect : {}".format(vect))
        error()

    d = {}
    i = 0
    while i < length:
        k = vect[i]
        v = vect[i+1]
        d[k] = v
        i = i + 2

    return d

@prim('dict-length')
def dict_length(d):
    return len(d)

@prim('dict-find')
def dict_find(d, k):
    try:
        return VALUES(d[k], True)
    except KeyError:
        return False

@prim('dict-update')
def dict_update(d1, d2):
    d1 = dict_copy(d1)
    return d1.update(d2)

@prim('dict-delete')
def dict_delete(d, k):
    d = dict_copy(d)
    del d[k]
    return d

prim('Tuple')(tuple)

@prim('tuple?')
def tuple_p(x):
    return type(x) == tuple

@prim('vect->tuple')
def vect_to_tuple(vect):
    return tuple(vect)

@prim('tuple->vect')
def tuple_to_vect(tu):
    return Vect(tu)

@prim('tuple-length')
def tuple_length(tu):
    return len(tu)

@prim('tuple-ref')
def tuple_ref(tu, index):
    return tu[index]

@prim('tuple-append')
def tuple_append(tu1, tu2):
    vect1 = Vect(tu1)
    vect1.extend(tu2)
    return tuple(vect1)

prim('Set')(set)

@prim('set?')
def set_p(x):
    return type(x) == set

@prim('vect->set')
def vect_to_set(vect):
    return set(vect)

@prim('set->vect')
def set_to_vect(s):
    return Vect(s)

@prim('set-length')
def set_length(s):
    return len(s)

@prim('set-member?')
def set_member_p(x, s):
    return x in s

@prim('set-disjoint?')
def set_disjoint_p(s1, s2):
    return s1.isdisjoint(s2)

@prim('set-subset?')
def set_subset_p(s1, s2):
    return s1.issubset(s2)

@prim('set-superset?')
def set_superset_p(s1, s2):
    return s1.issuperset(s2)

@prim('set-union')
def set_union(s1, s2):
    return s1.union(s2)

@prim('set-intersection')
def set_intersection(s1, s2):
    return s1.intersection(s2)

@prim('set-difference')
def set_difference(s1, s2):
    return s1.difference(s2)

@prim('set-symmetric-difference')
def set_symmetric_difference(s1, s2):
    return s1.symmetric_difference(s2)

prim('print')(p_print)

@prim('newline')
def newline():
    print("")
    sys.stdout.flush()

prim('nl')(newline)

@prim('space')
def space():
    p_print(" ")

@prim('bye')
def bye():
    print("bye bye ^-^/")
    sys.exit()

def read_char(char_stack):
    if len(char_stack) == 0:
        return sys.stdin.read(1)
    else:
        return char_stack.pop()

def read_string(char_stack):
    char_vect = []
    collecting_bytes_p = False

    while True:
        char = read_char(char_stack)
        if char == ';':
            read_drop_comment(char_stack)

        elif not collecting_bytes_p:
            if space_p(char):
                pass
            elif doublequote_p(char):
                return read_doublequoted_string(char_stack)
            elif delimiter_p(char):
                char_vect.append(char)
                break
            else:
                char_vect.append(char)
                collecting_bytes_p = True

        else:
            if (doublequote_p(char) or
                delimiter_p(char) or
                space_p(char)):
                char_stack.append(char)
                break
            else:
                char_vect.append(char)

    return "".join(char_vect)

def read_drop_comment(char_stack):
    while True:
        char = read_char(char_stack)
        if char == '\n':
            return

def read_doublequoted_string(char_stack):
    char_vect = []
    while True:
        char = read_char(char_stack)
        if char == '"':
            break
        else:
            char_vect.append(char)
    return "".join(['"'] + char_vect + ['"'])

def read_sexp(char_stack):
    string = read_string(char_stack)
    if string == '(':
        sexp_list = read_sexp_list_until_ket(char_stack, ')')
        return sexp_list
    elif string == '[':
        sexp_list = read_sexp_list_until_ket(char_stack, ']')
        return cons('begin', sexp_list)
    elif string == '{':
        sexp_list = read_sexp_list_until_ket(char_stack, '}')
        return cons('clo', sexp_list)
    elif string == '"':
        return read_doublequoted_string(char_stack)
    elif string == "'":
        sexp = read_sexp(char_stack)
        return cons('quote', cons(sexp, null))
    elif string == "`":
        sexp = read_sexp(char_stack)
        return cons('partquote', cons(sexp, null))
    else:
        return string

def read_sexp_list_until_ket(char_stack, ket):
    string = read_string(char_stack)
    if string == ket:
        return null
    else:
        char_vect = Vect(string)
        char_vect.reverse()
        char_stack.extend(char_vect)
        sexp = read_sexp(char_stack)
        recur = read_sexp_list_until_ket(char_stack, ket)
        return cons(sexp, recur)

def print_data_stack(ds):
    p_print(";{}> ".format(len(ds)))
    print(ds)

def print_return_stack(rs):
    print("- return-stack * {} *".format(len(rs)))
    for rp in rs:
        return_point_print(rp)

def return_point_print(rp):
    p_print("  - progress : {} / {}".format(rp.cursor, rp.length))
    newline()

    next_cursor = rp.cursor
    last_cursor = rp.cursor - 1

    if last_cursor == 0:
        pass
    else:
        p_print("    pass : ")
        i = 0
        while i < last_cursor:
            jo_print(rp.body[i])
            space()
            i = i + 1
        newline()

    p_print("    last : ")
    jo_print(rp.body[last_cursor])
    newline()

    if next_cursor == rp.length:
        pass
    else:
        p_print("    next : ")
        i = next_cursor
        while i < rp.length:
            jo_print(rp.body[i])
            space()
            i = i + 1
        newline()

    if len(rp.lr) == 0:
       pass
    else:
       p_print("    where : {}".format(rp.lr))
       newline()

def jo_print(jo):
    if fun_p(jo):
        p_print(jo.__module__)
        p_print(".")
        p_print(jo.__name__)
    elif hasattr(jo, "jo_print"):
        jo.jo_print()
    else:
        p_print(jo)

def module_repl(module):
    module.repl_char_stack = []
    print_data_stack(module.vm.ds)
    try:
        while True:
            module_repl_one_step(module)
    except KeyboardInterrupt:
        return
    except EXIT_MODULE_REPL:
        return

class EXIT_MODULE_REPL(Exception):
    pass

def module_repl_one_step(module):
    sexp = read_sexp(module.repl_char_stack)
    if sexp == 'exit':
        raise EXIT_MODULE_REPL()

    try:
        merge_sexp_vect(module, [sexp])
        print_data_stack(module.vm.ds)
    except SystemExit:
        sys.exit()
    except:
        error_type = sys.exc_info()[0]
        error_name = error_type.__name__
        error_info = sys.exc_info()[1]
        print("- error : {}".format(error_name))
        print("  info : {}".format(error_info))
        print("  traceback : ")
        traceback.print_exc()
        call_module_debug(module, 1)

prim('error')(error)

@prim('module-debug')
def module_debug(module, level):
    print("- enter debug-repl [level : {}]".format(level))
    module.debug_repl_char_stack = []
    print_return_stack(module.vm.rs)
    print_data_stack(module.vm.ds)
    try:
        while True:
            module_debug_one_step(module, level)
    except KeyboardInterrupt:
        module.vm.rs = []
        newline()
        print("- leave debug-repl [level : {}]".format(level))
        print("  return-stack is cleared")
        print("  for module : {}".format(module.__name__))
        print_data_stack(module.vm.ds)
        return
    except EXIT_MODULE_DEBUG_REPL:
        module.vm.ds = []
        module.vm.rs = []
        print("- exit debug-repl [level : {}]".format(level))
        print("  return-stack is cleared")
        print("  data-stack is cleared")
        print("  for module : {}".format(module.__name__))
        print_data_stack(module.vm.ds)
        return
    except LEAVE_MODULE_DEBUG_REPL:
        module.vm.rs = []
        print("- leave debug-repl [level : {}]".format(level))
        print("  return-stack is cleared")
        print("  for module : {}".format(module.__name__))
        print_data_stack(module.vm.ds)
        return

class EXIT_MODULE_DEBUG_REPL(Exception):
    pass

class LEAVE_MODULE_DEBUG_REPL(Exception):
    pass

def module_debug_one_step(module, level):
    p_print("debug[{}]> ".format(level))
    sys.stdout.flush()
    sexp = read_sexp(module.debug_repl_char_stack)
    if sexp == 'exit':
        raise EXIT_MODULE_DEBUG_REPL()
    if sexp == 'leave':
        raise LEAVE_MODULE_DEBUG_REPL()

    try:
        merge_sexp_vect(module, [sexp])
        print_data_stack(module.vm.ds)
    except SystemExit:
        sys.exit()
    except:
        error_type = sys.exc_info()[0]
        error_name = error_type.__name__
        error_info = sys.exc_info()[1]
        print("- error : {}".format(error_name))
        print("  info : {}".format(error_info))
        p_print("  traceback : ")
        traceback.print_exc()
        call_module_debug(module, level + 1)

def call_module_debug(module, level):
    jojo = JOJO([module, level, module_debug, nop])
    module.vm.rs.append(RP(jojo))
    module.vm.exe()

prim('Object')(object)

@prim('value->class')
def value_to_class(value):
    return type(value)

@prim('subclass?')
def subclass_p(c1, c2):
    if type(c2) == UNION:
       return c1 in c2.get_type_vect()
    else:
       return issubclass(c1, c2)

prim('schedule-start')(schedule_start)

@prim('nop')
def nop():
    return

@prim('none')
def none():
    return VALUES(None)

@prim('sleep')
def sleep(secs):
    time.sleep(secs)
    return

def fun_to_positional_default_arg_dict(fun):
    signature = get_signature(fun)
    if signature == None:
        print("- fun_to_positional_default_arg_dict")
        print("  fail to get signature")
        print("  fun : {}".format(fun))
        error()
    parameters = signature.parameters
    return get_positional_default_arg_dict(parameters)

@prim('prepare-data-arguments')
def prepare_data_arguments(field_vect, value_vect, data):
    if not class_p(data):
        print("- prepare_data_arguments fail")
        print("  data must be a python class")
        print("  data : {}".format(data))
        error()
    elif not hasattr(data, 'field_name_vect'):
        print("- prepare_data_arguments fail")
        print("  data must has 'field_name_vect' attribute")
        print("  data : {}".format(data))
        error()

    if len(field_vect) == 0:
        normal_value_vect = value_vect
        field_value_vect = []
    elif len(field_vect) <= len(value_vect):
        normal_value_vect = value_vect[:-len(field_vect)]
        field_value_vect = value_vect[len(value_vect)-len(field_vect):]
    else:
        print("- prepare_data_arguments fail")
        print("  length of field_vect")
        print("    must be shorter then length of value_vect")
        print("  length of field_vect : {}".format(len(field_vect)))
        print("  length of value_vect : {}".format(len(value_vect)))
        print("  data : {}".format(data))
        print("  field_vect : {}".format(field_vect))
        error()

    field_dict = dict(zip(field_vect, field_value_vect))
    ordered_vect = []
    for field_name in data.field_name_vect:
        if field_name in field_dict.keys():
            ordered_vect.append(field_dict[field_name])

    result_vect = normal_value_vect + ordered_vect
    return VALUES(*result_vect)

@prim('keyword-apply')
def keyword_apply(field_vect, value_vect, fun):
    kwargs = dict(zip(field_vect, value_vect))
    return fun(**kwargs)

keyword_dict = {}

def keyword(name):
    def decorator(fun):
        keyword_dict[name] = fun
        return fun
    return decorator

@keyword("note")
def k_note(module, body):
    return []

@keyword('begin')
def k_begin(module, body):
    return sexp_list_emit(module, body)

@keyword('clo')
def k_clo(module, body):
    return [CLO(sexp_list_emit(module, body))]

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

@keyword('stack')
def k_stack(module, sexp_list):
    return k_vect(module, sexp_list)

@keyword('dict')
def k_dict(module, sexp_list):
    jo_vect = []
    jo_vect.extend([MARK])
    jo_vect.extend(sexp_list_emit(module, sexp_list))
    jo_vect.extend([COLLECT_VECT, vect_to_dict])
    return jo_vect

@keyword('tuple')
def k_tuple(module, sexp_list):
    jo_vect = []
    jo_vect.extend([MARK])
    jo_vect.extend(sexp_list_emit(module, sexp_list))
    jo_vect.extend([COLLECT_VECT, vect_to_tuple])
    return jo_vect

keyword('*')(k_tuple)

@keyword('set')
def k_set(module, sexp_list):
    jo_vect = []
    jo_vect.extend([MARK])
    jo_vect.extend(sexp_list_emit(module, sexp_list))
    jo_vect.extend([COLLECT_VECT, vect_to_set])
    return jo_vect

@keyword('primitive')
def k_primitive(module, sexp_list):
    jo_vect = []
    sexp_vect = list_to_vect(sexp_list)
    for sexp in sexp_vect:
        if not string_p(sexp):
            print("- (primitive) syntax error")
            print("  body of (primitive) must be names")
            print("  non string sexp : {}".format(sexp))
            print("  body : {}".format(sexp_vect))
            error()
        else:
            jo_vect.extend([PRIMITIVE(operator.attrgetter(sexp)(module))])
    return jo_vect

@keyword("import")
def k_import(module, body):
    name_vect = list_to_vect(body)

    if 'as' in name_vect:
        k_import_as(module, body)
        return []

    if null_p(body):
        return []

    for name in name_vect:
        if '.' in name:
            print("- (import) syntax error")
            print("  module name can not contain '.'")
            print("  module name : {}".format(name))
            p_print("  import body : ")
            sexp_list_print(body)
            newline()
            error()

    for name in name_vect:
        k_import_one(module, name)

    return []

def k_import_one(module, name):
    imported_module = importlib.import_module(name)
    jojo_define(module, name, imported_module)

def k_import_as(module, body):
    name_vect = list_to_vect(body)
    if (len(name_vect) != 3 or
        name_vect[0] == 'as' or
        name_vect[1] != 'as' or
        name_vect[2] == 'as'):
        print("- (import) syntax error")
        print("  syntax for (import as) should be :")
        print("  (import <module-name> as <name>)")
        p_print("  import body : ")
        sexp_list_print(body)
        newline()
        error()
    name = name_vect[0]
    as_name = name_vect[2]
    imported_module = importlib.import_module(name)
    jojo_define(module, as_name, imported_module)

@keyword("from")
def k_from(module, body):
    vect_body = list_to_vect(body)
    if 'as' in vect_body:
        k_from_as(module, body)
        return []

    k_from_syntax_check(body)
    module_name = car(body)
    name_vect = list_to_vect(cdr(cdr(body)))
    imported_module = importlib.import_module(module_name)
    for name in name_vect:
        jojo_define(module, name, getattr(imported_module, name))

    return []

def k_from_syntax_check(body):
    vect_body = list_to_vect(body)
    if len(vect_body) > 2:
        pass
    if vect_body[1] == 'import':
        return
    print("- (from) syntax error")
    print("  syntax for (from import) should be :")
    print("  (from <module-name> import <name> ...)")
    p_print("  import body : ")
    sexp_list_print(body)
    newline()
    error()

def k_from_as(module, body):
    k_from_as_syntax_check(body)
    vect_body = list_to_vect(body)
    module_name = vect_body[0]
    name = vect_body[2]
    as_name = vect_body[4]
    imported_module = importlib.import_module(module_name)
    jojo_define(module, as_name, getattr(imported_module, name))

def k_from_as_syntax_check(body):
    vect_body = list_to_vect(body)
    if len(vect_body) == 5:
        pass
    if vect_body[1] == 'import':
        pass
    if vect_body[3] == 'as':
        return
    print("- (from) syntax error")
    print("  syntax for (from import as) should be :")
    print("  (from <module-name> import <name> as <name>)")
    p_print("  import body : ")
    sexp_list_print(body)
    newline()
    error()

@keyword("+jojo")
def plus_jojo(module, body):
    if list_length(body) == 0:
        print("- (+jojo) syntax error")
        print("  body of (+jojo) can not be empty")
        error()

    jojo_name = car(body)
    jojo_define(module, jojo_name,
                JOJO(sexp_list_emit(module, cdr(body))))

    return []

@keyword("+data")
def plus_data(module, body):
    data_name = car(body)
    if not data_name_string_p(data_name):
        print("- (+data) syntax error")
        print("  data_name must be of form <...>")
        print("  data_name : {}".format(data_name))
        error()

    field_name_vect = body_to_field_name_vect(cdr(body))
    data_class = create_data_class(data_name, field_name_vect)
    data_class.__module__ = module
    jojo_define(module, data_name, data_class)
    # generate more bindings
    constructor_name = data_name[1:-1]
    jojo_define(module, constructor_name, JOJO([data_class, NEW]))
    predicate_name = "".join([constructor_name, "?"])
    jojo_define(module, predicate_name, DATA_PRED(data_class))
    return []

def body_to_field_name_vect(body):
    body_vect = list_to_vect(body)
    field_name_vect = []
    for sexp in body_vect:
        if string_p(sexp):
            if message_string_p(sexp):
                sexp = sexp[1:]
                field_name_vect.append(sexp)
        elif cons_p(sexp):
            if car(sexp) == '.':
                vect1 = body_to_field_name_vect(cdr(sexp))
                field_name_vect.extend(vect1)
    return field_name_vect

def data_name_string_p(string):
    if not string_p(string):
        return False
    if len(string) < 3: # example : '<n>'
        return False
    elif string[0] != '<':
        return False
    elif string[-1] != '>':
        return False
    elif string.count('<') != 1:
        return False
    elif string.count('>') != 1:
        return False
    elif string.count('.') != 0:
        return False
    elif string.count(':') != 0:
        return False
    else:
        return True

def create_data_init(field_name_vect):
    '''
    just like
    def __init__(self, x1, x2):
        self.__dict__['field-name-1'] = x1
        self.__dict__['field-name-2'] = x2
    '''
    if len(field_name_vect) == 0:
        code = "def init(self):pass"
        exec(code, globals())
        return init
    else:
        length = len(field_name_vect)
        pieces = []
        pieces.append("def init(self")
        for field_name, index in zip(field_name_vect, range(length)):
            pieces.append(",{}".format('x'+str(index)))
        pieces.append("):")
        for field_name, index in zip(field_name_vect, range(length)):
            pieces.append("self.__dict__['{}']={};".format(field_name,
                                               ('x'+str(index))))
        code = ''.join(pieces)
        exec(code, globals())
        return init

def create_data_class(data_name, field_name_vect):
    rev = vect_copy(field_name_vect)
    rev.reverse()
    def update_ns(ns):
        ns.update({
            '__init__' : create_data_init(field_name_vect),
            'field_name_vect': field_name_vect,
            'reversed_field_name_vect': rev,
        })
    return types.new_class(
        data_name,
        kwds = None,
        exec_body = update_ns)

@keyword("+union")
def plus_union(module, body):
    name = car(body)
    rest = cdr(body)
    jo_vect = sexp_list_emit(module, rest)
    jojo = JOJO(jo_vect)
    jojo_define(module, name, UNION(jojo))
    return []

class UNION:
    def __init__(self, jojo):
        self.jojo = jojo

    def get_type_vect(self):
        vm = VM([], [RP(self.jojo)])
        vm.exe()
        return vm.ds

@keyword("+gene")
def plus_gene(module, body):
    name = car(body)
    rest = cdr(body)
    arrow = car(rest)
    arity = arrow_get_arity(arrow)
    if arity == 0:
        print("- (+gene) syntax error")
        print("  arity of arrow is zero")
        print("  gene dispatches on types of arguments")
        print("  can not define gene over nothing")
        print("  name : {}".format(name))
        p_print("  arrow : ")
        sexp_print(arrow)
        newline()
        error()

    default_jojo = JOJO(sexp_list_emit(module, rest))
    jojo_define(module, name, GENE(arity, default_jojo))
    return []

def arrow_get_arity(arrow):
    arity = 0
    sexp_vect = list_to_vect(cdr(arrow))
    for sexp in sexp_vect:
        if local_string_p(sexp):
            arity = arity + 1
        elif sexp == '--':
            break
        else:
            pass

    return arity

@keyword("+disp")
def plus_disp(module, body):
    name = car(body)
    rest = cdr(body)
    arrow = car(rest)
    type_tuple_vect = arrow_get_type_tuple_vect(module, arrow)

    if not hasattr(module, name):
        print("- (+disp) syntax error")
        print("  name is undefined")
        print("  name : {}".format(name))
        error()

    gene = getattr(module, name)
    if type(gene) != GENE:
        print("- (+disp) syntax error")
        print("  type of name must be a gene")
        print("  name : {}".format(name))
        print("  type of name : {}".format(type(name)))
        error()

    jojo = JOJO(sexp_list_emit(module, rest))
    for type_tuple in type_tuple_vect:
        if type_tuple in gene.disp_dict:
            print("- (+disp) fail")
            print("  type_tuple for gene is already defined")
            print("  type_tuple : {}".format(type_tuple))
            print("  gene name : {}".format(name))
            p_print("  arrow : ")
            sexp_print(arrow)
            newline()
            error()
        else:
            gene.disp_dict[type_tuple] = jojo

    return []

def arrow_get_type_vect(module, arrow):
    sexp_vect = list_to_vect(cdr(arrow))
    new_sexp_vect = []
    for sexp in sexp_vect:
        if local_string_p(sexp):
            pass
        elif sexp == '--':
            break
        else:
            new_sexp_vect.append(sexp)

    new_sexp_list = vect_to_list(new_sexp_vect)
    jo_vect = sexp_list_emit(module, new_sexp_list)
    jojo = JOJO(jo_vect)
    vm = VM([], [RP(jojo)])
    vm.exe()

    return vm.ds

def type_vect_to_type_vect_vect(type_vect):
    type_vect_vect = []
    for t in type_vect:
        if type(t) == UNION:
            type_vect_vect.append(t.get_type_vect())
        else:
            type_vect_vect.append([t])

    return type_vect_vect

def arrow_get_type_tuple_vect(module, arrow):
    type_vect = arrow_get_type_vect(module, arrow)
    type_vect_vect = type_vect_to_type_vect_vect(type_vect)
    return Vect(itertools.product(*type_vect_vect))

key_jo_dict = {}

def key_jo(name, jo_vect):
    key_jo_dict[name] = jo_vect

key_jo('apply', [APPLY])
key_jo('ifte', [IFTE])
key_jo('new', [NEW])
key_jo(',', [])

key_jo('mark', [MARK])
key_jo('collect-vect', [COLLECT_VECT])
key_jo('vect-spread', [VECT_SPREAD])
key_jo('collect-list', [COLLECT_LIST])
key_jo('list-spread', [LIST_SPREAD])

key_jo('clear', [CLEAR])

key_jo('receive', [RECEIVE])
key_jo('send', [SEND])
key_jo('spawn', [SPAWN])
key_jo('action', [ACTION])

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
    print("- cond mismatch")
    p_print("  body : ")
    sexp_print(body)
    newline()
    error()

@macro('if')
def k_if(body):
    length = list_length(body)
    if length != 3:
        print("- (if) syntax fail")
        print("  body of (if) must has 3 sexps")
        print("  body length : {}".format(length))
        p_print("  body : ")
        sexp_list_print(body)
        newline()
        error()

    return vect_to_sexp(
        ['begin',
         car(body),
         ['clo', car(cdr(body))],
         ['clo', car(cdr(cdr(body)))],
         'ifte'])

@macro('when')
def k_when(body):
    length = list_length(body)
    if length <= 1:
        print("- (when) syntax fail")
        print("  length of body of (when) must be greater then 1")
        print("  body length : {}".format(length))
        p_print("  body : ")
        sexp_list_print(body)
        newline()
        error()

    rest_list = cdr(body)
    rest_vect = ['begin']
    rest_vect.extend(list_to_vect(rest_list))

    return vect_to_sexp(
        ['begin',
         car(body),
         ['clo', rest_vect],
         ['clo'],
         'ifte'])

@macro('call')
def k_call(body):
    rest_vect = list_to_vect(cdr(body))
    name = car(body)
    fields = []
    new_body = ['begin']
    for sexp in rest_vect:
       if message_string_p(sexp):
           fields.append(sexp[1:])
       else:
           new_body.append(sexp)
    return vect_to_sexp(
        ['begin',
         ['quote', fields], 'list->vect',
         'mark', new_body, 'collect-vect',
         ['primitive', name],
         'keyword-apply'])

@macro('create')
def k_create(body):
    rest_vect = list_to_vect(cdr(body))
    name = car(body)
    fields = []
    new_body = ['begin']
    for sexp in rest_vect:
        if message_string_p(sexp):
            fields.append(sexp[1:])
        else:
            new_body.append(sexp)
    return vect_to_sexp(
        ['begin',
         ['quote', fields], 'list->vect',
         'mark', new_body, 'collect-vect',
         name,
         'prepare-data-arguments',
         name,
         'new'])

@macro('main-act')
def k_main_act(body):
    body_vect = list_to_vect(body)
    return vect_to_sexp(
        ['begin',
         'schedule-start',
         (['clo'] + body_vect),
         'action'])

def maybe_drop_shebang(code):
    length = len(code)
    if length < 3:
        return code
    elif code[0:2] != '#!':
        return code
    else:
        end_of_first_line = code.find('\n')
        if end_of_first_line == -1:
            return ""
        else:
            return code[end_of_first_line:]

def load(name, path):
    current_module = sys.modules[inspect.stack()[1].frame.f_globals['__name__']]
    if ((current_module.__name__ == '__main__') or
        (not hasattr(current_module, '__file__'))):
        path = os.path.abspath(path)
    else:
        current_module_dir = os.path.dirname(current_module.__file__)
        path = "/".join([current_module_dir, path])

    if not os.path.exists(path):
        print("- load fail")
        print("  path does not exist")
        print("  path : {}".format(path))
        error()

    if not os.path.isfile(path):
        print("- load fail")
        print("  path is not file")
        print("  path : {}".format(path))
        error()

    with open(path, "r") as f:
        code = f.read()
        code = maybe_drop_shebang(code)
        sexp_vect = parse_sexp_vect(code_scan(code))
        module = compile_module(name, sexp_vect)

    module.__file__ = path

    return module

def load_core(path):
    path = os.path.abspath(path)

    if not os.path.exists(path):
        print("- load_core fail")
        print("  path does not exist")
        print("  path : {}".format(path))
        error()

    if not os.path.isfile(path):
        print("- load_core fail")
        print("  path is not file")
        print("  path : {}".format(path))
        error()

    with open(path, "r") as f:
        code = f.read()
        sexp_vect = parse_sexp_vect(code_scan(code))
        module = compile_core_module(path, sexp_vect)

    module.__file__ = path

    return module

current_module = sys.modules[__name__]
current_module_dir = os.path.dirname(current_module.__file__)
core_path = "/".join([current_module_dir, "core.jo"])
core_module = load_core(core_path)

@prim('repl')
def repl():
    module = new_module('jojo-repl')
    merge_prim_dict(module)
    merge_module(module, core_module)
    print ("welcome to jojo's programming adventure in python ^-^/")
    module_repl(module)
