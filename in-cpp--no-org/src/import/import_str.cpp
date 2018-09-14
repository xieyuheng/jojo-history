#include "import_str.hpp"

#include "../object/type.hpp"
#include "../object/prim.hpp"
#include "../object/str.hpp"

sig_t jj_str_print_sig = { "str-print", "str" };
// -- str-t ->
void jj_str_print (env_t &env, obj_map_t &obj_map)
{
    auto obj = obj_map ["str"];
    assert (str_p (env, obj));
    auto str = static_pointer_cast <str_o> (obj);
    cout << str->str;
}

void
import_str (env_t &env)
{
    define_type (env, "str-t");
    define_prim (env,
                 jj_str_print_sig,
                 jj_str_print);
}
