#include "assign.hpp"

#include "../eval.hpp"

#include "../object/type.hpp"
#include "../object/data.hpp"
#include "../object/data_cons.hpp"
#include "../object/list.hpp"
#include "../object/vect.hpp"
// #include "../object/dict.hpp"
#include "../object/str.hpp"

// (= <name> (data ...))

// [todo]
// - type must all be top-level
//   - and (= a.b.c ...) is not handled.

bool
assign_data_p (env_t &env, shared_ptr <obj_t> body)
{
    if (! cons_p (env, body))
        return false;
    if (! str_p (env, car (env, body)))
        return false;
    if (! cons_p (env, cdr (env, body)))
        return false;
    if (! cons_p (env, car (env, cdr (env, body))))
        return false;
    if (! str_p (env, car (env, car (env, cdr (env, body)))))
        return false;
    auto str = static_pointer_cast <str_o>
        (car (env, car (env, cdr (env, body))));
    return str->str == "data";
}

name_t
type_name_to_data_name (name_t type_name)
{
    auto data_name = type_name;
    data_name.pop_back ();
    data_name.pop_back ();
    data_name += "-c";
    return data_name;
}

void
tk_assign_data (env_t &env, shared_ptr <obj_t> body)
{
    auto head = static_pointer_cast <str_o> (car (env, body));
    auto type_name = head->str;
    auto data_name = type_name_to_data_name (type_name);
    auto type_tag = type_name;
    auto rest = cdr (env, body);
    auto data_body = cdr (env, (car (env, rest)));
    if (null_p (env, data_body)) {
        auto data = make_shared <data_o>
            (env, type_tag, obj_map_t ());
        define (env, data_name, data);
        auto type = make_shared <type_o>
            (env, type_tag, obj_map_t ());
        define (env, type_name, type);
    }
    else {
        auto name_vect = list_to_vect (env, data_body);
        auto name_vector = name_vector_t ();
        for (auto obj: name_vect->obj_vector) {
            auto str = static_pointer_cast <str_o> (obj);
            name_vector.push_back (str->str);
        }
        auto data_cons = make_shared <data_cons_o>
            (env, type_tag, name_vector, obj_map_t ());
        define (env, data_name, data_cons);
        auto type = make_shared <type_o>
            (env, type_tag, obj_map_t ());
        define (env, type_name, type);
    }
}

// (= (<name> ...) ...)

bool
assign_lambda_sugar_p (env_t &env, shared_ptr <obj_t> body)
{
    if (! cons_p (env, body))
        return false;
    if (! cons_p (env, car (env, body)))
        return false;
    return true;
}

shared_ptr <obj_t>
assign_lambda_desugar (env_t &env, shared_ptr <obj_t> body)
{
    auto head = car (env, body);
    auto name = car (env, head);
    auto lambda_body = cdr (env, body);
    lambda_body = cons_c
        (env,
         list_to_vect (env, cdr (env, head)),
         lambda_body);
    lambda_body = cons_c
        (env,
         make_shared <str_o> (env, "lambda"),
         lambda_body);
    lambda_body = cons_c
        (env,
         lambda_body,
         null_c (env));
    return cons_c (env, name, lambda_body);
}

// (= <name> ...)

shared_ptr <obj_t>
sexp_substitute_recur (env_t &env,
                       shared_ptr <obj_t> sub,
                       shared_ptr <obj_t> sexp)
{
    if (str_p (env, sexp)) {
        auto str = static_pointer_cast <str_o> (sexp);
        if (str->str == "recur")
            return sub;
        else
            return sexp;
    }
    if (cons_p (env, sexp))
        return cons_c
            (env,
             sexp_substitute_recur (env, sub, car (env, sexp)),
             sexp_substitute_recur (env, sub, cdr (env, sexp)));
    if (vect_p (env, sexp)) {
        auto vect_sexp = static_pointer_cast <vect_o> (sexp);
        auto list_sexp = vect_to_list (env, vect_sexp);
        auto new_list_sexp = sexp_substitute_recur (env, sub, list_sexp);
        return list_to_vect (env, new_list_sexp);
    }
    else
        return sexp;
}

shared_ptr <obj_t>
lambda_sexp_patch_this (env_t &env, shared_ptr <obj_t> lambda_sexp)
{
    auto vect = static_pointer_cast <vect_o>
        (car (env, (cdr (env, lambda_sexp))));
    auto vector = vect->obj_vector;
    reverse (vector.begin (),
             vector.end ());
    vector.push_back (make_shared <str_o> (env, "this"));
    reverse (vector.begin (),
             vector.end ());
    return cons_c (env,
                   car (env, lambda_sexp),
                   cons_c (env,
                           make_shared <vect_o> (env, vector),
                           cdr (env, cdr (env, lambda_sexp))));
}

shared_ptr <obj_t>
rest_patch_this (env_t &env, shared_ptr <obj_t> rest)
{
    if (null_p (env, rest))
        return rest;
    auto sexp = car (env, rest);
    if (! cons_p (env, sexp))
        return rest;
    auto head = car (env, sexp);
    if (! str_p (env, head))
        return rest;
    auto str = static_pointer_cast <str_o> (head);
    if (str->str == "lambda") {
        return cons_c
            (env,
             lambda_sexp_patch_this (env, sexp),
             cdr (env, rest));
    }
    else return rest;
}

void
tk_assign_value (env_t &env, shared_ptr <obj_t> body)
{
    auto head = static_pointer_cast <str_o> (car (env, body));
    auto rest = cdr (env, body);
    auto name = head->str;
    string prefix = "";
    auto string_vector = string_split (name, '.');
    assert (string_vector.size () <= 2);
    if (string_vector.size () == 2) {
        prefix = string_vector [0];
        name = string_vector [1];
        rest = rest_patch_this (env, rest);
    }
    rest = sexp_substitute_recur (env, head, rest);
    sexp_list_eval (env, rest);
    auto obj = env.obj_stack.top ();
    env.obj_stack.pop ();
    assign (env, prefix, name, obj);
}

void
tk_assign (env_t &env, shared_ptr <obj_t> body)
{
    if (assign_data_p (env, body))
        tk_assign_data (env, body);
    else if (assign_lambda_sugar_p (env, body))
        tk_assign_value (env, assign_lambda_desugar (env, body));
    else
        tk_assign_value (env, body);
}
