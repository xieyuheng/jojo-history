#include "keyword.hpp"

keyword_o::
keyword_o (env_t &env, keyword_fn fn)
{
    this->tag = "keyword-t";
    this->fn = fn;
}

bool
keyword_o::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag) return false;
    return this != obj.get ();
}

bool
keyword_p (env_t &env, shared_ptr <obj_t> a)
{
    return a->tag == "keyword-t";
}

void
define_keyword (env_t &env, name_t name, keyword_fn fn)
{
    define (env, name, make_shared <keyword_o> (env, fn));
}
