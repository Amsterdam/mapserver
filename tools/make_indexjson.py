# Produces a JSON file containing an overview of available maps.
# Usage:
#   python3 tools/make_overview.py *.map
#
# This file needs to be compatible with Python 3.6 as long as our images
# are based on Ubuntu 18.04.

import json
import logging
import os.path
import re
import sys
from typing import Dict, Optional, Tuple


def unquote(s):
    if len(s) >= 2 and s[0] in "'\"" and s[-1] in "'\"":
        s = s[1 : len(s) - 1]
    return s


def parse_mapfile(filename: str) -> Dict[str, object]:
    """Parses a mapfile to extract metadata about a map.

    Returns a dict that possibly maps "title" and "abstract" to the first
    ows_{title,abstract} that occur.
    """
    keys = {
        "ows_title": "title",
        "ows_abstract": "abstract",
    }

    # This is a bit of a hack. It would seem that using mappyfile to parse the
    # mapfiles would be cleaner, but mappyfile doesn't support the full mapfile
    # grammar, so we'd need this as a fallback anyway.
    r = {}
    with open(filename, encoding="utf-8") as f:
        for ln in f:
            ln = ln.split(None, 1)
            if len(ln) == 0:
                continue

            key = keys.get(unquote(ln[0]))
            if key is None:
                continue

            value = ln[1]
            # Remove comments.
            if "#" in value:
                value = value[value.index("#") :]
            value = value.strip()

            if value.startswith('"') or value.startswith("'"):
                value = value[1:-1]
            r.setdefault(key, value)

    return r


NAME_RE = re.compile("^[A-Za-z0-9_]+")


if __name__ == "__main__":
    logger = logging.getLogger(sys.argv[0])

    index = {}
    for f in sys.argv[1:]:
        props = parse_mapfile(f)
        name = os.path.basename(f)[: -len(".map")]
        if not NAME_RE.match(name):
            logger.error("Name should match %r, got %r", NAME_RE.pattern, name)
            continue
        index[name] = props

    json.dump(index, sys.stdout, sort_keys=True)
