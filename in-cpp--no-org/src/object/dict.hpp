#pragma once

#include "../libjojo.hpp"

#include "str.hpp"
#include "list.hpp"

struct dict_o: obj_t
{
    dict_o (env_t &env, obj_map_t obj_map);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
    string repr (env_t &env);
};

bool
dict_p (env_t &env, shared_ptr <obj_t> a);

shared_ptr <dict_o>
list_to_dict (env_t &env, shared_ptr <obj_t> l);

shared_ptr <obj_t>
dict_to_list (env_t &env, shared_ptr <dict_o> dict);

void
test_dict ();
