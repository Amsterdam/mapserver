# Produces a JSON file containing an overview of available maps.
# Usage:
#   python3 tools/make_overview.py *.map
#
# This file needs to be compatible with Python 3.6 as long as our images
# are based on Ubuntu 18.04.

import json
import logging
import sys
from typing import Dict, Optional, Tuple

import mappyfile


def dict_get(x: Dict, *keys: str) -> Optional[object]:
    for key in keys:
        # Don't use x[key] here, because mappyfile uses custom dicts
        # that have the annoying habit of adding non-existent keys (!).
        x = x.get(key)
        if x is None:
            break
    return x


def parse_mapfile(filename: str) -> Tuple[str, Dict[str, object]]:
    m = mappyfile.open(filename)
    r = {}
    for key, path in (
        ("title", ["web", "metadata", "ows_title"]),
        ("abstract", ["web", "metadata", "ows_abstract"]),
    ):
        val = dict_get(m, *path)
        if val is not None:
            r[key] = val
    return m["name"], r


if __name__ == "__main__":
    logger = logging.getLogger(sys.argv[0])

    index = {}
    for f in sys.argv[1:]:
        # It's tempting to just dump mappyfile.open(f) as JSON,
        # but doing so leaks the db passwords, which mappyfile inserts
        # when expanding the includes.
        try:
            name, props = parse_mapfile(f)
        except Exception as e:
            logger.error(e)
            continue
        index[name] = props

    json.dump(index, sys.stdout, sort_keys=True)
