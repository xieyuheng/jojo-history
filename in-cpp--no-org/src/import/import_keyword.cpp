#include "import_keyword.hpp"

#include "../object/keyword.hpp"
#include "../object/type.hpp"

void
import_keyword (env_t &env)
{
    define_type (env, "keyword-t");
}
