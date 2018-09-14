#include "ref_compile.hpp"

#include "ref_jo.hpp"
#include "local_ref_jo.hpp"

shared_ptr <jojo_t>
ref_compile (env_t &env,
             local_ref_map_t &local_ref_map,
             name_t name)
{
    auto jo_vector = jo_vector_t ();
    auto it = local_ref_map.find (name);
    if (it != local_ref_map.end ()) {
        auto local_ref = it->second;
        auto local_ref_jo = new local_ref_jo_t
            (local_ref.first,
             local_ref.second);
        jo_vector.push_back (local_ref_jo);
    }
    else
        jo_vector.push_back (new ref_jo_t (boxing (env, name)));
    return make_shared <jojo_t> (jo_vector);
}
