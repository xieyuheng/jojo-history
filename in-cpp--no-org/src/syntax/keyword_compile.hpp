#pragma once

#include "../libjojo.hpp"

#include "../object/keyword.hpp"
#include "../object/str.hpp"
#include "../object/list.hpp"

bool
keyword_sexp_p (env_t &env, shared_ptr <obj_t> sexp);

keyword_fn
get_keyword_fn (env_t &env, name_t name);

shared_ptr <jojo_t>
keyword_compile (env_t &env,
                 local_ref_map_t &local_ref_map,
                 shared_ptr <obj_t> sexp);
