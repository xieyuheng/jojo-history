#include "closure.hpp"

void
closure_o::apply (env_t &env, size_t arity)
{
    auto size = this->name_vector.size ();
    auto have = number_of_obj_in_bind_vector (this->bind_vector);
    auto lack = size - have;
    if (lack == arity) {
        auto obj_vector = pick_up_obj_vector
            (env, arity);
        auto bind_vector = bind_vector_merge_obj_vector
            (this->bind_vector, obj_vector);
        auto local_scope = local_scope_extend
            (this->local_scope, bind_vector);
        auto frame = make_shared <frame_t>
            (this->jojo, local_scope);
        env.frame_stack.push (frame);
    }
    else if (arity < lack) {
        auto obj_vector = pick_up_obj_vector
            (env, arity);
        auto bind_vector = bind_vector_merge_obj_vector
            (this->bind_vector, obj_vector);
        auto closure = make_shared <closure_o>
            (env,
             this->name_vector,
             this->jojo,
             bind_vector,
             this->local_scope);
        env.obj_stack.push (closure);
    }
    else {
        cout << "- fatal error : closure_o::apply" << "\n"
             << "  over-arity apply" << "\n"
             << "  arity > lack" << "\n"
             << "  arity : " << arity << "\n"
             << "  lack : " << lack << "\n";
        exit (1);
    }
}

closure_o::
closure_o (env_t &env,
           name_vector_t name_vector,
           shared_ptr <jojo_t> jojo,
           bind_vector_t bind_vector,
           local_scope_t local_scope)
{
    this->tag = "closure-t";
    this->name_vector = name_vector;
    this->jojo = jojo;
    this->bind_vector = bind_vector;
    this->local_scope = local_scope;
}

bool
closure_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    // raw pointers must be equal first
    if (this != obj.get ()) return false;
    auto that = static_pointer_cast <closure_o> (obj);
    // then scopes
    if (local_scope_equal
        (env,
         this->local_scope,
         that->local_scope)) return false;
    // then bindings
    if (bind_vector_equal
        (env,
         this->bind_vector,
         that->bind_vector)) return false;
    else return true;
}

string
closure_o::repr (env_t &env)
{
    string repr = "(closure ";
    repr += name_vector_repr (this->name_vector);
    repr += " ";
    repr += jojo_repr (env, this->jojo);
    repr += "\n";
    auto local_scope = this->local_scope;
    local_scope.push_back (this->bind_vector);
    repr += local_scope_repr (env, local_scope);
    if (! repr.empty ()) repr.pop_back ();
    if (! repr.empty ()) repr.pop_back ();
    repr += ")";
    return repr;
}
