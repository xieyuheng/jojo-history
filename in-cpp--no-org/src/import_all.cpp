#include "import_all.hpp"

#include "import/import_bool.hpp"
#include "import/import_bool.hpp"
#include "import/import_int.hpp"
#include "import/import_str.hpp"
#include "import/import_list.hpp"
#include "import/import_vect.hpp"
#include "import/import_dict.hpp"
#include "import/import_sexp.hpp"
#include "import/import_top_keyword.hpp"
#include "import/import_keyword.hpp"
#include "import/import_syntax.hpp"
#include "import/import_type.hpp"
#include "import/import_stack.hpp"
#include "import/import_misc.hpp"

void
import_all (env_t &env)
{
    import_bool (env);
    import_int (env);
    import_str (env);
    import_list (env);
    import_vect (env);
    import_dict (env);
    import_sexp (env);
    import_top_keyword (env);
    import_keyword (env);
    import_syntax (env);
    import_type (env);
    import_stack (env);
    import_misc (env);
}
