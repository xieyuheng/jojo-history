#pragma once

#include "../libjojo.hpp"

#include "data.hpp"

shared_ptr <obj_t>
null_c (env_t &env);

shared_ptr <obj_t>
cons_c (env_t &env,
        shared_ptr <obj_t> car,
        shared_ptr <obj_t> cdr);

bool
cons_p (env_t &env, shared_ptr <obj_t> a);

shared_ptr <obj_t>
car (env_t &env, shared_ptr <obj_t> cons);

shared_ptr <obj_t>
cdr (env_t &env, shared_ptr <obj_t> cons);

bool
null_p (env_t &env, shared_ptr <obj_t> a);

bool
list_p (env_t &env, shared_ptr <obj_t> a);

size_t
list_length (env_t &env, shared_ptr <obj_t> l);

void
test_list ();
