#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <functional>
#include <cassert>
#include <memory>
#include <vector>
#include <array>
#include <map>
#include <set>
#include <stack>

using namespace std;

struct env_t;
struct obj_t;
struct jo_t;
struct jojo_t;
struct box_t;
struct frame_t;

using name_t = string;
using name_vector_t = vector <name_t>;
using bind_t = pair <name_t, shared_ptr <obj_t>>;
using bind_vector_t = vector <bind_t>; // index from end
using local_scope_t = vector <bind_vector_t>; // index from end
using jo_vector_t = vector <jo_t *>;
using tag_t = string;
using obj_map_t = map <name_t, shared_ptr <obj_t>>;
using obj_vector_t = vector <shared_ptr <obj_t>>;
using box_map_t = map <name_t, box_t *>;
using obj_stack_t = stack <shared_ptr <obj_t>>;
using frame_stack_t = stack <shared_ptr <frame_t>>;
using jojo_map_t = map <tag_t, shared_ptr <jojo_t>>;
using string_vector_t = vector <string>;
using local_ref_t = pair <size_t, size_t>;
using local_ref_map_t = map <name_t, local_ref_t>;

// #include "env.hpp"

struct env_t
{
    box_map_t box_map;
    obj_stack_t obj_stack;
    frame_stack_t frame_stack;
    void step ();
    void run ();
    void box_map_report ();
    void frame_stack_report ();
    void obj_stack_report ();
    void report ();
    void run_with_base (size_t base);
    void double_report ();
    void step_and_report ();
};

struct jojo_t
{
    jo_vector_t jo_vector;
    jojo_t (jo_vector_t jo_vector);
    ~jojo_t ();
};

struct frame_t
{
    size_t index;
    shared_ptr <jojo_t> jojo;
    local_scope_t local_scope;
    frame_t (shared_ptr <jojo_t> jojo, local_scope_t local_scope);
};

struct box_t
{
    shared_ptr <obj_t> obj;
    bool empty_p;
    box_t ();
    box_t (shared_ptr <obj_t> obj);
};

shared_ptr <jojo_t>
jojo_append (shared_ptr <jojo_t> ante,
             shared_ptr <jojo_t> succ);

void
jojo_print (env_t &env, shared_ptr <jojo_t> jojo);

void
jojo_print_with_index (env_t &env,
                       shared_ptr <jojo_t> jojo,
                       size_t index);

void
frame_report (env_t &env, shared_ptr <frame_t> frame);

box_t *
boxing (env_t &env, name_t name);

name_t
name_of_box (env_t &env, box_t *box);

// #include "obj.hpp"

struct obj_t
{
    tag_t tag;
    obj_map_t obj_map;
    virtual ~obj_t ();
    virtual string repr (env_t &env);
    virtual bool equal (env_t &env, shared_ptr <obj_t> obj);
    virtual void apply (env_t &env, size_t arity);
};

using sig_t = name_vector_t;

void
define (env_t &env,
        name_t name,
        shared_ptr <obj_t> obj);

name_t
name_of_sig (sig_t &sig);

name_vector_t
name_vector_of_sig (sig_t &sig);

// #include "jo.hpp"

struct jo_t
{
    virtual jo_t * copy ();
    virtual ~jo_t ();
    virtual void exe (env_t &env, local_scope_t &local_scope);
    virtual string repr (env_t &env);
};


template <typename Out>
void
string_split (const string &s, char delim, Out result);

vector <string>
string_split (const string &s, char delim);

string
jojo_repr (env_t &env, shared_ptr <jojo_t> jojo);

string
name_vector_repr (name_vector_t &name_vector);

string
bind_vector_repr (env_t &env, bind_vector_t bind_vector);

string
local_scope_repr (env_t &env, local_scope_t local_scope);

size_t
number_of_obj_in_bind_vector (bind_vector_t &bind_vector);

void
bind_vector_insert_obj (bind_vector_t &bind_vector,
                        shared_ptr <obj_t> obj);

bind_vector_t
bind_vector_merge_obj_vector (bind_vector_t &old_bind_vector,
                              obj_vector_t &obj_vector);

obj_vector_t
pick_up_obj_vector (env_t &env, size_t counter);

local_scope_t
local_scope_extend (local_scope_t old_local_scope,
                    bind_vector_t bind_vector);

bool
bind_equal (env_t &env,
            bind_t &lhs,
            bind_t &rhs);

bool
bind_vector_equal (env_t &env,
                   bind_vector_t &lhs,
                   bind_vector_t &rhs);

bool
local_scope_equal (env_t &env,
                   local_scope_t &lhs,
                   local_scope_t &rhs);

bool
obj_map_equal (env_t &env, obj_map_t &lhs, obj_map_t &rhs);

string
obj_map_repr (env_t &env, obj_map_t &obj_map);

name_vector_t
name_vector_obj_map_lack (name_vector_t &old_name_vector,
                          obj_map_t &obj_map);

name_vector_t
name_vector_obj_map_arity_lack (name_vector_t &old_name_vector,
                                obj_map_t &obj_map,
                                size_t arity);

obj_map_t
pick_up_obj_map_and_merge (env_t &env,
                           name_vector_t &lack_name_vector,
                           obj_map_t &old_obj_map);

string
name_vector_and_obj_map_repr (env_t &env,
                              name_vector_t &name_vector,
                              obj_map_t &obj_map);

bind_vector_t
bind_vector_from_name_vector (name_vector_t &name_vector);

shared_ptr <frame_t>
new_frame_from_jojo (shared_ptr <jojo_t> jojo);

shared_ptr <frame_t>
new_frame_from_jo_vector (jo_vector_t jo_vector);

bool
obj_equal (env_t &env,
           shared_ptr <obj_t> &lhs,
           shared_ptr <obj_t> &rhs);

local_ref_map_t
local_ref_map_extend (env_t &env,
                      local_ref_map_t &old_local_ref_map,
                      name_vector_t &name_vector);

void
assert_pop_eq (env_t &env, shared_ptr <obj_t> obj);

void
assert_tos_eq (env_t &env, shared_ptr <obj_t> obj);

void
assert_stack_size (env_t &env, size_t size);
