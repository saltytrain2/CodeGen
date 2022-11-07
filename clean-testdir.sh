#!/bin/sh

mkdir tempdir
mv tests/*.cl tempdir/
rm -r tests
mv tempdir tests
