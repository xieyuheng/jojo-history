#include "libjojo.hpp"

#include "object/str.hpp"

#include "eval.hpp"

#include "test_all.hpp"
#include "import_all.hpp"

void
eval_file (env_t &env, string file_name)
{
    auto input_file = ifstream (file_name);
    auto buffer = stringstream ();
    buffer << input_file.rdbuf ();
    auto code = make_shared <str_o> (env, buffer.str ());
    code_eval (env, code);
}

void
the_story_begin (string_vector_t arg_vector)
{
    auto env = env_t ();
    import_all (env);
    for (auto file_name: arg_vector)
        eval_file (env, file_name);
}

int
main (int argc, char **argv)
{
    test_all ();
    auto arg_vector = string_vector_t ();
    for (auto i = 1; i < argc; i++) {
        arg_vector.push_back (string (argv[i]));
    }
    the_story_begin (arg_vector);
    return 0;
}
