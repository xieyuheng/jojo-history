#include "test_data.hpp"

#include "../object/str.hpp"
#include "../object/data.hpp"

#include "../syntax/ref_jo.hpp"
#include "../syntax/field_jo.hpp"

void
test_data ()
{
    auto env = env_t ();

    obj_map_t obj_map = {
        {"car", make_shared <str_o> (env, "bye")},
        {"cdr", make_shared <str_o> (env, "world")},
    };

    define (env, "last-cry", make_shared <data_o>
            (env, "cons-t", obj_map));

    jo_vector_t jo_vector = {
        new ref_jo_t (boxing (env, "last-cry")),
        new field_jo_t ("car"),
        new ref_jo_t (boxing (env, "last-cry")),
        new field_jo_t ("cdr"),
        new ref_jo_t (boxing (env, "last-cry")),
    };

    env.frame_stack.push (new_frame_from_jo_vector (jo_vector));

    {
        env.run ();

        assert_stack_size (env, 3);
        assert_pop_eq (env, make_shared <data_o>
                       (env,
                        "cons-t",
                        obj_map));
        assert_pop_eq (env, make_shared <str_o> (env, "world"));
        assert_pop_eq (env, make_shared <str_o> (env, "bye"));
        assert_stack_size (env, 0);
    }
}
