#pragma once

#include "libjojo.hpp"

struct obj_t
{
    tag_t tag;
    obj_map_t obj_map;
    virtual ~obj_t ();
    virtual string repr (env_t &env);
    virtual bool equal (env_t &env, shared_ptr <obj_t> obj);
    virtual void apply (env_t &env, size_t arity);
};

using sig_t = name_vector_t;

void
define (env_t &env,
        name_t name,
        shared_ptr <obj_t> obj);

name_t
name_of_sig (sig_t &sig);

name_vector_t
name_vector_of_sig (sig_t &sig);
