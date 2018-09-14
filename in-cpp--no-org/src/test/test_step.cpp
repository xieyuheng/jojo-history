#include "test_step.hpp"

#include "../object/str.hpp"

#include "../syntax/ref_jo.hpp"

void
test_step ()
{
    auto env = env_t ();

    define (env, "s1", make_shared <str_o> (env, "bye"));
    define (env, "s2", make_shared <str_o> (env, "world"));

    jo_vector_t jo_vector = {
        new ref_jo_t (boxing (env, "s1")),
        new ref_jo_t (boxing (env, "s2")),
    };

    env.frame_stack.push (new_frame_from_jo_vector (jo_vector));

    {
        env.run ();
        assert_stack_size (env, 2);
        assert_pop_eq (env, make_shared <str_o> (env, "world"));
        assert_pop_eq (env, make_shared <str_o> (env, "bye"));
        assert_stack_size (env, 0);
    }
}
