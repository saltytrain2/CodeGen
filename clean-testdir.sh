#!/bin/sh

mkdir tempdir
mv tests/*.cl tempdir/
mv tests/*.txt tempdir/
rm -r tests
mv tempdir tests
