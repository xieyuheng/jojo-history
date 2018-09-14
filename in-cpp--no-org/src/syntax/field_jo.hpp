#pragma once

#include "../libjojo.hpp"

struct field_jo_t: jo_t
{
    name_t name;
    jo_t * copy ();
    field_jo_t (name_t name);
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
