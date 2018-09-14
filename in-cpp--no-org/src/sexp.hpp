#pragma once

#include "libjojo.hpp"

#include "object/str.hpp"
#include "object/list.hpp"
#include "object/vect.hpp"
#include "object/dict.hpp"

// drop `,`
shared_ptr <obj_t>
word_vector_to_word_list
(env_t &env, string_vector_t &word_vector);

shared_ptr <obj_t>
scan_word_list (env_t &env, shared_ptr <str_o> code);

bool
bar_word_p (string word);

bool
ket_word_p (string word);

bool
quote_word_p (string word);

string
bar_word_to_ket_word (string bar);

shared_ptr <obj_t>
word_list_head_with_bar_ket_counter
(env_t &env,
 shared_ptr <obj_t> word_list,
 string bar,
 string ket,
 size_t counter);

shared_ptr <obj_t>
word_list_head (env_t &env, shared_ptr <obj_t> word_list);

shared_ptr <obj_t>
word_list_rest_with_bar_ket_counter
(env_t &env,
 shared_ptr <obj_t> word_list,
 string bar,
 string ket,
 size_t counter);

shared_ptr <obj_t>
word_list_rest (env_t &env, shared_ptr <obj_t> word_list);

shared_ptr <obj_t>
word_list_drop_ket
(env_t &env,
 shared_ptr <obj_t> word_list,
 string ket);

shared_ptr <obj_t>
parse_sexp (env_t &env, shared_ptr <obj_t> word_list);

shared_ptr <obj_t>
parse_sexp_list (env_t &env, shared_ptr <obj_t> word_list);

string
sexp_repr (env_t &env, shared_ptr <obj_t> a);

string
sexp_list_repr (env_t &env, shared_ptr <obj_t> sexp_list);
