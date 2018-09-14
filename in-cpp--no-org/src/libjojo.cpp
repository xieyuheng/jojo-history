#include "libjojo.hpp"

template <typename Out>
void
string_split (const string &s, char delim, Out result)
{
    stringstream ss (s);
    string item;
    while (getline (ss, item, delim)) {
        *(result++) = item;
    }
}

vector <string>
string_split (const string &s, char delim)
{
    vector <string> elems;
    string_split (s, delim, back_inserter (elems));
    return elems;
}

string
jojo_repr (env_t &env, shared_ptr <jojo_t> jojo)
{
    assert (jojo->jo_vector.size () != 0);
    string repr = "";
    for (auto &jo: jojo->jo_vector) {
        repr += jo->repr (env);
        repr += " ";
    }
    repr.pop_back ();
    return repr;
}

string
name_vector_repr (name_vector_t &name_vector)
{
    if (name_vector.size () == 0) {
        string repr = "[";
        repr += "]";
        return repr;
    }
    else {
        string repr = "[";
        for (auto name: name_vector) {
            repr += name;
            repr += " ";
        }
        if (! repr.empty ()) repr.pop_back ();
        repr += "]";
        return repr;
    }
}

string
bind_vector_repr (env_t &env, bind_vector_t bind_vector)
{
    string repr = "";
    for (auto it = bind_vector.rbegin ();
         it != bind_vector.rend ();
         it++) {
        repr += "(";
        repr += to_string (distance (bind_vector.rbegin (), it));
        repr += " ";
        repr += it->first;
        repr += " = ";
        auto obj = it->second;
        if (obj == nullptr)
            repr += "_";
        else
            repr += obj->repr (env);
        repr += ") ";
    }
    return repr;
}

string
local_scope_repr (env_t &env, local_scope_t local_scope)
{
    string repr = "";
    repr += "  - [";
    repr += to_string (local_scope.size ());
    repr += "] ";
    repr += "local_scope - ";
    repr += "\n";
    for (auto it = local_scope.rbegin ();
         it != local_scope.rend ();
         it++) {
        repr += "    ";
        repr += to_string (distance (local_scope.rbegin (), it));
        repr += " ";
        repr += bind_vector_repr (env, *it);
        repr += "\n";
    }
    return repr;
}

size_t
number_of_obj_in_bind_vector (bind_vector_t &bind_vector)
{
    size_t sum = 0;
    auto begin = bind_vector.begin ();
    auto end = bind_vector.end ();
    for (auto it = begin; it != end; it++)
        if (it->second)
            sum++;
    return sum;
}

void
bind_vector_insert_obj (bind_vector_t &bind_vector,
                        shared_ptr <obj_t> obj)
{
    auto begin = bind_vector.rbegin ();
    auto end = bind_vector.rend ();
    for (auto it = begin; it != end; it++) {
        if (it->second == nullptr) {
            it->second = obj;
            return;
        }
    }
    cout << "- fatal error : bind_vector_insert_obj" << "\n"
         << "  the bind_vector is filled" << "\n";
    exit (1);
}

bind_vector_t
bind_vector_merge_obj_vector (bind_vector_t &old_bind_vector,
                              obj_vector_t &obj_vector)
{
    auto bind_vector = old_bind_vector;
    for (auto obj: obj_vector)
        bind_vector_insert_obj (bind_vector, obj);
    return bind_vector;
}

obj_vector_t
pick_up_obj_vector (env_t &env, size_t counter)
{
    auto obj_vector = obj_vector_t ();
    while (counter > 0) {
        counter--;
        auto obj = env.obj_stack.top ();
        obj_vector.push_back (obj);
        env.obj_stack.pop ();
    }
    reverse (obj_vector.begin (),
             obj_vector.end ());
    return obj_vector;
}

local_scope_t
local_scope_extend (local_scope_t old_local_scope,
                    bind_vector_t bind_vector)
{
    auto local_scope = old_local_scope;
    local_scope.push_back (bind_vector);
    return local_scope;
}

bool
bind_equal (env_t &env,
            bind_t &lhs,
            bind_t &rhs)
{
    if (lhs.first != rhs.first) return false;
    return lhs.second->equal (env, rhs.second);
}

bool
bind_vector_equal (env_t &env,
                   bind_vector_t &lhs,
                   bind_vector_t &rhs)
{
    if (lhs.size () != rhs.size ()) return false;
    auto size = lhs.size ();
    auto index = 0;
    while (index < size) {
        if (! bind_equal (env, lhs [index], rhs [index]))
            return false;
        index++;
    }
    return true;
}

bool
local_scope_equal (env_t &env,
                   local_scope_t &lhs,
                   local_scope_t &rhs)
{
    if (lhs.size () != rhs.size ()) return false;
    auto size = lhs.size ();
    auto index = 0;
    while (index < size) {
        if (! bind_vector_equal (env, lhs [index], rhs [index]))
            return false;
        index++;
    }
    return true;
}

bool
obj_map_equal (env_t &env, obj_map_t &lhs, obj_map_t &rhs)
{
    if (lhs.size () != rhs.size ()) return false;
    for (auto &kv: lhs) {
        auto name = kv.first;
        auto it = rhs.find (name);
        if (it == rhs.end ()) return false;
        if (! kv.second->equal (env, it->second)) return false;
    }
    return true;
}

string
obj_map_repr (env_t &env, obj_map_t &obj_map)
{
    string repr = "";
    for (auto &kv: obj_map) {
        auto name = kv.first;
        repr += name;
        repr += " = ";
        auto obj = kv.second;
        repr += obj->repr (env);
        repr += " ";
    }
    if (! repr.empty ()) repr.pop_back ();
    return repr;
}

name_vector_t
name_vector_obj_map_lack (name_vector_t &old_name_vector,
                          obj_map_t &obj_map)
{
    auto name_vector = name_vector_t ();
    for (auto name: old_name_vector) {
        auto it = obj_map.find (name);
        // not found == lack
        if (it == obj_map.end ())
            name_vector.push_back (name);
    }
    return name_vector;
}

name_vector_t
name_vector_obj_map_arity_lack (name_vector_t &old_name_vector,
                                obj_map_t &obj_map,
                                size_t arity)
{
    auto name_vector = name_vector_obj_map_lack
        (old_name_vector, obj_map);
    auto lack = name_vector.size ();
    auto counter = lack - arity;
    while (counter > 0) {
        counter--;
        name_vector.pop_back ();
    }
    return name_vector;
}

obj_map_t
pick_up_obj_map_and_merge (env_t &env,
                           name_vector_t &lack_name_vector,
                           obj_map_t &old_obj_map)
{
    auto obj_map = old_obj_map;
    auto begin = lack_name_vector.rbegin ();
    auto end = lack_name_vector.rend ();
    for (auto it = begin; it != end; it++) {
        name_t name = *it;
        auto obj = env.obj_stack.top ();
        env.obj_stack.pop ();
        obj_map [name] = obj;
    }
    return obj_map;
}

string
name_vector_and_obj_map_repr (env_t &env,
                              name_vector_t &name_vector,
                              obj_map_t &obj_map)
{
    string repr = "";
    for (auto &name: name_vector) {
        auto it = obj_map.find (name);
        if (it == obj_map.end ()) {
            repr += name;
            repr += " = _ ";
        }
    }
    for (auto &kv: obj_map) {
        auto name = kv.first;
        repr += name;
        repr += " = ";
        auto obj = kv.second;
        repr += obj->repr (env);
        repr += " ";
    }
    if (! repr.empty ()) repr.pop_back ();
    return repr;
}

bind_vector_t
bind_vector_from_name_vector (name_vector_t &name_vector)
{
    auto bind_vector = bind_vector_t ();
    auto begin = name_vector.begin ();
    auto end = name_vector.end ();
    for (auto it = begin; it != end; it++)
        bind_vector.push_back (make_pair (*it, nullptr));
    return bind_vector;
}

shared_ptr <frame_t>
new_frame_from_jojo (shared_ptr <jojo_t> jojo)
{
    return make_shared <frame_t>
        (jojo, local_scope_t ());
}

shared_ptr <frame_t>
new_frame_from_jo_vector (jo_vector_t jo_vector)
{
    auto jojo = make_shared <jojo_t> (jo_vector);
    return make_shared <frame_t>
        (jojo, local_scope_t ());
}

bool
obj_equal (env_t &env,
           shared_ptr <obj_t> &lhs,
           shared_ptr <obj_t> &rhs)
{
    return lhs->equal (env, rhs);
}

local_ref_map_t
local_ref_map_extend (env_t &env,
                      local_ref_map_t &old_local_ref_map,
                      name_vector_t &name_vector)
{
    auto local_ref_map = local_ref_map_t ();
    for (auto &kv: old_local_ref_map) {
        auto name = kv.first;
        auto old_local_ref = kv.second;
        auto local_ref = local_ref_t ();
        local_ref.first = old_local_ref.first + 1;
        local_ref.second = old_local_ref.second;
        local_ref_map.insert (make_pair (name, local_ref));
    }
    auto index = 0;
    auto size = name_vector.size ();
    while (index < size) {
        auto name = name_vector [index];
        auto local_ref = local_ref_t ();
        local_ref.first = 0;
        local_ref.second = index;
        local_ref_map.insert (make_pair (name, local_ref));
        index++;
    }
    return local_ref_map;
}

void
assert_pop_eq (env_t &env, shared_ptr <obj_t> obj)
{
    auto that = env.obj_stack.top ();
    assert (obj->equal (env, that));
    env.obj_stack.pop ();
}

void
assert_tos_eq (env_t &env, shared_ptr <obj_t> obj)
{
    auto that = env.obj_stack.top ();
    assert (obj->equal (env, that));
}

void
assert_stack_size (env_t &env, size_t size)
{
    assert (env.obj_stack.size () == size);
}

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

obj_t::~obj_t ()
{
    // all classes that will be derived from
    // should have a virtual or protected destructor,
    // otherwise deleting an instance via a pointer
    // to a base class results in undefined behavior.
}

string
obj_t::repr (env_t &env)
{
    return "#<" + this->tag + ">";
}

bool
obj_t::equal (env_t &env, shared_ptr <obj_t> obj)
{
    if (this->tag != obj->tag)
        return false;
    else {
        cout << "- fatal error : obj_t::equal" << "\n"
             << "  equal is not implemented for  : "
             << obj->tag << "\n";
        exit (1);
    }
}

void
obj_t::apply (env_t &env, size_t arity)
{
    cout << "- fatal error : applying non applicable object" << "\n";
    exit (1);
}

void
define (env_t &env,
        name_t name,
        shared_ptr <obj_t> obj)
{
    auto it = env.box_map.find (name);
    if (it != env.box_map.end ()) {
        auto box = it->second;
        box->empty_p = false;
        box->obj = obj;
    }
    else {
        env.box_map [name] = new box_t (obj);
    }
}

name_t
name_of_sig (sig_t &sig)
{
    return sig [0];
}

name_vector_t
name_vector_of_sig (sig_t &sig)
{
    auto name_vector = name_vector_t ();
    auto begin = sig.begin () + 1;
    auto end = sig.end ();
    for (auto it = begin; it != end; it++) {
        name_vector.push_back (*it);
    }
    return name_vector;
}


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
