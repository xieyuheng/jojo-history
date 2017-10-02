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
