#include "note.hpp"

#include "lit_jo.hpp"

#include "../object/str.hpp"
#include "../object/list.hpp"

shared_ptr <jojo_t>
k_note (env_t &env,
        local_ref_map_t &local_ref_map,
        shared_ptr <obj_t> body)
{
    body = cons_c (env, make_shared <str_o> (env, "note"),
                   body);
    jo_vector_t jo_vector = {
        new lit_jo_t (body),
    };
    auto jojo = make_shared <jojo_t> (jo_vector);
    return jojo;
}
