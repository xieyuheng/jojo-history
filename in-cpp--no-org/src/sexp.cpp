#include "sexp.hpp"

#include "scan.hpp"

// - about literal in quote
//   | ( ) | list-t |
//   | [ ] | vect-t |
//   | { } | dict-t |

// drop `,`
shared_ptr <obj_t>
word_vector_to_word_list
(env_t &env, string_vector_t &word_vector)
{
    auto begin = word_vector.rbegin ();
    auto end = word_vector.rend ();
    auto collect = null_c (env);
    for (auto it = begin; it != end; it++) {
        auto word = *it;
        if (word != ",") {
            auto obj = make_shared <str_o> (env, word);
            collect = cons_c (env, obj, collect);
        }
    }
    return collect;
}

shared_ptr <obj_t>
scan_word_list (env_t &env, shared_ptr <str_o> code)
{
    auto word_vector = scan_word_vector (code->str);
    return word_vector_to_word_list
        (env, word_vector);
}

bool
bar_word_p (string word)
{
    return word == "("
        || word == "["
        || word == "{";
}

bool
ket_word_p (string word)
{
    return word == ")"
        || word == "]"
        || word == "}";
}

bool
quote_word_p (string word)
{
    return word == "'"
        || word == "`";
}

string
bar_word_to_ket_word (string bar)
{
    assert (bar_word_p (bar));
    if (bar == "(") return ")";
    if (bar == "[") return "]";
    if (bar == "{") return "}";
    cout << "bar_word_to_ket_word fail\n";
    exit (1);
}

shared_ptr <obj_t>
word_list_head_with_bar_ket_counter
(env_t &env,
 shared_ptr <obj_t> word_list,
 string bar,
 string ket,
 size_t counter)
{
    if (counter == 0)
        return null_c (env);
    auto head = static_pointer_cast <str_o>
        (car (env, word_list));
    auto word = head->str;
    if (word == bar)
        return cons_c
            (env, head, word_list_head_with_bar_ket_counter
             (env,
              cdr (env, word_list),
              bar, ket, counter + 1));
    if (word == ket)
        return cons_c
            (env, head, word_list_head_with_bar_ket_counter
             (env,
              cdr (env, word_list),
              bar, ket, counter - 1));
    else
        return cons_c
            (env, head, word_list_head_with_bar_ket_counter
             (env,
              cdr (env, word_list),
              bar, ket, counter));
}

shared_ptr <obj_t>
word_list_head (env_t &env, shared_ptr <obj_t> word_list)
{
    assert (cons_p (env, word_list));
    auto head = static_pointer_cast <str_o>
        (car (env, word_list));
    auto word = head->str;
    if (bar_word_p (word)) {
        auto bar = word;
        auto ket = bar_word_to_ket_word (word);
        return cons_c
            (env, head, word_list_head_with_bar_ket_counter
             (env,
              cdr (env, word_list),
              bar, ket, 1));
    }
    else if (quote_word_p (word))
        return cons_c (env, head,
                       word_list_head (env, cdr (env, word_list)));
    else
        return cons_c (env, head, null_c (env));
}

shared_ptr <obj_t>
word_list_rest_with_bar_ket_counter
(env_t &env,
 shared_ptr <obj_t> word_list,
 string bar,
 string ket,
 size_t counter)
{
    if (counter == 0)
        return word_list;
    auto head = static_pointer_cast <str_o>
        (car (env, word_list));
    auto word = head->str;
    if (word == bar)
        return word_list_rest_with_bar_ket_counter
            (env,
             cdr (env, word_list),
             bar, ket, counter + 1);
    if (word == ket)
        return word_list_rest_with_bar_ket_counter
            (env,
             cdr (env, word_list),
             bar, ket, counter - 1);
    else
        return word_list_rest_with_bar_ket_counter
            (env,
             cdr (env, word_list),
             bar, ket, counter);
}

shared_ptr <obj_t>
word_list_rest (env_t &env, shared_ptr <obj_t> word_list)
{
    assert (cons_p (env, word_list));
    auto head = static_pointer_cast <str_o>
        (car (env, word_list));
    auto word = head->str;
    if (bar_word_p (word)) {
        auto bar = word;
        auto ket = bar_word_to_ket_word (word);
        return word_list_rest_with_bar_ket_counter
            (env,
             cdr (env, word_list),
             bar, ket, 1);
    }
    else if (quote_word_p (word))
        return word_list_rest (env, cdr (env, word_list));
    else
        return cdr (env, word_list);
}

shared_ptr <obj_t>
word_list_drop_ket
(env_t &env,
 shared_ptr <obj_t> word_list,
 string ket)
{
    auto head = car (env, word_list);
    auto rest = cdr (env, word_list);
    if (null_p (env, rest))
        return null_c (env);
    auto cdr_rest = cdr (env, rest);
    auto car_rest = static_pointer_cast <str_o> (car (env, rest));
    auto word = car_rest->str;
    if (null_p (env, cdr_rest)) {
        assert (word == ket);
        return cons_c (env, head, null_c (env));
    }
    else {
        return cons_c (env, head,
                       word_list_drop_ket (env, rest, ket));
    }
}

shared_ptr <obj_t>
parse_sexp (env_t &env, shared_ptr <obj_t> word_list)
{
    auto head = static_pointer_cast <str_o>
        (car (env, word_list));
    auto word = head->str;
    auto rest = cdr (env, word_list);
    if (word == "(")
        return parse_sexp_list
            (env, word_list_drop_ket (env, rest, ")"));
    else if (word == "[")
        return list_to_vect
            (env, parse_sexp_list
             (env, word_list_drop_ket (env, rest, "]")));
    else if (word == "{")
        return list_to_dict
            (env, parse_sexp_list
             (env, word_list_drop_ket (env, rest, "}")));
    else if (word == "'")
        return cons_c (env, make_shared <str_o> (env, "quote"),
                       cons_c (env, parse_sexp (env, rest),
                               null_c (env)));
    else if (word == "`")
        return cons_c (env, make_shared <str_o> (env, "partquote"),
                       cons_c (env, parse_sexp (env, rest),
                               null_c (env)));
    else
        return head;
}

shared_ptr <obj_t>
parse_sexp_list (env_t &env, shared_ptr <obj_t> word_list)
{
    if (null_p (env, word_list))
        return word_list;
    else
        return cons_c
            (env,
             parse_sexp (env, word_list_head (env, word_list)),
             parse_sexp_list (env, word_list_rest (env, word_list)));
}

string
sexp_repr (env_t &env, shared_ptr <obj_t> a)
{
    if (null_p (env, a)) {
        return "()";
    }
    else if (cons_p (env, a)) {
        return "(" + sexp_list_repr (env, a) + ")";
    }
    else if (vect_p (env, a)) {
        auto v = static_pointer_cast <vect_o> (a);
        auto l = vect_to_list (env, v);
        return "[" + sexp_list_repr (env, l) + "]";
    }
    else if (dict_p (env, a)) {
        auto d = static_pointer_cast <dict_o> (a);
        auto l = dict_to_list (env, d);
        return "{" + sexp_list_repr (env, l) + "}";
    }
    else {
        assert (str_p (env, a));
        auto str = static_pointer_cast <str_o> (a);
        return str->str;
    }
}

string
sexp_list_repr (env_t &env, shared_ptr <obj_t> sexp_list)
{
    if (null_p (env, sexp_list))
        return "";
    else if (null_p (env, cdr (env, sexp_list)))
        return sexp_repr (env, car (env, sexp_list));
    else {
        return
            sexp_repr (env, car (env, sexp_list)) + " " +
            sexp_list_repr (env, cdr (env, sexp_list));
    }
}
