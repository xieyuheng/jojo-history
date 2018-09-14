#include "case_jo.hpp"

case_jo_t::
case_jo_t (jojo_map_t jojo_map)
{
    this->jojo_map = jojo_map;
    this->default_jojo = nullptr;
}

case_jo_t::
case_jo_t (jojo_map_t jojo_map,
           shared_ptr <jojo_t> default_jojo)
{
    this->jojo_map = jojo_map;
    this->default_jojo = default_jojo;
}

bool
case_jo_t::has_default_jojo_p ()
{
    return this->default_jojo != nullptr;
}

jo_t *
case_jo_t::copy ()
{
    return new case_jo_t
        (this->jojo_map,
         this->default_jojo);
}

void
case_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto obj = env.obj_stack.top ();
    env.obj_stack.pop ();
    auto it = this->jojo_map.find (obj->tag);
    if (it != this->jojo_map.end ()) {
        auto jojo = it->second;
        auto frame = make_shared <frame_t> (jojo, local_scope);
        env.frame_stack.push (frame);
    }
    else if (this->has_default_jojo_p ()) {
        auto jojo = this->default_jojo;
        auto frame = make_shared <frame_t> (jojo, local_scope);
        env.frame_stack.push (frame);
    }
    else {
        cout << "- fatal error : case_jo_t::exe mismatch" << "\n";
        cout << "  tag : " << obj->tag << "\n";
        exit (1);
    }

}

string
case_jo_t::repr (env_t &env)
{
    return "(case)";
}
