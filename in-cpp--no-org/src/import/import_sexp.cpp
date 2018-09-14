#include "import_sexp.hpp"

#include "../object/str.hpp"
#include "../object/prim.hpp"

#include "../sexp.hpp"

sig_t jj_scan_word_list_sig = { "scan-word-list", "code" };
// -- str-t -> (list-t str-t)
void jj_scan_word_list (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["code"];
    assert (str_p (env, obj));
    auto code = static_pointer_cast <str_o> (obj);
    env.obj_stack.push (scan_word_list (env, code));
}

sig_t jj_parse_sexp_sig = { "parse-sexp", "word-list" };
// -- (list-t str-t) -> sexp-t
void jj_parse_sexp (env_t &env, obj_map_t &obj_map)
{
    env.obj_stack.push (parse_sexp (env, obj_map ["word-list"]));
}

sig_t jj_parse_sexp_list_sig = { "parse-sexp-list", "word-list" };
// -- (list-t str-t) -> (list-t sexp-t)
void jj_parse_sexp_list (env_t &env, obj_map_t &obj_map)
{
    env.obj_stack.push (parse_sexp_list (env, obj_map ["word-list"]));
}

sig_t jj_sexp_repr_sig = { "sexp-repr", "sexp" };
// -- sexp-t ->
void jj_sexp_repr (env_t &env, obj_map_t &obj_map)
{
    auto str = sexp_repr (env, obj_map ["sexp"]);
    env.obj_stack.push (make_shared <str_o> (env, str));
}

sig_t jj_sexp_list_repr_sig = { "sexp-list-repr", "sexp-list" };
// -- (list-t sexp-t) ->
void jj_sexp_list_repr (env_t &env, obj_map_t &obj_map)
{
    auto str = sexp_list_repr (env, obj_map ["sexp-list"]);
    env.obj_stack.push (make_shared <str_o> (env, str));
}

void
import_sexp (env_t &env)
{
    define_prim (env,
                 jj_scan_word_list_sig,
                 jj_scan_word_list);
    define_prim (env,
                 jj_parse_sexp_list_sig,
                 jj_parse_sexp_list);
    define_prim (env,
                 jj_parse_sexp_sig,
                 jj_parse_sexp);
    define_prim (env,
                 jj_sexp_repr_sig,
                 jj_sexp_repr);
    define_prim (env,
                 jj_sexp_list_repr_sig,
                 jj_sexp_list_repr);
}
