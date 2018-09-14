#include "ref_jo.hpp"

ref_jo_t::ref_jo_t (box_t *box)
{
    this->box = box;
}

jo_t *
ref_jo_t::copy ()
{
    return new ref_jo_t (this->box);
}

void
ref_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    if (this->box->empty_p) {
        cout << "- fatal error : ref_jo_t::exe fail" << "\n";
        cout << "  undefined name : "
             << name_of_box (env, box) << "\n";
        exit (1);
    }
    else {
        env.obj_stack.push (this->box->obj);
    }
}

string
ref_jo_t::repr (env_t &env)
{
    return name_of_box (env, this->box);
}
