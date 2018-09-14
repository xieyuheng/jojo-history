#include "import_stack.hpp"

#include "../object/prim.hpp"

sig_t jj_drop_sig = { "drop" };
void jj_drop (env_t &env, obj_map_t &obj_map)
{
    env.obj_stack.pop ();
}

void
import_stack (env_t &env)
{
    define_prim (env,
                 jj_drop_sig,
                 jj_drop);
}
