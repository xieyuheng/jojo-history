#include "str.hpp"

str_o::str_o (env_t &env, string str)
{
    this->tag = "str-t";
    this->str = str;
}

string
str_o::repr (env_t &env)
{
    return "\"" + this->str + "\"";
}

bool
str_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <str_o> (obj);
    return (this->str == that->str);
}

bool
str_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "str-t";
}

void
test_str ()
{
}
