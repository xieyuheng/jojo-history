#include "assert_jo.hpp"

#include "../object/bool.hpp"

#include "../sexp.hpp"

assert_jo_t::
assert_jo_t (shared_ptr <obj_t> body,
             shared_ptr <jojo_t> jojo)
{
    this->body = body;
    this->jojo = jojo;
}

jo_t *
assert_jo_t::copy ()
{
    return new assert_jo_t
        (this->body,
         this->jojo);
}

void
assert_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto base = env.frame_stack.size ();
    auto jojo = this->jojo;
    auto frame = make_shared <frame_t> (jojo, local_scope);
    env.frame_stack.push (frame);
    env.run_with_base (base);
    auto result = env.obj_stack.top ();
    if (true_p (env, result)) {
        return;
    }
    else {
        env.frame_stack_report ();
        env.obj_stack_report ();
        cout << "- assert fail : " << "\n";
        cout << "  " << sexp_list_repr (env, this->body) << "\n";
        exit (1);
    }
}

string
assert_jo_t::repr (env_t &env)
{
    return "(assert)";
}
