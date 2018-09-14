#pragma once

#include "../libjojo.hpp"

struct apply_jo_t: jo_t
{
    size_t arity;
    apply_jo_t (size_t arity);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
