#include "list.hpp"

shared_ptr <obj_t>
null_c (env_t &env)
{
    return make_shared <data_o>
        (env,
         "null-t",
         obj_map_t ());
}

shared_ptr <obj_t>
cons_c (env_t &env,
        shared_ptr <obj_t> car,
        shared_ptr <obj_t> cdr)
{
    auto obj_map = obj_map_t ();
    obj_map ["car"] = car;
    obj_map ["cdr"] = cdr;
    return make_shared <data_o>
        (env,
         "cons-t",
         obj_map);
}

bool
cons_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "cons-t";
}

shared_ptr <obj_t>
car (env_t &env, shared_ptr <obj_t> cons)
{
    assert (cons_p (env, cons));
    return cons->obj_map ["car"];
}

shared_ptr <obj_t>
cdr (env_t &env, shared_ptr <obj_t> cons)
{
    assert (cons_p (env, cons));
    return cons->obj_map ["cdr"];
}

bool
null_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "null-t";
}

bool
list_p (env_t &env, shared_ptr <obj_t> a)
{
    return null_p (env, a)
        || cons_p (env, a);
}

size_t
list_length (env_t &env, shared_ptr <obj_t> l)
{
    assert (list_p (env, l));
    auto length = 0;
    while (! null_p (env, l)) {
        length++;
        l = cdr (env, l);
    }
    return length;
}

void
test_list ()
{
}
