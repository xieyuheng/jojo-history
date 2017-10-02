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

def cdr(x):
    return x.cdr

def car(x):
    return x.car

def list_p(x):
    return null_p(x) or cons_p(x)

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
