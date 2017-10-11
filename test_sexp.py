from jojo import scan_string_vect, parse_sexp_vect, sexp_write

string = '''\
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
(1 (1 2 3) 2 (1 2 3) 3 "123")
'a
'(1 2 3)
('a 'b '(1 2 3))
'''
def newline():
    print("")

def test_0():
    symbol_vect = scan_string_vect(string)
    sexp_vect = parse_sexp_vect(symbol_vect)
    for sexp in sexp_vect:
        sexp_write(sexp)
        newline()

test_0()
