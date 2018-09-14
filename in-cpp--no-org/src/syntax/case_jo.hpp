#pragma once

#include "../libjojo.hpp"

struct case_jo_t: jo_t
{
    jojo_map_t jojo_map;
    shared_ptr <jojo_t> default_jojo;
    case_jo_t (jojo_map_t jojo_map);
    case_jo_t (jojo_map_t jojo_map,
               shared_ptr <jojo_t> default_jojo);
    bool has_default_jojo_p ();
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
