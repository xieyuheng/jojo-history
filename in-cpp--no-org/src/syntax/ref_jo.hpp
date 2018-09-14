#pragma once

#include "../libjojo.hpp"

struct ref_jo_t: jo_t
{
    box_t *box;
    ref_jo_t (box_t *box);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
