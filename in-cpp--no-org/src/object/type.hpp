#pragma once

#include "../libjojo.hpp"

struct type_o: obj_t
{
    tag_t type_tag;
    type_o (env_t &env,
            tag_t type_tag,
            obj_map_t obj_map);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};

void
assign (env_t &env,
        name_t prefix,
        name_t name,
        shared_ptr <obj_t> obj);

bool
tag_name_p (name_t name);

void
define_type (env_t &env, name_t name);

void
test_type ();
