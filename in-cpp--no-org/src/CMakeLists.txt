cmake_minimum_required(VERSION 2.8)

project(jojo)

add_executable(jojo jojo.cpp
  libjojo.cpp
  object/bool.cpp
  object/closure.cpp
  object/data.cpp
  object/data_cons.cpp
  object/dict.cpp
  object/int.cpp
  object/keyword.cpp
  object/list.cpp
  object/prim.cpp
  object/str.cpp
  object/top_keyword.cpp
  object/type.cpp
  object/vect.cpp
  syntax/apply_jo.cpp
  syntax/assert.cpp
  syntax/assert_jo.cpp
  syntax/assign.cpp
  syntax/call_compile.cpp
  syntax/case.cpp
  syntax/case_jo.cpp
  syntax/collect_dict_jo.cpp
  syntax/collect_vect_jo.cpp
  syntax/dict_compile.cpp
  syntax/field_jo.cpp
  syntax/field_string_compile.cpp
  syntax/int_string_compile.cpp
  syntax/key_string_compile.cpp
  syntax/keyword_compile.cpp
  syntax/lambda.cpp
  syntax/lambda_jo.cpp
  syntax/lit_jo.cpp
  syntax/local_ref_jo.cpp
  syntax/note.cpp
  syntax/quote.cpp
  syntax/ref_compile.cpp
  syntax/ref_jo.cpp
  syntax/string_string_compile.cpp
  syntax/vect_compile.cpp
  scan.cpp
  sexp.cpp
  compile.cpp
  eval.cpp
  test/test_data.cpp
  test/test_step.cpp
  test_all.cpp
  import/import_bool.cpp
  import/import_dict.cpp
  import/import_int.cpp
  import/import_keyword.cpp
  import/import_list.cpp
  import/import_misc.cpp
  import/import_sexp.cpp
  import/import_stack.cpp
  import/import_str.cpp
  import/import_syntax.cpp
  import/import_top_keyword.cpp
  import/import_type.cpp
  import/import_vect.cpp
  import_all.cpp)

install(TARGETS jojo DESTINATION bin)