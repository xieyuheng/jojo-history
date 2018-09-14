#include "import_misc.hpp"

#include "../object/type.hpp"
#include "../object/prim.hpp"
#include "../object/str.hpp"
#include "../object/bool.hpp"

sig_t jj_repr_sig = { "repr", "obj" };
void jj_repr (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["obj"];
    env.obj_stack.push
        (make_shared <str_o>
         (env, obj->repr (env)));
}

sig_t jj_print_sig = { "print", "obj" };
void jj_print (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["obj"];
    cout << obj->repr (env) << flush;
    env.obj_stack.push (obj);
}

sig_t jj_println_sig = { "println", "obj" };
void jj_println (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["obj"];
    cout << obj->repr (env) << "\n" << flush;
    env.obj_stack.push (obj);
}

sig_t jj_nl_sig = { "nl" };
void jj_nl (env_t &env, obj_map_t &obj_map)
{
    cout << "\n" << flush;
    auto nl = make_shared <str_o> (env, "\n");
    env.obj_stack.push (nl);
}

sig_t jj_equal_sig = { "equal", "lhs", "rhs" };
void jj_equal (env_t &env, obj_map_t &obj_map)
{
    auto lhs = obj_map ["lhs"];
    auto rhs = obj_map ["rhs"];
    if (obj_equal (env, lhs, rhs))
        env.obj_stack.push (true_c (env));
    else
        env.obj_stack.push (false_c (env));
}

sig_t jj_env_report_sig = { "env-report" };
void jj_env_report (env_t &env, obj_map_t &obj_map)
{
    env.report ();
    env.obj_stack.push (true_c (env));
}

void
import_misc (env_t &env)
{
    define_type (env, "closure-t");
    define_type (env, "data-cons-t");
    define_type (env, "prim-t");
    define_prim (env,
                 jj_repr_sig,
                 jj_repr);
    define_prim (env,
                 jj_print_sig,
                 jj_print);
    define_prim (env,
                 jj_println_sig,
                 jj_println);
    define_prim (env,
                 jj_nl_sig,
                 jj_nl);
    define_prim (env,
                 jj_equal_sig,
                 jj_equal);
    define_prim (env,
                 jj_env_report_sig,
                 jj_env_report);
}
