#include "jo.hpp"

jo_t *
jo_t::copy ()
{
    cout << "- fatal error : jo_t::copy unknown jo" << "\n";
    exit (1);
}

jo_t::~jo_t ()
{
    // all classes that will be derived from
    // should have a virtual or protected destructor,
    // otherwise deleting an instance via a pointer
    // to a base class results in undefined behavior.
}

void
jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    cout << "- fatal error : unknown jo" << "\n";
    exit (1);
}

string
jo_t::repr (env_t &env)
{
    return "#<unknown-jo>";
}
