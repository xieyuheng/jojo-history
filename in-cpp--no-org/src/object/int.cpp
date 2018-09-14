#include "int.hpp"

int_o::int_o (env_t &env, int i)
{
    this->tag = "int-t";
    this->i = i;
}

string
int_o::repr (env_t &env)
{
    return to_string (this->i);
}

bool
int_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <int_o> (obj);
    return (this->i == that->i);
}

bool
int_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "int-t";
}

void
test_int ()
{
}
