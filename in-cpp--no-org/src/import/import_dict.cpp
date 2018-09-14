#include "import_dict.hpp"

#include "../object/type.hpp"
#include "../object/dict.hpp"

void
import_dict (env_t &env)
{
    define_type (env, "dict-t");
}
