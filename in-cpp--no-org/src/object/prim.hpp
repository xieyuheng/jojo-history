#pragma once

#include "../libjojo.hpp"

using prim_fn = function
    <void (env_t &, obj_map_t &)>;

struct prim_o: obj_t
{
    name_vector_t name_vector;
    prim_fn fn;
    prim_o (env_t &env,
            name_vector_t name_vector,
            prim_fn fn,
            obj_map_t obj_map);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    void apply (env_t &env, size_t arity);
    string repr (env_t &env);
};

void
define_prim (env_t &env, sig_t sig, prim_fn fn);
