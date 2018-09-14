#include "eval.hpp"

#include "object/top_keyword.hpp"

#include "sexp.hpp"
#include "compile.hpp"

bool
top_keyword_sexp_p (env_t &env, shared_ptr <obj_t> sexp)
{
    if (! cons_p (env, sexp)) return false;
    if (! str_p (env, (car (env, sexp)))) return false;
    auto head = static_pointer_cast <str_o> (car (env, sexp));
    auto name = head->str;
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        box_t *box = it->second;
        if (box->empty_p) return false;
        if (top_keyword_p (env, box->obj)) return true;
        else return false;
    }
    else {
        return false;
    }
}

top_keyword_fn
get_top_keyword_fn (env_t &env, name_t name)
{
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        box_t *box = it->second;
        if (box->empty_p) {
            cout << "- fatal error: get_top_keyword_fn fail\n";
            exit (1);
        }
        if (top_keyword_p (env, box->obj)) {
            auto top_keyword = static_pointer_cast <top_keyword_o>
                (box->obj);
            return top_keyword->fn;
        }
        else {
            cout << "- fatal error: get_top_keyword_fn fail\n";
            exit (1);
        };
    }
    else {
        cout << "- fatal error: get_top_keyword_fn fail\n";
        exit (1);
    }
}

void
jojo_run (env_t &env, shared_ptr <jojo_t> jojo)
{
    auto base = env.frame_stack.size ();
    env.frame_stack.push (new_frame_from_jojo (jojo));
    env.run_with_base (base);
}

void
sexp_eval (env_t &env, shared_ptr <obj_t> sexp)
{
    if (top_keyword_sexp_p (env, sexp)) {
        auto head = static_pointer_cast <str_o> (car (env, sexp));
        auto body = cdr (env, sexp);
        auto name = head->str;
        auto fn = get_top_keyword_fn (env, name);
        fn (env, body);
    }
    else {
        auto local_ref_map = local_ref_map_t ();
        auto jojo = sexp_compile (env, local_ref_map, sexp);
        jojo_run (env, jojo);
    }
}

void
sexp_list_eval (env_t &env, shared_ptr <obj_t> sexp_list)
{
    if (null_p (env, sexp_list))
        return;
    else {
        sexp_eval (env, car (env, sexp_list));
        sexp_list_eval (env, cdr (env, sexp_list));
    }
}

void
top_sexp_eval (env_t &env, shared_ptr <obj_t> sexp)
{
    if (top_keyword_sexp_p (env, sexp)) {
        auto head = static_pointer_cast <str_o> (car (env, sexp));
        auto body = cdr (env, sexp);
        auto name = head->str;
        auto fn = get_top_keyword_fn (env, name);
        fn (env, body);
    }
    else {
        auto local_ref_map = local_ref_map_t ();
        auto jojo = sexp_compile (env, local_ref_map, sexp);
        jojo_run (env, jojo);
        if (! env.obj_stack.empty ())
            env.obj_stack.pop ();
    }
}

void
top_sexp_list_eval (env_t &env, shared_ptr <obj_t> sexp_list)
{
    if (null_p (env, sexp_list))
        return;
    else {
        top_sexp_eval (env, car (env, sexp_list));
        top_sexp_list_eval (env, cdr (env, sexp_list));
    }
}

void
code_eval (env_t &env, shared_ptr <str_o> code)
{
    auto word_list = scan_word_list (env, code);
    auto sexp_list = parse_sexp_list (env, word_list);
    top_sexp_list_eval (env, sexp_list);
}
