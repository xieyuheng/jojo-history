#pragma once

#include "../libjojo.hpp"

shared_ptr <obj_t>
sexp_literalize (env_t &env, shared_ptr <obj_t> sexp);

shared_ptr <jojo_t>
k_quote (env_t &env,
         local_ref_map_t &local_ref_map,
         shared_ptr <obj_t> body);
