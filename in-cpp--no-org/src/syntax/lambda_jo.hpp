#pragma once

#include "../libjojo.hpp"

struct lambda_jo_t: jo_t
{
    name_vector_t name_vector;
    shared_ptr <jojo_t> jojo;
    lambda_jo_t (name_vector_t name_vector,
                 shared_ptr <jojo_t> jojo);
    jo_t * copy ();
    void exe (env_t &env, local_scope_t &local_scope);
    string repr (env_t &env);
};
