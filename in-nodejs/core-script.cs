    (+fun drop (let x))
    (+fun dup (let x) x x)
    (+fun over (let x y) x y x)
    (+fun tuck (let x y) y x y)
    (+fun swap (let x y) y x)
    (+macro note drop
      '(begin))
    (+fun ifte
      (let bool true-fn false-fn)
      (case bool
        (true-t true-fn)
        (false-t false-fn)))
    (+macro if
      (let body)
      body.car (let question)
      body.cdr.car (let on-true)
      body.cdr.cdr.car (let on-false)
      `(case (@ question)
         (true-t (@ on-true))
         (false-t (@ on-false))))
    (+macro when (let body)
      `(if (@ body.car)
         (@ 'begin body.cdr cons-c)
         []))

    (+macro unless (let body)
      `(if (@ body.car)
         []
         (@ 'begin body.cdr cons-c)))
    (+macro assert (let body)
      `(if [(@ body list-spread)]
         []
         ["- (assert) fail : " string-print
          (quote (@ body)) sexp-list-print nl]))

    (+macro assert! (let body)
      `(if [(@ body list-spread)]
         []
         ["- (assert!) fail : " string-print
          (quote (@ body)) sexp-list-print nl
          error]))
    (+macro and (let body)
      (if [body null-p]
        'true-c
        `(if (@ body.car)
           [(@ body.cdr recur)]
           false-c)))

    (+macro or (let body)
      (if [body null-p]
        'false-c
        `(if (@ body.car)
           true-c
           [(@ body.cdr recur)])))
    (+macro cond (let body)
      (case body
        (null-t
          `(begin
             "- cond mismatch!" string-print nl
             error))
        (cons-t
          body.car (when [dup 'else eq-p] drop 'true-c) (let question)
          body.cdr.car (let answer)
          `(if (@ question)
             (@ answer)
             (@ body.cdr.cdr recur)))))
    (+gene repr 1
      default-repr)
    (+disp repr [string-t]
      doublequote-string swap string-append
      doublequote-string string-append)
    (+disp repr [number-t]
      number->string)
    (+gene w 1
      repr string-print)
    (+gene p 1
      w)
    (+disp p [string-t]
      string-print)
    (+gene length 1
      error)
    (+gene empty-p 1
      error)
    (+gene inc 1
      error)
    (+gene dec 1
      error)
    (+gene add 2
      error)
    (+gene sub 2
      error)
    (+gene mul 2
      error)
    (+gene div 2
      error)
    (+gene mod 2
      error)
    (+gene moddiv 2
      (let x y)
      x y mod
      x y div)
    (+gene divmod 2
      (let x y)
      x y div
      x y mod)
  (+gene not 1
    error)
    (+gene gt-p 2
      error)
    (+gene lt-p 2
      error)
    (+gene gteq-p 2
      (let x y)
      (or [x y eq-p]
          [x y gt-p]))
    (+gene lteq-p 2
      (let x y)
      (or [x y eq-p]
          [x y lt-p]))
    (+fun times (let fun n)
      (unless [n 0 number-lteq-p]
        fun
        {fun} n number-dec recur))
    (+union bool-u
      true-t
      false-t)
    (+fun bool-assert
      (let bool)
      (case bool
        (true-t)
        (else
          "- bool-assertion fail : " p bool p nl)))
    (+macro bool-if
      (let body)
      body.car (let true-fn)
      body.cdr.car (let false-fn)
      `(begin
         {(@ true-fn)}
         {(@ false-fn)}
         ifte))
    (+macro bool-when
      (let body)
      `(begin
         {(@ body list-spread)}
         {}
         ifte))

    (+macro bool-when-not
      (let body)
      `(begin
         {}
         {(@ body list-spread)}
         ifte))
    (+disp repr [bool-u]
      (bool-if "true-c" "false-c"))
    (+disp not [bool-u]
      bool-not)
    (+disp gt-p [number-t number-t]
      number-gt-p)
    (+disp lt-p [number-t number-t]
      number-lt-p)
    (+disp inc [number-t]
      number-inc)
    (+disp dec [number-t]
      number-dec)
    (+disp add [number-t number-t]
      number-add)
    (+disp sub [number-t number-t]
      number-sub)
    (+disp mul [number-t number-t]
      number-mul)
    (+disp div [number-t number-t]
      number-div)
    (+disp mod [number-t number-t]
      number-mod)
    (+fun string-head
      0 string-ref)
    (+fun string-tail
      dup string-length
      1 swap string-slice)
    (+fun string-last
      dup string-length
      dup number-dec swap string-slice)
    (+fun string-take
      (let string length)
      string 0 length string-slice)
    (+fun string-drop
      (let string length)
      string length string string-length string-slice)
    (+fun string-member-p
      (let string substring)
      substring string-length (let length)
      (cond
        [string string-length length lt-p] false-c
        [string length string-take substring eq-p] true-c
        else [string string-tail substring recur]))
    (+fun string-split-by-char
      0 string-split-by-char-with-cursor)
    (+fun string-split-by-char-with-cursor
      (let string char cursor)
      (cond
        [string string-length cursor lteq-p]
        [string null-c cons-c]

        [string cursor string-ref char eq-p]
        [string cursor string-take
         string cursor string-drop string-tail char 0 recur
         cons-c]

        else
        [string char cursor number-inc recur]))
    (+fun decons
      dup .car swap .cdr)
    (+union list-u
      null-t
      cons-t)
    (+macro lit-list (let body)
      `(begin mark (@ body list-spread) collect-list))
    (+fun list-length (let list)
      (if [list null-p]
        0
        [list.cdr recur number-inc]))
    (+fun list-ref
      (let list index)
      (if [index 0 eq-p]
        [list.car]
        [list.cdr index dec recur]))
    (+fun list-append (let ante succ)
      (case ante
        (null-t succ)
        (cons-t ante.car ante.cdr succ recur cons-c)))
    (+fun tail-cons null-c cons-c list-append)
    (+fun list-reverse null-c swap list-reverse-swap-append)

    (+fun list-reverse-swap-append
      ;; -> ante list -- list
      (let list)
      (case list
        (null-t)
        (cons-t list.car swap cons-c list.cdr recur)))
    (+fun list-any-p (let list pred)
      (cond [list null-p] false-c
            [list.car pred] true-c
            else [list.cdr {pred} recur]))
    (+fun list-every-p (let list pred)
      (cond [list null-p] true-c
            [list.car pred bool-not] false-c
            else [list.cdr {pred} recur]))
    (+fun list-ante (let list pred)
      (cond [list null-p] null-c
            [list.car pred] null-c
            else [list.car
                  list.cdr {pred} recur
                  cons-c]))
    (+fun list-succ (let list pred)
      (cond [list null-p] null-c
            [list.car pred] list
            else [list.cdr {pred} recur]))
    (+fun list-split-to-two (let list pred) ;; -- ante succ
      (cond [list null-p] [null-c null-c]
            [list.car pred] [null-c list]
            else [list.car
                  list.cdr {pred} recur
                  (let succ) cons-c succ]))
    (+fun list-map (let list fun)
      (case list
        (null-t null-c)
        (cons-t list.car fun list.cdr {fun} recur cons-c)))
    (+fun list-for-each (let list fun)
      (case list
        (null-t)
        (cons-t list.car fun list.cdr {fun} recur)))
    (+fun list-filter (let list pred)
      (cond [list null-p] null-c
            [list.car pred]
            [list.car list.cdr {pred} recur cons-c]
            else [list.cdr {pred} recur]))
    (+fun list-foldr (let list b a-b->b)
      (case list
        (null-t b)
        (cons-t
          list.car
          list.cdr b {a-b->b} recur
          a-b->b)))
    (+fun list-foldl (let list b b-a->b)
      (case list
        (null-t b)
        (cons-t
          list.cdr b {b-a->b} recur
          list.car
          b-a->b)))
    (+fun list-member-p (let list x)
      list {x eq-p} list-any-p)
    (+disp repr [list-u]
      (let list)
      (case list
        (null-t "(lit-list)")
        (cons-t
          list list-inner-repr
          "(lit-list " swap string-append
          ")" string-append )))

    (+fun list-inner-repr
      (let list)
      (case list
        (null-t "")
        (cons-t
          list.car repr
          (unless [list.cdr null-p]
            " " string-append
            list.cdr recur string-append))))
    (+disp p [list-u]
      "[" p
      list-inner-print
      "]" p)

    (+fun list-inner-print
      (let list)
      (case list
        (null-t)
        (cons-t
          list.car p
          (case list.cdr
            (null-t)
            (cons-t
              " " p list.cdr recur)
            (else
              " . " p list.cdr p)))))
    (+data dict-t
      assoc-list)
    (+fun dict-length
      .assoc-list list-length)
    (+fun dict-empty-p
      dict-length 0 eq-p)
    (+fun new-dict
      null-c dict-c)
    (+fun dict-find
      (let dict key)
      ;; -- | value true-t
      ;;      false-t
      dict.assoc-list
      key assoc-list-find)
    (+fun dict-get
      (let dict key)
      ;; -- | value true-t
      ;;      false-t
      dict key dict-find
      (bool-when-not
        "- dict-get fail" p nl
        "  key : " p key p nl
        "  dict : " p dict p nl
        error))
    (+fun assoc-list-find
      (let assoc-list key)
      ;; -- | value true-t
      ;;      false-t
      (case assoc-list
        (null-t false-c)
        (cons-t
          (if [assoc-list.car.car key eq-p]
            [assoc-list.car.cdr true-c]
            [assoc-list.cdr key recur]))))
    (+fun dict-insert
      (let dict key value)
      ;; -- dict
      dict.assoc-list
      key value assoc-list-insert
      (. assoc-list) dict clone)
    (+fun assoc-list-insert
      (let assoc-list key value)
      key value cons-c assoc-list cons-c)
    (+macro lit-dict (let body)
      `(begin (lit-list (@ body list-spread)) even-list->dict))
    (+fun even-list->dict
      even-list->assoc-list dict-c)
    (+fun even-list->assoc-list
      (let even-list)
      (case even-list
        (null-t null-c)
        (cons-t
          even-list.car even-list.cdr.car cons-c
          even-list.cdr.cdr recur cons-c)))
    (+disp repr [dict-t]
      .assoc-list (let assoc-list)
      (case assoc-list
        (null-t "(lit-dict)")
        (cons-t
          "(lit-dict "
          assoc-list assoc-list-inner-repr string-append
          ")" string-append)))
    (+fun assoc-list-inner-repr
      (let assoc-list)
      (case assoc-list
        (null-t "")
        (cons-t
          assoc-list.car decons
          swap repr " " string-append
          swap repr string-append
          (unless [assoc-list.cdr null-p]
            ", " string-append
            assoc-list.cdr recur string-append))))
    (+disp p [dict-t]
      "[" p
      .assoc-list assoc-list-inner-print
      "]" p)
    (+fun assoc-list-inner-print
      (let assoc-list)
      (case assoc-list
        (null-t)
        (cons-t
          assoc-list.car.car p " = " p
          assoc-list.car.cdr p
          (case assoc-list.cdr
            (null-t)
            (cons-t
              ", " p
              assoc-list.cdr recur)))))
    (+fun dict-for-each (let dict fun)
      dict.assoc-list {decons fun} list-for-each)
    (assert
      true-c false-c bool-and
      false-c eq-p)

    (assert
      true-c false-c bool-or
      true-c eq-p)

    (assert
      true-c bool-not
      false-c eq-p)

    (assert
      true-c bool-not bool-not
      true-c eq-p)

    (assert
      true-c not
      false-c eq-p)

    (assert
      true-c not not
      true-c eq-p)
    (assert
      1 dup number-add 2 eq-p)
    (assert
      1 2 3 null-c cons-c cons-c cons-c
      1 2 3 null-c cons-c cons-c cons-c eq-p)
      (assert 2 dec 1 eq-p)
      (+fun number-factorial-case
        (let n)
        (case [n 0 eq-p]
          (true-t 1)
          (false-t n number-dec recur n number-mul)))

      (assert
        5 number-factorial-case
        120 eq-p)

      (+fun number-factorial-ifte
        (let n)
        n 0 eq-p
        {1}
        {n number-dec recur n number-mul}
        ifte)

      (assert
        5 number-factorial-ifte
        120 eq-p)

      (+fun number-factorial
        (let n)
        (if [n 0 eq-p]
          1
          [n number-dec recur n number-mul]))

      (assert
        5 number-factorial
        120 eq-p)
    (assert
      "0123" string-length
      4 eq-p)

    (assert
      "0123" "4567" string-append
      "01234567" eq-p)

    (assert
      "01234567" 3 string-ref
      "3" eq-p)

    (assert
      "01234567" 3 5 string-slice
      "34" eq-p)

    (assert
      123 number->string
      "123" eq-p)

    (assert
      "01234567" string-head
      "0" eq-p)

    (assert
      "01234567" string-tail
      "1234567" eq-p)

    (assert
      "01234567" string-last
      "7" eq-p)

    (assert
      "01234567" 3 string-take
      "012" eq-p)

    (assert
      "01234567" 3 string-drop
      "34567" eq-p)

    (assert
      "01234567" "34567" string-member-p)

    (assert
      "01234567" "012" string-member-p)

    (assert
      "01234567" "34567*" string-member-p bool-not)

    (assert
      "01234567" "*012" string-member-p bool-not)

    (assert
      "0123.4567" "." string-split-by-char
      (lit-list "0123" "4567")
      eq-p)

    (assert
      "..0123..4567.." "." string-split-by-char
      (lit-list "" "" "0123" "" "4567" "" "")
      eq-p)

    (assert
      "0.1.2.3.4.5.6.7" "." string-split-by-char
      '(0 1 2 3 4 5 6 7)
      eq-p)
    (+union nat-u
      zero-t
      succ-t)

    (+data zero-t)

    (+data succ-t
      prev)

    (+fun nat-add
      (let m n)
      (case n
        (zero-t m)
        (succ-t m n.prev recur succ-c)))

    (+fun nat-mul
      (let m n)
      (case n
        (zero-t n)
        (succ-t m n.prev recur m nat-add)))

    (+fun nat-factorial
      (let n)
      (case n
        (zero-t zero-c succ-c)
        (succ-t n.prev recur n nat-mul)))

    (assert
      zero-c succ-c succ-c succ-c succ-c succ-c nat-factorial
      zero-c succ-c succ-c succ-c succ-c succ-c
      zero-c succ-c succ-c succ-c succ-c nat-mul
      zero-c succ-c succ-c succ-c nat-mul
      zero-c succ-c succ-c nat-mul
      zero-c succ-c nat-mul
      eq-p)
    (+var var-cons 1 null-c cons-c)

    (assert
      2 var-cons.car!
      var-cons 2 null-c cons-c eq-p)

    (+fun nat->number
      (let n)
      (case n
        (zero-t 0)
        (succ-t n.prev recur number-inc)))

    (+var var-nat zero-c succ-c succ-c)

    (assert
      var-nat nat->number 2 eq-p)

    (assert
      zero-c var-nat.prev!
      var-nat nat->number 1 eq-p)
    (assert
      `(1 2 (@ 1 2 number-add number->string))
      '(1 2 3) eq-p)
    (+gene gene0 2
      drop drop
      "default gene0")

    (assert 1 2 gene0 "default gene0" eq-p)

    (+disp gene0 [number-t number-t]
      drop drop
      "number-t number-t gene0")

    (assert 1 2 gene0 "number-t number-t gene0" eq-p)
    (assert
      (when [1 1 eq-p] 'ok)
      'ok eq-p)

    (assert
      true-c
      (unless [1 1 eq-p] 'ugh))

    (assert
      true-c
      (when [1 2 eq-p] 'ugh))

    (assert
      (unless [1 2 eq-p] 'ok)
      'ok eq-p)
      (assert
        "" {"*" string-append} 3 times
        "***" eq-p)
    (begin
      1 2 cons-c
      decons
      2 eq-p bool-assert
      1 eq-p bool-assert)
      (assert
        mark 0 1 2 3 4 collect-list
        (lit-list 0 1 2 3 4)
        eq-p)
      (assert '(a b c) list-length 3 eq-p)
      (assert '(a b c) '(d e f) list-append '(a b c d e f) eq-p)
      (assert '(a b c) 'd tail-cons '(a b c d) eq-p)

      (assert
        (lit-list 0 1 2 3 4)
        (lit-list 5 6 7 8 9)
        list-append
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        eq-p)

      (assert
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        list-reverse
        (lit-list 9 8 7 6 5 4 3 2 1 0)
        eq-p)
      (assert
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        {5 gteq-p} list-ante
        (lit-list 0 1 2 3 4)
        eq-p)

      (assert
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        {5 gteq-p} list-split-to-two
        swap (lit-list 0 1 2 3 4) eq-p
        swap (lit-list 5 6 7 8 9) eq-p
        bool-and)
      (assert
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        {inc} list-map
        (lit-list 1 2 3 4 5 6 7 8 9 10)
        eq-p)

      (assert
        (lit-list 0 1 2 3 4 5 6 7 8 9)
        {2 mod 0 eq-p} list-filter
        (lit-list 0 2 4 6 8)
        eq-p)
      (assert
        (lit-list 0 1 2 3 4 5) 100 {add} list-foldr
        0 1 2 3 4 5 100 add add add add add add
        eq-p)

      (assert
        (lit-list 0 1 2 3 4 5) 100 {add} list-foldl
        100 5 add 4 add 3 add 2 add 1 add 0 add
        eq-p)

      (assert
        (lit-list
          (lit-list 1 2 3)
          (lit-list 4 5 6)
          (lit-list 7 8 9))
        null-c {list-append} list-foldr
        (lit-list 1 2 3, 4 5 6, 7 8 9)
        eq-p)

      (assert
        (lit-list
          (lit-list 1 2 3)
          (lit-list 4 5 6)
          (lit-list 7 8 9))
        null-c {list-append} list-foldl
        (lit-list 7 8 9, 4 5 6, 1 2 3)
        eq-p)
      (begin
        new-dict
        1 "v1" dict-insert (let dict)
        dict 1 dict-find bool-assert
        "v1" eq-p bool-assert)

      (begin
        new-dict
        1 "v1" dict-insert
        2 "v2" dict-insert
        3 "v3" dict-insert
        (let dict)
        dict 1 dict-get "v1" eq-p bool-assert
        dict 2 dict-get "v2" eq-p bool-assert
        dict 3 dict-get "v3" eq-p bool-assert)
      (begin
        (lit-dict
         1 "v1"
         2 "v2"
         3 "v3")
        (let dict)
        dict 1 dict-find bool-assert "v1" eq-p bool-assert
        dict 2 dict-find bool-assert "v2" eq-p bool-assert
        dict 3 dict-find bool-assert "v3" eq-p bool-assert)
      #note
      (begin
        (lit-dict
         1 "v1"
         2 "v2"
         3 "v3")
        {(let key value) key p " " p value p nl}
        dict-for-each)
    (assert true-c (bool-if 1 2) 1 eq-p)
    (assert false-c (bool-if 1 2) 2 eq-p)

    (assert true-c (bool-when 'ok) 'ok eq-p)
    (assert 'ok false-c (bool-when 'ugh) 'ok eq-p)

    (assert false-c (bool-when-not 'ok) 'ok eq-p)
    (assert 'ok true-c (bool-when-not 'ugh) 'ok eq-p)
    #note
    (begin
      '(a b c) w nl
      '(a b c) p nl)

    #note
    (begin
      zero-c succ-c p nl)

    #note
    (begin
      (lit-list
       (lit-list
        (lit-dict
         1 "v1"
         2 (lit-dict
            1 "v1"
            2 "v2"
            3 "v3")
         3 "v3")))
      (let dict)
      dict w nl)

    #note
    (begin
      '(1 2 3) p nl)


