#include "scan.hpp"

bool space_char_p (char c)
{
    return (c == ' '  ||
            c == '\n' ||
            c == '\t');
}

bool delimiter_char_p (char c)
{
    return (c == '(' ||
            c == ')' ||
            c == '[' ||
            c == ']' ||
            c == '{' ||
            c == '}' ||
            c == ',' ||
            c == ';' ||
            c == '`' ||
            c == '\'');
}

string
string_from_char (char c)
{
    string str = "";
    str.push_back (c);
    return str;
}

bool doublequote_char_p (char c)
{
    return c == '"';
}

size_t find_word_length (string code, size_t begin)
{
    size_t length = code.length ();
    size_t index = begin;
    while (true) {
        if (index == length)
            return index - begin;
        char c = code [index];
        if (space_char_p (c) or
            doublequote_char_p (c) or
            delimiter_char_p (c))
            return index - begin;
        index++;
    }
}

size_t find_string_length (string code, size_t begin)
{
    size_t length = code.length ();
    size_t index = begin + 1;
    while (true) {
        if (index == length) {
            cout << "- fatal error : find_string_length" << "\n";
            cout << "  doublequote mismatch" << "\n";
            exit (1);
        }
        char c = code [index];
        if (doublequote_char_p (c))
            return index - begin + 1;
        index++;
    }
}

string_vector_t
scan_word_vector (string code)
{
    auto string_vector = string_vector_t ();
    size_t i = 0;
    size_t length = code.length ();
    while (i < length) {
        char c = code [i];
        if (space_char_p (c)) i++;
        else if (delimiter_char_p (c)) {
            string_vector.push_back (string_from_char (c));
            i++;
        }
        else if (doublequote_char_p (c)) {
            auto string_length = find_string_length (code, i);
            string str = code.substr (i, string_length);
            string_vector.push_back (str);
            i += string_length;
        }
        else {
            auto word_length = find_word_length (code, i);
            string word = code.substr (i, word_length);
            string_vector.push_back (word);
            i += word_length;
        }
    }
    return string_vector;
}

void
test_scan ()
{
    auto code = "(cons-c <car> <cdr>)";
    auto string_vector = scan_word_vector (code);
    assert (string_vector.size () == 5);
    assert (string_vector [0] == "(");
    assert (string_vector [1] == "cons-c");
    assert (string_vector [2] == "<car>");
    assert (string_vector [3] == "<cdr>");
    assert (string_vector [4] == ")");

    {
        auto code = "\"123\"";
        auto string_vector = scan_word_vector (code);
        assert (string_vector.size () == 1);
        assert (string_vector [0] == "\"123\"");
    }

}
