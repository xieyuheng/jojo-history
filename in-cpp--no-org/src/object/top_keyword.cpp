#include "top_keyword.hpp"

top_keyword_o::
top_keyword_o (env_t &env, top_keyword_fn fn)
{
    this->tag = "top-keyword-t";
    this->fn = fn;
}

bool
top_keyword_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    return this != obj.get ();
}

bool
top_keyword_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "top-keyword-t";
}

void
define_top_keyword (env_t &env, name_t name, top_keyword_fn fn)
{
    define (env, name, make_shared <top_keyword_o> (env, fn));
}
