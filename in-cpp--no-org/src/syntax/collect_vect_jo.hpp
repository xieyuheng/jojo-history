#pragma once

#include "../libjojo.hpp"

struct collect_vect_jo_t: jo_t
{
    size_t counter;
    collect_vect_jo_t (size_t counter);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
