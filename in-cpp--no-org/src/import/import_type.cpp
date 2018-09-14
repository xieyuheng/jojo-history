#include "import_type.hpp"

#include "../object/type.hpp"
#include "../object/prim.hpp"

sig_t jj_typeof_sig = { "typeof", "obj" };
void jj_typeof (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["obj"];
    auto it_box = env.box_map.find (obj->tag);
    assert (it_box != env.box_map.end ());
    auto box = it_box->second;
    env.obj_stack.push (box->obj);
}

void
import_type (env_t &env)
{
    define_type (env, "type-t");
    define_prim (env,
                 jj_typeof_sig,
                 jj_typeof);
}
