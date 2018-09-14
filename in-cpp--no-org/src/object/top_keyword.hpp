#pragma once

#include "../libjojo.hpp"

using top_keyword_fn = function
    <void (env_t &, shared_ptr <obj_t>)>;

struct top_keyword_o: obj_t
{
    top_keyword_fn fn;
    top_keyword_o (env_t &env, top_keyword_fn fn);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
};

bool
top_keyword_p (env_t &env, shared_ptr <obj_t> a);

void
define_top_keyword (env_t &env, name_t name, top_keyword_fn fn);
