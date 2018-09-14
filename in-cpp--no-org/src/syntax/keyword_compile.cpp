#include "keyword_compile.hpp"

bool
keyword_sexp_p (env_t &env, shared_ptr <obj_t> sexp)
{
    if (! cons_p (env, sexp)) return false;
    if (! str_p (env, (car (env, sexp)))) return false;
    auto head = static_pointer_cast <str_o> (car (env, sexp));
    auto name = head->str;
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        box_t *box = it->second;
        if (box->empty_p) return false;
        if (keyword_p (env, box->obj)) return true;
        else return false;
    }
    else {
        return false;
    }
}

keyword_fn
get_keyword_fn (env_t &env, name_t name)
{
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        box_t *box = it->second;
        if (box->empty_p) {
            cout << "- fatal error: get_keyword_fn fail\n";
            exit (1);
        }
        if (keyword_p (env, box->obj)) {
            auto keyword = static_pointer_cast <keyword_o>
                (box->obj);
            return keyword->fn;
        }
        else {
            cout << "- fatal error: get_keyword_fn fail\n";
            exit (1);
        };
    }
    else {
        cout << "- fatal error: get_keyword_fn fail\n";
        exit (1);
    }
}

shared_ptr <jojo_t>
keyword_compile (env_t &env,
                 local_ref_map_t &local_ref_map,
                 shared_ptr <obj_t> sexp)
{
    auto head = static_pointer_cast <str_o> (car (env, sexp));
    auto body = cdr (env, sexp);
    auto name = head->str;
    auto fn = get_keyword_fn (env, name);
    return fn (env, local_ref_map, body);
}
