#include "string_string_compile.hpp"

#include "lit_jo.hpp"

#include "../object/str.hpp"

bool
string_string_p (string str)
{
    auto size = str.size ();
    if (size < 2) return false;
    if (str [0] != '"') return false;
    if (str [size-1] != '"') return false;
    return true;
}

shared_ptr <jojo_t>
string_string_compile (env_t &env,
                       local_ref_map_t &local_ref_map,
                       string str)
{
    auto size = str.size () - 2;
    str = str.substr (1, size);
    jo_vector_t jo_vector = {
        new lit_jo_t (make_shared <str_o> (env, str)),
    };
    auto jojo = make_shared <jojo_t> (jo_vector);
    return jojo;
}
