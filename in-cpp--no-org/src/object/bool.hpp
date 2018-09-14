#pragma once

#include "../libjojo.hpp"

#include "data.hpp"

shared_ptr <obj_t>
true_c (env_t &env);

bool
true_p (env_t &env, shared_ptr <obj_t> a);

shared_ptr <obj_t>
false_c (env_t &env);

bool
false_p (env_t &env, shared_ptr <obj_t> a);

void
test_bool ();
