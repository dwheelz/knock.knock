#!/bin/bash
for filename in ./config/*.fwknoprc; do
    [ -e "$filename" ] || continue
    fwknop --rc-file "$filename" --verbose
done