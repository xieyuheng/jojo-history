#pragma once

#include "../libjojo.hpp"

struct lit_jo_t: jo_t
{
    shared_ptr <obj_t> obj;
    lit_jo_t (shared_ptr <obj_t> obj);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
