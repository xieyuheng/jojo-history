#pragma once

#include "../libjojo.hpp"

struct local_ref_jo_t: jo_t
{
    size_t level;
    size_t index;
    local_ref_jo_t (size_t level, size_t index);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
