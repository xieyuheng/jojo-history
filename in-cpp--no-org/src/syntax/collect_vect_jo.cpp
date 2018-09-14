#include "collect_vect_jo.hpp"

#include "../object/vect.hpp"

collect_vect_jo_t::
collect_vect_jo_t (size_t counter)
{
    this->counter = counter;
}

jo_t *
collect_vect_jo_t::copy ()
{
    return new collect_vect_jo_t (this->counter);
}

void
collect_vect_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto index = 0;
    auto obj_vector = obj_vector_t ();
    while (index < this->counter) {
        auto obj = env.obj_stack.top ();
        env.obj_stack.pop ();
        obj_vector.push_back (obj);
        index++;
    }
    reverse (obj_vector.begin (),
             obj_vector.end ());
    auto vect = make_shared <vect_o> (env, obj_vector);
    env.obj_stack.push (vect);
}

string
collect_vect_jo_t::repr (env_t &env)
{
    return "(collect-vect " + to_string (this->counter) + ")";
}
