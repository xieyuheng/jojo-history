#pragma once

#include "../libjojo.hpp"

struct assert_jo_t: jo_t
{
    shared_ptr <obj_t> body;
    shared_ptr <jojo_t> jojo;
    assert_jo_t (shared_ptr <obj_t> body,
                 shared_ptr <jojo_t> jojo);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
