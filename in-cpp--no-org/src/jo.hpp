#pragma once

#include "libjojo.hpp"

struct jo_t
{
    virtual jo_t * copy ();
    virtual ~jo_t ();
    virtual void exe (env_t &env, local_scope_t &local_scope);
    virtual string repr (env_t &env);
};
