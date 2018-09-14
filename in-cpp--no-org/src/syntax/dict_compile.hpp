#pragma once

#include "../libjojo.hpp"

#include "../object/dict.hpp"

shared_ptr <jojo_t>
dict_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <dict_o> dict);
