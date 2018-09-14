#include "obj.hpp"

obj_t::~obj_t ()
{
    // all classes that will be derived from
    // should have a virtual or protected destructor,
    // otherwise deleting an instance via a pointer
    // to a base class results in undefined behavior.
}

string
obj_t::repr (env_t &env)
{
    return "#<" + this->tag + ">";
}

bool
obj_t::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag)
        return false;
    else {
        cout << "- fatal error : obj_t::equal" << "\n"
             << "  equal is not implemented for  : "
             << obj->tag << "\n";
        exit (1);
    }
}

void
obj_t::apply (env_t &env, size_t arity)
{
    cout << "- fatal error : applying non applicable object" << "\n";
    exit (1);
}

void
define (env_t &env,
        name_t name,
        shared_ptr <obj_t> obj)
{
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        auto box = it->second;
        box->empty_p = false;
        box->obj = obj;
    }
    else {
        env.box_map [name] = new box_t (obj);
    }
}

name_t
name_of_sig (sig_t &sig)
{
    return sig [0];
}

name_vector_t
name_vector_of_sig (sig_t &sig)
{
    auto name_vector = name_vector_t ();
    auto begin = sig.begin () + 1;
    auto end = sig.end ();
    for (auto it = begin; it != end; it++) {
        name_vector.push_back (*it);
    }
    return name_vector;
}
