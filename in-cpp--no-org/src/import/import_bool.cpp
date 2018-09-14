#include "import_type.hpp"

#include "../object/bool.hpp"
#include "../object/data.hpp"
#include "../object/type.hpp"

shared_ptr <obj_t>
jj_true_c (env_t &env)
{
    return make_shared <data_o>
        (env, "true-t", obj_map_t ());
}

shared_ptr <obj_t>
jj_false_c (env_t &env)
{
    return make_shared <data_o>
        (env, "false-t", obj_map_t ());
}

void
import_bool (env_t &env)
{
    define_type (env, "true-t");
    define_type (env, "false-t");
    define (env, "true-c", jj_true_c (env));
    define (env, "false-c", jj_false_c (env));
}
