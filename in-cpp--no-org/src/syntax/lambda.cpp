#include "lambda.hpp"

#include "lambda_jo.hpp"

#include "../object/str.hpp"
#include "../object/list.hpp"
#include "../object/vect.hpp"

#include "../compile.hpp"

shared_ptr <obj_t>
lambda_patch_drop (env_t &env, shared_ptr <obj_t> sexp_list)
{
    assert (cons_p (env, sexp_list));
    auto head = car (env, sexp_list);
    auto rest = cdr (env, sexp_list);
    if (null_p (env, rest)) return sexp_list;
    else {
        auto drop = cons_c
            (env, make_shared <str_o> (env, "drop"),
             null_c (env));
        sexp_list = lambda_patch_drop (env, rest);
        sexp_list = cons_c (env, drop, sexp_list);
        sexp_list = cons_c (env, head, sexp_list);
        return sexp_list;
    }
}

name_vector_t
obj_vector_to_name_vector (env_t &env, obj_vector_t &obj_vect)
{
    auto name_vector = name_vector_t ();
    for (auto &obj: obj_vect) {
        assert (str_p (env, obj));
        auto str = static_pointer_cast <str_o> (obj);
        name_vector.push_back (str->str);
    }
    return name_vector;
}

shared_ptr <jojo_t>
k_lambda (env_t &env,
          local_ref_map_t &old_local_ref_map,
          shared_ptr <obj_t> body)
{
    auto name_vect = static_pointer_cast <vect_o> (car (env, body));
    auto rest = cdr (env, body);
    auto name_vector = obj_vector_to_name_vector
        (env, name_vect->obj_vector);
    auto local_ref_map = local_ref_map_extend
        (env, old_local_ref_map, name_vector);
    rest = lambda_patch_drop (env, rest);
    auto rest_jojo = sexp_list_compile
        (env, local_ref_map, rest);
    jo_vector_t jo_vector = {
        new lambda_jo_t (name_vector, rest_jojo),
    };
    return make_shared <jojo_t> (jo_vector);
}
