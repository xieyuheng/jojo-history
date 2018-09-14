#pragma once

#include "../libjojo.hpp"

bool
int_string_p (string str);

shared_ptr <jojo_t>
int_string_compile (env_t &env,
                    local_ref_map_t &local_ref_map,
                    string str);
