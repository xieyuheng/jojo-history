#pragma once

#include "../libjojo.hpp"

struct int_o: obj_t
{
    int i;
    int_o (env_t &env, int i);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};

bool
int_p (env_t &env, shared_ptr <obj_t> a);

void
test_int ();
