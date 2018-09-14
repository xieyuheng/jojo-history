#include "assert.hpp"

#include "assert_jo.hpp"

#include "../compile.hpp"

shared_ptr <jojo_t>
k_assert (env_t &env,
          local_ref_map_t &local_ref_map,
          shared_ptr <obj_t> body)
{
    auto jojo = sexp_list_compile (env, local_ref_map, body);
    jo_vector_t jo_vector = {
        new assert_jo_t (body, jojo),
    };
    return make_shared <jojo_t> (jo_vector);
}
