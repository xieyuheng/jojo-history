#pragma once

#include "../libjojo.hpp"

struct closure_o: obj_t
{
    name_vector_t name_vector;
    shared_ptr <jojo_t> jojo;
    bind_vector_t bind_vector;
    local_scope_t local_scope;
    closure_o (env_t &env,
               name_vector_t name_vector,
               shared_ptr <jojo_t> jojo,
               bind_vector_t bind_vector,
               local_scope_t local_scope);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    void apply (env_t &env, size_t arity);
    string repr (env_t &env);
};
