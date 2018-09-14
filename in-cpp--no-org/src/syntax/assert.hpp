#pragma once

#include "../libjojo.hpp"

shared_ptr <jojo_t>
k_assert (env_t &env,
          local_ref_map_t &local_ref_map,
          shared_ptr <obj_t> body);
