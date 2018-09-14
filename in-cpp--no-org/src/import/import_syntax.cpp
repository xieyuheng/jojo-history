#include "import_syntax.hpp"

#include "../object/top_keyword.hpp"
#include "../object/keyword.hpp"

#include "../syntax/assign.hpp"
#include "../syntax/lambda.hpp"
#include "../syntax/case.hpp"
#include "../syntax/quote.hpp"
#include "../syntax/note.hpp"
#include "../syntax/assert.hpp"

void
import_syntax (env_t &env)
{
    define_top_keyword (env, "=", tk_assign);
    define_keyword (env, "lambda", k_lambda);
    define_keyword (env, "case", k_case);
    define_keyword (env, "quote", k_quote);
    define_keyword (env, "note", k_note);
    define_keyword (env, "assert", k_assert);
}
