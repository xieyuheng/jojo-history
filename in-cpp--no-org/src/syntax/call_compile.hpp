#pragma once

#include "../libjojo.hpp"

bool
field_head_p (env_t &env, shared_ptr <obj_t> head);

shared_ptr <jojo_t>
call_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <obj_t> sexp);
