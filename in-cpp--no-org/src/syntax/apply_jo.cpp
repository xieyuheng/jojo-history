#include "apply_jo.hpp"

apply_jo_t::
apply_jo_t (size_t arity)
{
    this->arity = arity;
}

jo_t *
apply_jo_t::copy ()
{
    return new apply_jo_t (this->arity);
}

void
apply_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto obj = env.obj_stack.top ();
    env.obj_stack.pop ();
    obj->apply (env, this->arity);
}

string
apply_jo_t::repr (env_t &env)
{
    return "(apply " +
        to_string (this->arity) + ")";
}
