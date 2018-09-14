#include "dict_compile.hpp"

#include "collect_dict_jo.hpp"

#include "../object/list.hpp"

#include "../compile.hpp"

shared_ptr <jojo_t>
dict_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <dict_o> dict)
{
    auto sexp_list = dict_to_list (env, dict);
    auto jojo = sexp_list_compile
        (env, local_ref_map, sexp_list);
    auto counter = list_length (env, sexp_list);
    counter = counter / 2;
    jo_vector_t jo_vector = {
        new collect_dict_jo_t (counter),
    };
    auto ending_jojo = make_shared <jojo_t> (jo_vector);
    return jojo_append (jojo, ending_jojo);
}
