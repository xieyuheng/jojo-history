#include "vect.hpp"

vect_o::vect_o (env_t &env, obj_vector_t obj_vector)
{
    this->tag = "vect-t";
    this->obj_vector = obj_vector;
}

bool
vect_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    auto that = static_pointer_cast <vect_o> (obj);
    return vect_equal (env, this->obj_vector, that->obj_vector);
}

string
vect_o::repr (env_t &env)
{
    string repr = "[";
    for (auto &obj: this->obj_vector) {
        repr += obj->repr (env);
        repr += " ";
    }
    if (! repr.empty ()) repr.pop_back ();
    repr += "]";
    return repr;
}

bool
vect_equal (env_t &env,
            obj_vector_t &lhs,
            obj_vector_t &rhs)
{
    if (lhs.size () != rhs.size ()) return false;
    auto size = lhs.size ();
    auto index = 0;
    while (index < size) {
        if (! obj_equal (env, lhs [index], rhs [index]))
            return false;
        index++;
    }
    return true;
}

bool
vect_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "vect-t";
}

shared_ptr <vect_o>
list_to_vect (env_t &env, shared_ptr <obj_t> l)
{
    auto obj_vector = obj_vector_t ();
    while (cons_p (env, l)) {
        obj_vector.push_back (car (env, l));
        l = cdr (env, l);
    }
    return make_shared <vect_o> (env, obj_vector);
}

shared_ptr <obj_t>
vect_to_list (env_t &env, shared_ptr <vect_o> vect)
{
    auto obj_vector = vect->obj_vector;
    auto result = null_c (env);
    auto begin = obj_vector.rbegin ();
    auto end = obj_vector.rend ();
    for (auto it = begin; it != end; it++)
        result = cons_c (env, *it, result);
    return result;
}

void
test_vect ()
{
}
