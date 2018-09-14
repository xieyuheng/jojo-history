#include "lambda_jo.hpp"

#include "../object/closure.hpp"

lambda_jo_t::
lambda_jo_t (name_vector_t name_vector,
             shared_ptr <jojo_t> jojo)
{
    this->name_vector = name_vector;
    this->jojo = jojo;
}

jo_t *
lambda_jo_t::copy ()
{
    return new lambda_jo_t (this->name_vector, this->jojo);
}

void
lambda_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto closure = make_shared <closure_o>
        (env,
         this->name_vector,
         this->jojo,
         bind_vector_from_name_vector (this->name_vector),
         local_scope);
    env.obj_stack.push (closure);
}

string
lambda_jo_t::repr (env_t &env)
{
    return "(lambda " +
        name_vector_repr (this->name_vector) +
        " " +
        jojo_repr (env, this->jojo) +
        ")";
}
