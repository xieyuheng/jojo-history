#include "field_string_compile.hpp"

#include "field_jo.hpp"

#include "../compile.hpp"

bool
field_string_p (string str)
{
    auto pos = str.find (".");
    return (pos != string::npos);
}

shared_ptr <jojo_t>
field_string_compile (env_t &env,
                      local_ref_map_t &local_ref_map,
                      string str)
{
    auto string_vector = string_split (str, '.');
    auto jojo = string_compile
        (env, local_ref_map, string_vector [0]);
    auto begin = string_vector.begin () + 1;
    auto end = string_vector.end ();
    for (auto it = begin; it != end; it++) {
        jo_vector_t jo_vector = {
            new field_jo_t (*it),
        };
        auto field_jojo = make_shared <jojo_t> (jo_vector);
        jojo = jojo_append (jojo, field_jojo);
    }
    return jojo;
}
