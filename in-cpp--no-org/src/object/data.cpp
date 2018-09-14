#include "data.hpp"

data_o::
data_o (env_t &env,
        tag_t tag,
        obj_map_t obj_map)
{
    this->tag = tag;
    this->obj_map = obj_map;
}

bool
data_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <data_o> (obj);
    return obj_map_equal (env, this->obj_map, that->obj_map);

}

string
data_o::repr (env_t &env)
{
    if (this->obj_map.size () == 0) {
        string repr = "";
        repr += this->tag;
        repr.pop_back ();
        repr.pop_back ();
        repr += "-c";
        return repr;
    }
    else {
        string repr = "(";
        repr += this->tag;
        repr.pop_back ();
        repr.pop_back ();
        repr += "-c ";
        repr += obj_map_repr (env, this->obj_map);
        repr += ")";
        return repr;
    }
}
