#include "test_all.hpp"

#include "test/test_step.hpp"
#include "test/test_data.hpp"

#include "object/bool.hpp"
#include "object/int.hpp"
#include "object/str.hpp"
#include "object/list.hpp"
#include "object/vect.hpp"
#include "object/dict.hpp"

#include "scan.hpp"

void
test_all ()
{
    test_step ();
    test_data ();
    // test_apply ();
    // test_lambda_curry ();
    // test_data_cons ();
    // test_data_cons_curry ();
    // test_prim ();

    test_bool ();
    test_int ();
    test_str ();
    test_list ();
    test_vect ();
    test_dict ();

    test_scan ();
}
