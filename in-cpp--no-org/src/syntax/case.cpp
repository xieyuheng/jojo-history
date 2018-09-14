#include "case.hpp"

#include "case_jo.hpp"

#include "../object/str.hpp"
#include "../object/list.hpp"

#include "../compile.hpp"

shared_ptr <jojo_t>
case_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <obj_t> body)
{
    auto jojo_map = jojo_map_t ();
    shared_ptr <jojo_t> default_jojo = nullptr;
    while (! null_p (env, body)) {
        auto one = car (env, body);
        auto head = static_pointer_cast <str_o> (car (env, one));
        auto rest = cdr (env, one);
        auto name = head->str;
        if (name == "_") {
            auto jojo = sexp_list_compile (env, local_ref_map, rest);
            body = cdr (env, body);
            default_jojo = jojo;
        }
        else {
            auto tag = name;
            auto jojo = sexp_list_compile (env, local_ref_map, rest);
            jojo_map.insert (make_pair (tag, jojo));
            body = cdr (env, body);
        }
    }
    jo_vector_t jo_vector = {
        new case_jo_t (jojo_map, default_jojo),
    };
    return make_shared <jojo_t> (jo_vector);
}

shared_ptr <jojo_t>
k_case (env_t &env,
        local_ref_map_t &local_ref_map,
        shared_ptr <obj_t> body)
{
    auto head = car (env, body);
    auto rest = cdr (env, body);
    auto head_jojo = sexp_compile (env, local_ref_map, head);
    auto rest_jojo = case_compile (env, local_ref_map, rest);
    return jojo_append (head_jojo, rest_jojo);
}
