#pragma once

#include "../libjojo.hpp"

struct data_o: obj_t
{
    data_o (env_t &env,
            tag_t tag,
            obj_map_t obj_map);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};
