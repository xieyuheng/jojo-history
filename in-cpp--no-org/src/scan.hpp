#pragma once

#include "libjojo.hpp"

bool space_char_p (char c);

bool delimiter_char_p (char c);

string
string_from_char (char c);

bool doublequote_char_p (char c);

size_t find_word_length (string code, size_t begin);

size_t find_string_length (string code, size_t begin);

string_vector_t
scan_word_vector (string code);

void
test_scan ();
