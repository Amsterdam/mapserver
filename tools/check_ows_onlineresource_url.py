#!/bin/env python3

"""Check that the value in the ows_onlineresource_domain meta field starts with the url placeholder. """

import sys
import mappyfile

files = sys.argv[1:]

for file in files:
    map = mappyfile.open(file, expand_includes=False)
    ows_onlineresource = map['web']['metadata'].get("ows_onlineresource", "MAP_URL_REPLACE/")
    assert ows_onlineresource.startswith("MAP_URL_REPLACE/")
     