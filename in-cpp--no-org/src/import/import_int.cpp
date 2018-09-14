#include "import_int.hpp"

#include "../object/type.hpp"

void
import_int (env_t &env)
{
    define_type (env, "int-t");
}
