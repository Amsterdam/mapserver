#!/bin/env python3

"""Check formatting of a mapfile. """

import sys
import mappyfile
import fileinput

files = sys.argv[1:]

for file in files:
    d = mappyfile.open(
        file,
        expand_includes=False,
        include_comments=True,
        include_position=True,
    )
    mappyfile.save(
        d,
        file,
        align_values=True,
        spacer=" ",
        indent=2,
    )

    # make mappyfile output posix compliant
    for line in fileinput.input(file, inplace=True):
        print(line.rstrip())
    with open(file, 'a', encoding="utf-8") as fp:
        fp.write("")
    sys.exit(0)
