#pragma once

#include "libjojo.hpp"

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
