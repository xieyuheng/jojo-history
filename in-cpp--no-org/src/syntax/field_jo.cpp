#include "field_jo.hpp"

field_jo_t::field_jo_t (name_t name)
{
    this->name = name;
}

jo_t *
field_jo_t::copy ()
{
    return new field_jo_t (this->name);
}

void
field_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto obj = env.obj_stack.top ();
    env.obj_stack.pop ();
    auto it = obj->obj_map.find (this->name);
    if (it != obj->obj_map.end ()) {
        env.obj_stack.push (it->second);
        return;
    }
    else {
        auto it_box = env.box_map.find (obj->tag);
        assert (it_box != env.box_map.end ());
        auto box = it_box->second;
        auto it = box->obj->obj_map.find (this->name);
        if (it != box->obj->obj_map.end ()) {
            if (it->second->tag == "closure-t") {
                env.obj_stack.push (obj);
            }
            env.obj_stack.push (it->second);
            return;
        }
        else {
            cout << "- fatal error : field_jo_t::exe" << "\n"
                 << "  unknown field : " << this->name << "\n"
                 << "  fail to find it in both object and type" << "\n";
            exit (1);
        }
    }
}

string
field_jo_t::repr (env_t &env)
{
    return "." + this->name;
}
