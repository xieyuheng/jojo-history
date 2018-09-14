#include "prim.hpp"

prim_o::prim_o (env_t &env,
                name_vector_t name_vector,
                prim_fn fn,
                obj_map_t obj_map)
{
    this->tag = "prim-t";
    this->name_vector = name_vector;
    this->fn = fn;
    this->obj_map = obj_map;
}

string
prim_o::repr (env_t &env)
{
    if (this->name_vector.size () == 0) {
        string repr = "(prim)";
        return repr;
    }
    else {
        string repr = "(prim ";
        repr += name_vector_and_obj_map_repr
            (env, this->name_vector, this->obj_map);
        repr += ")";
        return repr;
    }
}

bool prim_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <prim_o> (obj);
    if (this != obj.get ()) return false;
    return obj_map_equal (env, this->obj_map, that->obj_map);
}

void prim_o::apply (env_t &env, size_t arity)
{
    auto size = this->name_vector.size ();
    auto have = this->obj_map.size ();
    auto lack = size - have;
    if (lack == arity) {
        auto lack_name_vector = name_vector_obj_map_lack
            (this->name_vector, this->obj_map);
        auto obj_map = pick_up_obj_map_and_merge
            (env, lack_name_vector, this->obj_map);
        this->fn (env, obj_map);
    }
    else if (arity < lack) {
        auto lack_name_vector = name_vector_obj_map_arity_lack
            (this->name_vector, this->obj_map, arity);
        auto obj_map = pick_up_obj_map_and_merge
            (env, lack_name_vector, this->obj_map);
        auto prim = make_shared <prim_o>
            (env, this->name_vector, this->fn, obj_map);
        env.obj_stack.push (prim);
    }
    else {
        cout << "- fatal error : prim_o::apply" << "\n"
             << "  over-arity apply" << "\n"
             << "  arity > lack" << "\n"
             << "  arity : " << arity << "\n"
             << "  lack : " << lack << "\n";
        exit (1);
    }
}

void
define_prim (env_t &env, sig_t sig, prim_fn fn)
{
    auto name = name_of_sig (sig);
    auto name_vector = name_vector_of_sig (sig);
    define (env, name, make_shared <prim_o>
            (env, name_vector, fn, obj_map_t ()));
}
