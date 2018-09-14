#include "import_list.hpp"

#include "../object/type.hpp"
#include "../object/list.hpp"
#include "../object/data.hpp"
#include "../object/data_cons.hpp"

shared_ptr <obj_t>
jj_null_c (env_t &env)
{
    return make_shared <data_o>
        (env, "null-t", obj_map_t ());
}

shared_ptr <data_cons_o>
jj_cons_c (env_t &env)
{
    return make_shared <data_cons_o>
        (env, "cons-t",
         name_vector_t ({ "car", "cdr" }),
         obj_map_t ());
}

void
import_list (env_t &env)
{
    define_type (env, "null-t");
    define_type (env, "cons-t");
    define (env, "null-c", jj_null_c (env));
    define (env, "cons-c", jj_cons_c (env));
}
