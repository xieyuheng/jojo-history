#include "collect_dict_jo.hpp"

#include "../object/str.hpp"
#include "../object/dict.hpp"

collect_dict_jo_t::
collect_dict_jo_t (size_t counter)
{
    this->counter = counter;
}

jo_t *
collect_dict_jo_t::copy ()
{
    return new collect_dict_jo_t (this->counter);
}

void
collect_dict_jo_t::exe (env_t &env, local_scope_t &local_scope)
{
    auto index = 0;
    auto obj_map = obj_map_t ();
    while (index < this->counter) {
        auto obj = env.obj_stack.top ();
        env.obj_stack.pop ();
        auto str = env.obj_stack.top ();
        env.obj_stack.pop ();
        assert (str_p (env, str));
        auto key = static_pointer_cast <str_o> (str);
        obj_map [key->str] = obj;
        index++;
    }
    auto dict = make_shared <dict_o> (env, obj_map);
    env.obj_stack.push (dict);
}

string
collect_dict_jo_t::repr (env_t &env)
{
    return "(collect-dict " + to_string (this->counter) + ")";
}
