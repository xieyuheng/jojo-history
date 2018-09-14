#include "env.hpp"

jojo_t::
jojo_t (jo_vector_t jo_vector)
{
    this->jo_vector = jo_vector;
}

jojo_t::
~jojo_t ()
{
    for (jo_t *jo_ptr: this->jo_vector)
        delete jo_ptr;
}

shared_ptr <jojo_t>
jojo_append (shared_ptr <jojo_t> ante,
             shared_ptr <jojo_t> succ)
{
    auto jo_vector = jo_vector_t ();
    for (auto x: ante->jo_vector) jo_vector.push_back (x->copy ());
    for (auto x: succ->jo_vector) jo_vector.push_back (x->copy ());
    return make_shared <jojo_t> (jo_vector);
}

frame_t::frame_t (shared_ptr <jojo_t> jojo,
                  local_scope_t local_scope)
{
    this->index = 0;
    this->jojo = jojo;
    this->local_scope = local_scope;
}

void
jojo_print (env_t &env, shared_ptr <jojo_t> jojo)
{
    for (auto &jo: jojo->jo_vector) {
        cout << jo->repr (env)
             << " ";
    }
}

void
jojo_print_with_index (env_t &env,
                       shared_ptr <jojo_t> jojo,
                       size_t index)
{
    for (auto it = jojo->jo_vector.begin ();
         it != jojo->jo_vector.end ();
         it++) {
        size_t it_index = it - jojo->jo_vector.begin ();
        jo_t *jo = *it;
        if (index == it_index) {
            cout << "->> " << jo->repr (env) << " ";
        }
        else {
            cout << jo->repr (env) << " ";
        }
    }
}

void
frame_report (env_t &env, shared_ptr <frame_t> frame)
{
    cout << "  - [" << frame->index+1
         << "/" << frame->jojo->jo_vector.size ()
         << "] ";
    jojo_print_with_index (env, frame->jojo, frame->index);
    cout << "\n";
    cout << local_scope_repr (env, frame->local_scope);
}

box_t::box_t ()
{
    this->empty_p = true;
}

box_t::box_t (shared_ptr <obj_t> obj)
{
    this->empty_p = false;
    this->obj = obj;
}

box_t *
boxing (env_t &env, name_t name)
{
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        auto box = it->second;
        return box;
    }
    else {
        auto box = new box_t ();
        env.box_map [name] = box;
        return box;
    }
}

name_t
name_of_box (env_t &env, box_t *box)
{
    for (auto &kv: env.box_map) {
        auto name = kv.first;
        if (kv.second == box) {
            return name;
        }
    }
    return "#non-name";
}

void
env_t::step ()
{
    auto frame = this->frame_stack.top ();
    size_t size = frame->jojo->jo_vector.size ();
    // it is assumed that jojo in frame are not empty
    assert (size != 0);
    size_t index = frame->index;
    frame->index++;
    // handle proper tail call
    if (index+1 == size) this->frame_stack.pop ();
    // since the last frame might be drop,
    //   we pass last local_scope as an extra argument.
    frame->jojo->jo_vector[index]->exe (*this, frame->local_scope);
}

void
env_t::run ()
{
    while (!this->frame_stack.empty ()) {
        this->step ();
    }
}

void
env_t::box_map_report ()
{
    auto &env = *this;
    cout << "- [" << env.box_map.size () << "] "
         << "box_map - " << "\n";
    for (auto &kv: env.box_map) {
        cout << "  " << kv.first << " = ";
        auto box = kv.second;
        if (box->empty_p)
            cout << "_";
        else
            cout << box->obj->repr (env);
        cout << "\n";
    }
}

void
env_t::frame_stack_report ()
{
    auto &env = *this;
    cout << "- [" << env.frame_stack.size () << "] "
         << "frame_stack - " << "\n";
    frame_stack_t frame_stack = env.frame_stack;
    while (! frame_stack.empty ()) {
       auto frame = frame_stack.top ();
       frame_report (env, frame);
       frame_stack.pop ();
    }
}

void
env_t::obj_stack_report ()
{
    auto &env = *this;
    cout << "- [" << env.obj_stack.size () << "] "
         << "obj_stack - " << "\n";
    auto obj_stack = env.obj_stack;
    while (! obj_stack.empty ()) {
        auto obj = obj_stack.top ();
        cout << "  ";
        cout << obj->repr (env);
        cout << "\n";
        obj_stack.pop ();
    }
}

void
env_t::report ()
{
    this->box_map_report ();
    this->frame_stack_report ();
    this->obj_stack_report ();
}

void
env_t::run_with_base (size_t base)
{
    while (this->frame_stack.size () > base) {
        this->step ();
    }
}

void
env_t::double_report ()
{
    this->report ();
    this->run ();
    this->report ();
}

void
env_t::step_and_report ()
{
    this->step ();
    this->report ();
}
