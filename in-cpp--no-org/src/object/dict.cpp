#include "dict.hpp"

dict_o::dict_o (env_t &env, obj_map_t obj_map)
{
    this->tag = "dict-t";
    this->obj_map = obj_map;
}

bool
dict_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <dict_o> (obj);
    return obj_map_equal (env, this->obj_map, that->obj_map);
}

string
dict_o::repr (env_t &env)
{
    string repr = "{";
    repr += obj_map_repr (env, this->obj_map);
    repr += "}";
    return repr;
}

bool
dict_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "dict-t";
}

shared_ptr <dict_o>
list_to_dict (env_t &env, shared_ptr <obj_t> l)
{
    auto obj_map = obj_map_t ();
    while (cons_p (env, l)) {
        auto head = car (env, l);
        assert (str_p (env, head));
        auto key = static_pointer_cast <str_o> (head);
        assert (cons_p (env, cdr (env, l)));
        auto obj = car (env, cdr (env, l));
        obj_map [key->str] = obj;
        l = cdr (env, cdr (env, l));
    }
    return make_shared <dict_o> (env, obj_map);
}

shared_ptr <obj_t>
dict_to_list (env_t &env, shared_ptr <dict_o> dict)
{
    auto result = null_c (env);
    for (auto &kv: dict->obj_map) {
        auto str = make_shared <str_o> (env, kv.first);
        auto obj = kv.second;
        result = cons_c (env, obj, result);
        result = cons_c (env, str, result);
    }
    return result;
}

void
test_dict ()
{
}
