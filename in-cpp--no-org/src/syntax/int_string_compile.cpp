#include "int_string_compile.hpp"

#include "lit_jo.hpp"

#include "../object/int.hpp"

bool
int_string_p (string str)
{
    auto size = str.size ();
    if (size < 1) return false;
    if (str [0] == '-')
        return int_string_p (str.substr (1, size - 1));
    auto pos = str.find_first_not_of ("0123456789");
    return pos == string::npos;
}

shared_ptr <jojo_t>
int_string_compile (env_t &env,
                    local_ref_map_t &local_ref_map,
                    string str)
{
    auto i = stoi (str);
    jo_vector_t jo_vector = {
        new lit_jo_t (make_shared <int_o> (env, i)),
    };
    auto jojo = make_shared <jojo_t> (jo_vector);
    return jojo;
}
