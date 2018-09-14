#include "compile.hpp"

#include "object/str.hpp"
#include "object/list.hpp"
#include "object/vect.hpp"
#include "object/dict.hpp"

#include "syntax/field_string_compile.hpp"
#include "syntax/string_string_compile.hpp"
#include "syntax/key_string_compile.hpp"
#include "syntax/int_string_compile.hpp"
#include "syntax/ref_compile.hpp"
#include "syntax/vect_compile.hpp"
#include "syntax/dict_compile.hpp"
#include "syntax/keyword_compile.hpp"
#include "syntax/call_compile.hpp"

shared_ptr <jojo_t>
string_compile (env_t &env,
                local_ref_map_t &local_ref_map,
                string str)
{
    if (field_string_p (str))
        return field_string_compile (env, local_ref_map, str);
    else if (string_string_p (str))
        return string_string_compile (env, local_ref_map, str);
    else if (key_string_p (str))
        return key_string_compile (env, local_ref_map, str);
    else if (int_string_p (str))
        return int_string_compile (env, local_ref_map, str);
    else
        return ref_compile (env, local_ref_map, str);
}

shared_ptr <jojo_t>
sexp_compile (env_t &env,
              local_ref_map_t &local_ref_map,
              shared_ptr <obj_t> sexp)
{
    if (str_p (env, sexp)) {
        auto str = static_pointer_cast <str_o> (sexp);
        return string_compile (env, local_ref_map, str->str);
    }
    if (vect_p (env, sexp)) {
        auto vect = static_pointer_cast <vect_o> (sexp);
        return vect_compile (env, local_ref_map, vect);
    }
    if (dict_p (env, sexp)) {
        auto dict = static_pointer_cast <dict_o> (sexp);
        return dict_compile (env, local_ref_map, dict);
    }
    if (keyword_sexp_p (env, sexp)) {
        return keyword_compile (env, local_ref_map, sexp);
    }
    else {
        assert (cons_p (env, sexp));
        return call_compile (env, local_ref_map, sexp);
    }
}

shared_ptr <jojo_t>
sexp_list_compile (env_t &env,
                   local_ref_map_t &local_ref_map,
                   shared_ptr <obj_t> sexp_list)
{
    auto jojo = make_shared <jojo_t> (jo_vector_t ());
    if (null_p (env, sexp_list))
        return jojo;
    else {
        assert (cons_p (env, sexp_list));
        auto head_jojo = sexp_compile
            (env, local_ref_map, car (env, sexp_list));
        auto body_jojo = sexp_list_compile
            (env, local_ref_map, cdr (env, sexp_list));
        return jojo_append (head_jojo, body_jojo);
    }
}
