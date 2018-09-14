#include "type.hpp"

type_o::type_o (env_t &env,
                tag_t type_tag,
                obj_map_t obj_map)
{
    this->tag = "type-t";
    this->type_tag = type_tag;
    this->obj_map = obj_map;
}

string
type_o::repr (env_t &env)
{
    return this->type_tag;
}

bool
type_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <type_o> (obj);
    if (this->type_tag != that->type_tag) return false;
    return true;
}

void
assign (env_t &env,
        name_t prefix,
        name_t name,
        shared_ptr <obj_t> obj)
{
    if (prefix == "") {
        define (env, name, obj);
        return;
    }
    auto it = env.box_map.find (prefix + "-t");
    if (it != env.box_map.end ()) {
        auto box = it->second;
        assert (! box->empty_p);
        assert (box->obj->tag == "type-t");
        auto type = static_pointer_cast <type_o> (box->obj);
        type->obj_map [name] = obj;
    }
    else {
        cout << "- fatal error : assign fail" << "\n";
        cout << "  unknown prefix : " << prefix << "\n";
        exit (1);
    }
}

bool
tag_name_p (name_t name)
{
    auto size = name.size ();
    if (size < 3) return false;
    if (name [size - 1] != 't') return false;
    if (name [size - 2] != '-') return false;
    return true;
}

void
define_type (env_t &env, name_t name)
{
    define (env, name, make_shared <type_o>
            (env, name, obj_map_t ()));
}

void
test_type ()
{

}
