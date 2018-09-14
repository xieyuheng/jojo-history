#include "data_cons.hpp"
#include "data.hpp"

data_cons_o::
data_cons_o (env_t &env,
             tag_t type_tag,
             name_vector_t name_vector,
             obj_map_t obj_map)
{
    this->tag = "data-cons-t";
    this->type_tag = type_tag;
    this->name_vector = name_vector;
    this->obj_map = obj_map;
}

void
data_cons_o::apply (env_t &env, size_t arity)
{
    auto size = this->name_vector.size ();
    auto have = this->obj_map.size ();
    auto lack = size - have;
    if (lack == arity) {
        auto lack_name_vector = name_vector_obj_map_lack
            (this->name_vector, this->obj_map);
        auto obj_map = pick_up_obj_map_and_merge
            (env, lack_name_vector, this->obj_map);
        auto data = make_shared <data_o>
            (env, this->type_tag, obj_map);
        env.obj_stack.push (data);
    }
    else if (arity < lack) {
        auto lack_name_vector = name_vector_obj_map_arity_lack
            (this->name_vector, this->obj_map, arity);
        auto obj_map = pick_up_obj_map_and_merge
            (env, lack_name_vector, this->obj_map);
        auto data_cons = make_shared <data_cons_o>
            (env, this->type_tag, this->name_vector, obj_map);
        env.obj_stack.push (data_cons);
    }
    else {
        cout << "- fatal error : data_cons_o::apply" << "\n"
             << "  over-arity apply" << "\n"
             << "  arity > lack" << "\n"
             << "  arity : " << arity << "\n"
             << "  lack : " << lack << "\n";
        exit (1);
    }
}

bool
data_cons_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <data_cons_o> (obj);
    if (this->type_tag != that->type_tag) return false;
    return obj_map_equal (env, this->obj_map, that->obj_map);
}

string
data_cons_o::repr (env_t &env)
{
    if (this->name_vector.size () == 0) {
        string repr = "";
        repr += this->type_tag;
        repr.pop_back ();
        repr.pop_back ();
        repr += "-c";
        return repr;
    }
    else {
        string repr = "(";
        repr += this->type_tag;
        repr.pop_back ();
        repr.pop_back ();
        repr += "-c ";
        repr += name_vector_and_obj_map_repr
            (env, this->name_vector, this->obj_map);
        repr += ")";
        return repr;
    }
}
