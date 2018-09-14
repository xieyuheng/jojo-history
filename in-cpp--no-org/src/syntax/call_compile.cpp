#include "call_compile.hpp"

#include "apply_jo.hpp"

#include "field_string_compile.hpp"

#include "../object/str.hpp"
#include "../object/list.hpp"

#include "../compile.hpp"

bool
field_head_p (env_t &env, shared_ptr <obj_t> head)
{
    if (! str_p (env, head)) return false;
    auto str = static_pointer_cast <str_o> (head);
    return field_string_p (str->str);
}

shared_ptr <jojo_t>
call_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <obj_t> sexp)
{
    auto head = car (env, sexp);
    auto body = cdr (env, sexp);
    auto jo_vector = jo_vector_t ();
    if (field_head_p (env, head)) {
        jo_vector.push_back
            (new apply_jo_t (list_length (env, body) + 1));
    }
    else {
        jo_vector.push_back
            (new apply_jo_t (list_length (env, body)));
    }
    auto jojo = make_shared <jojo_t> (jo_vector);
    auto head_jojo = sexp_compile (env, local_ref_map, head);
    auto body_jojo = sexp_list_compile (env, local_ref_map, body);
    jojo = jojo_append (head_jojo, jojo);
    jojo = jojo_append (body_jojo, jojo);
    return jojo;
}
