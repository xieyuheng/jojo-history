#!/bin/sh

#cc=gcc
cc=clang

w='-Wno-int-conversion -Wno-incompatible-pointer-types -Wno-return-type -Wunused-value'
o='-O2'
f='-fPIC'

l=''
b='-shared -Wl,-Bsymbolic'

build() {
    $cc $w $f $o -c haha.c
    $cc $l $b -o haha.so haha.o
}

default() {
    time build
}

if [ $# -eq 0 ]; then
    default
else
    $1
fi
