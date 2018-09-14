#pragma once

#include "../libjojo.hpp"

struct data_cons_o: obj_t
{
    tag_t type_tag;
    name_vector_t name_vector;
    data_cons_o (env_t &env,
                 tag_t type_tag,
                 name_vector_t name_vector,
                 obj_map_t obj_map);
    void apply (env_t &env, size_t arity);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};
