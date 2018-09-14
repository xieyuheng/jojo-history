#include "import_vect.hpp"

#include "../object/type.hpp"
#include "../object/prim.hpp"
#include "../object/vect.hpp"

sig_t jj_list_to_vect_sig = { "list-to-vect", "list" };
// -- (list-t t) -> (vect-t t)
void jj_list_to_vect (env_t &env, obj_map_t &obj_map)
{
    env.obj_stack.push (list_to_vect (env, obj_map ["list"]));
}

sig_t jj_vect_to_list_sig = { "vect-to-list", "vect" };
// -- (vect-t t) -> (list-t t)
void jj_vect_to_list (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["vect"];
    assert (vect_p (env, obj));
    auto vect = static_pointer_cast <vect_o> (obj);
    env.obj_stack.push (vect_to_list (env, vect));
}

void
import_vect (env_t &env)
{
    define_type (env, "vect-t");
    define_prim (env,
                 jj_list_to_vect_sig,
                 jj_list_to_vect);
    define_prim (env,
                 jj_vect_to_list_sig,
                 jj_vect_to_list);
}
