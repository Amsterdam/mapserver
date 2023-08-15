# Produces a JSON file containing an overview of available maps.
# Usage:
#   python3 tools/make_overview.py *.map
#
# This file needs to be compatible with Python 3.6 as long as our images
# are based on Ubuntu 18.04.

import json
import logging
import re
import sys
from typing import Dict, Optional, Tuple


def parse_mapfile(filename: str) -> Tuple[str, Dict[str, object]]:
    """Parses a mapfile to extract metadata about a map.

    Returns the name of the map, and a dict that possibly maps "title" and
    "abstract" to the first ows_{title,abstract} that occur.
    """
    keys = {
        "NAME": "name",
        '"ows_title"': "title",
        '"ows_abstract"': "abstract",
    }

    # This is a bit of a hack. It would seem that using mappyfile to parse the
    # mapfiles would be cleaner, but mappyfile doesn't support the full mapfile
    # grammar, so we'd need this as a fallback anyway.
    r = {}
    with open(filename, encoding="utf-8") as f:
        for ln in f:
            ln = ln.split()
            if len(ln) == 0:
                continue

            key = keys.get(ln[0])
            if key is None:
                continue

            value = ln[1]
            if value.startswith('"') or value.startswith("'"):
                value = value[1:-1]
            r.setdefault(key, value)

    name = r.pop("name")
    return name, r


NAME_RE = re.compile("^[A-Za-z0-9_]+")


if __name__ == "__main__":
    logger = logging.getLogger(sys.argv[0])

    index = {}
    for f in sys.argv[1:]:
        name, props = parse_mapfile(f)
        if not NAME_RE.match(name):
            logger.error("Name should match %r, got %r", NAME_RE.pattern, name)
            continue
        index[name] = props

    json.dump(index, sys.stdout, sort_keys=True)
