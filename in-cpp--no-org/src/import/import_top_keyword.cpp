#include "import_top_keyword.hpp"

#include "../object/top_keyword.hpp"
#include "../object/type.hpp"

void
import_top_keyword (env_t &env)
{
    define_type (env, "top-keyword-t");
}
