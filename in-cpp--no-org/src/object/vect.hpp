#pragma once

#include "../libjojo.hpp"

#include "str.hpp"
#include "list.hpp"

struct vect_o: obj_t
{
    obj_vector_t obj_vector;
    vect_o (env_t &env, obj_vector_t obj_vector);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};

bool
vect_equal (env_t &env,
            obj_vector_t &lhs,
            obj_vector_t &rhs);

bool
vect_p (env_t &env, shared_ptr <obj_t> a);

shared_ptr <vect_o>
list_to_vect (env_t &env, shared_ptr <obj_t> l);

shared_ptr <obj_t>
vect_to_list (env_t &env, shared_ptr <vect_o> vect);

void
test_vect ();
