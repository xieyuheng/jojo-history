#!/bin/sh

#cc=gcc
cc=clang

w='-Wno-int-conversion -Wno-incompatible-pointer-types -Wno-return-type -Wunused-value'
o='-O2'
f='-g'

l='-ldl'
b='-Wl,--export-dynamic'

copy() {
    rsync --recursive --links --perms --times --group --owner --devices --specials --verbose --human-readable $@
}

tangle() {
    ./tangle.js
    xxd -i core.jo > core.h
}

build() {
    $cc $w $f $o -c jojo.c
    $cc $l $b -o jojo jojo.o
}

fast_build() {
    $cc $w $f -c jojo.c
    $cc $l $b -o jojo jojo.o
}

clean() {
    rm -f jojo
    rm -f core.jojo.*
}

run() {
    ./jojo
}

default() {
    tangle
    clean
    time build
}

install_modules_to_default_usr_jojo_dir () {
    copy modules ~/.jojo/
}

remove_all_modules_in_default_usr_jojo_dir () {
    rm -rf ~/.jojo/modules/
}

fast() {
    tangle
    clean
    time fast_build
}

if [ $# -eq 0 ]; then
    default
else
    $1
fi
