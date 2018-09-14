#pragma once

#include "libjojo.hpp"

#include "object/str.hpp"
#include "object/list.hpp"
#include "object/top_keyword.hpp"

bool
top_keyword_sexp_p (env_t &env, shared_ptr <obj_t> sexp);

top_keyword_fn
get_top_keyword_fn (env_t &env, name_t name);

void
jojo_run (env_t &env, shared_ptr <jojo_t> jojo);

void
sexp_eval (env_t &env, shared_ptr <obj_t> sexp);

void
sexp_list_eval (env_t &env, shared_ptr <obj_t> sexp_list);

void
top_sexp_eval (env_t &env, shared_ptr <obj_t> sexp);

void
top_sexp_list_eval (env_t &env, shared_ptr <obj_t> sexp_list);

void
code_eval (env_t &env, shared_ptr <str_o> code);
