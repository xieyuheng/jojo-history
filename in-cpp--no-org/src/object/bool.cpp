#include "bool.hpp"

shared_ptr <obj_t>
true_c (env_t &env)
{
    return make_shared <data_o>
        (env, "true-t", obj_map_t ());
}

bool
true_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "true-t";
}

shared_ptr <obj_t>
false_c (env_t &env)
{
    return make_shared <data_o>
        (env, "false-t", obj_map_t ());
}

bool
false_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "false-t";
}

void
test_bool ()
{
}
