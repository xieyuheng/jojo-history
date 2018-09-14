#include "vect_compile.hpp"

#include "collect_vect_jo.hpp"

#include "../object/list.hpp"

#include "../compile.hpp"

shared_ptr <jojo_t>
vect_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <vect_o> vect)
{
    auto sexp_list = vect_to_list (env, vect);
    auto jojo = sexp_list_compile
        (env, local_ref_map, sexp_list);
    auto counter = list_length (env, sexp_list);
    jo_vector_t jo_vector = {
        new collect_vect_jo_t (counter),
    };
    auto ending_jojo = make_shared <jojo_t> (jo_vector);
    return jojo_append (jojo, ending_jojo);
}
