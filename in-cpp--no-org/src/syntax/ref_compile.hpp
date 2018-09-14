#pragma once

#include "../libjojo.hpp"

shared_ptr <jojo_t>
ref_compile (env_t &env,
             local_ref_map_t &local_ref_map,
             name_t name);
