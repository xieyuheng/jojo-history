#pragma once

#include "../libjojo.hpp"

using keyword_fn = function
    <shared_ptr <jojo_t>
     (env_t &,
      local_ref_map_t &,
      shared_ptr <obj_t>)>;

struct keyword_o: obj_t
{
    keyword_fn fn;
    keyword_o (env_t &env, keyword_fn fn);
    bool equal (env_t &env, shared_ptr <obj_t> obj);
};

bool
keyword_p (env_t &env, shared_ptr <obj_t> a);

void
define_keyword (env_t &env, name_t name, keyword_fn fn);
