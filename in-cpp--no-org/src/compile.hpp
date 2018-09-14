#pragma once

#include "libjojo.hpp"

shared_ptr <jojo_t>
string_compile (env_t &env,
                local_ref_map_t &local_ref_map,
                string str);

shared_ptr <jojo_t>
sexp_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <obj_t> sexp);

shared_ptr <jojo_t>
sexp_list_compile (env_t &env,
                   local_ref_map_t &local_ref_map,
                   shared_ptr <obj_t> sexp_list);
