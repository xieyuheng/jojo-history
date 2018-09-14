#! /bin/bash

test ()
{
    ./tangle.js
    time ./cicada-script
    cp cicada-script cicada-script.js core-script.cs ~/bin
}

test
