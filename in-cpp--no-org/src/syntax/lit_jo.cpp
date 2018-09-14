#include "lit_jo.hpp"

lit_jo_t::
lit_jo_t (shared_ptr <obj_t> obj)
{
    this->obj = obj;
}

jo_t *
lit_jo_t::copy ()
{
    return new lit_jo_t (this->obj);
}

void
lit_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    env.obj_stack.push (this->obj);
}

string
lit_jo_t::repr (env_t &env)
{
    return this->obj->repr (env);
}
