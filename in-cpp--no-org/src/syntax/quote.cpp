#include "quote.hpp"

#include "lit_jo.hpp"

#include "int_string_compile.hpp"
#include "string_string_compile.hpp"
#include "key_string_compile.hpp"

#include "../object/str.hpp"
#include "../object/int.hpp"
#include "../object/list.hpp"
#include "../object/vect.hpp"
#include "../object/dict.hpp"

shared_ptr <obj_t>
str_sexp_literalize (env_t &env, shared_ptr <str_o> sexp)
{
    auto str = sexp->str;
    if (int_string_p (str)) {
        auto i = stoi (str);
        return make_shared <int_o> (env, i);
    }
    if (string_string_p (str)) {
        auto size = str.size () - 2;
        str = str.substr (1, size);
        return make_shared <str_o> (env, str);
    }
    if (key_string_p (str)) {
        auto size = str.size () - 1;
        str = str.substr (0, size);
        return make_shared <str_o> (env, str);
    }
    else {
        return sexp;
    }
}

shared_ptr <obj_t>
vect_sexp_literalize (env_t &env, shared_ptr <vect_o> vect)
{
    auto obj_vector = obj_vector_t ();
    for (auto &sexp: vect->obj_vector) {
        obj_vector.push_back (sexp_literalize (env, sexp));
    }
    return make_shared <vect_o> (env, obj_vector);
}

shared_ptr <obj_t>
dict_sexp_literalize (env_t &env, shared_ptr <dict_o> dict)
{
    auto obj_map = obj_map_t ();
    for (auto &kv: dict->obj_map) {
        auto key = kv.first;
        auto sexp = kv.second;
        obj_map.insert
            (make_pair (key, sexp_literalize (env, sexp)));
    }
    return make_shared <dict_o> (env, obj_map);
}

shared_ptr <obj_t>
sexp_literalize (env_t &env, shared_ptr <obj_t> sexp)
{
    if (str_p (env, sexp))
        return str_sexp_literalize
            (env, static_pointer_cast <str_o> (sexp));
    if (vect_p (env, sexp))
        return vect_sexp_literalize
            (env, static_pointer_cast <vect_o> (sexp));
    if (dict_p (env, sexp))
        return dict_sexp_literalize
            (env, static_pointer_cast <dict_o> (sexp));
    if (null_p (env, sexp))
        return sexp;
    else {
        assert (cons_p (env, sexp));
        return cons_c
            (env,
             sexp_literalize (env, car (env, sexp)),
             sexp_literalize (env, cdr (env, sexp)));
    }
}

shared_ptr <jojo_t>
k_quote (env_t &env,
         local_ref_map_t &local_ref_map,
         shared_ptr <obj_t> body)
{
    assert (cons_p (env, body));
    assert (null_p (env, cdr (env, body)));
    auto sexp = car (env, body);
    jo_vector_t jo_vector = {
        new lit_jo_t (sexp_literalize (env, sexp)),
    };
    auto jojo = make_shared <jojo_t> (jo_vector);
    return jojo;
}
