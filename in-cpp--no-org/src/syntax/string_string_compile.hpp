#pragma once

#include "../libjojo.hpp"

bool
string_string_p (string str);

shared_ptr <jojo_t>
string_string_compile (env_t &env,
                       local_ref_map_t &local_ref_map,
                       string str);
