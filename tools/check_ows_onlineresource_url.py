#!/bin/env python3

"""Check that every mapfile advertises its own public address.

GetCapabilities tells clients such as QGIS where to send GetMap, GetFeatureInfo
and WFS requests. That address comes from the ows_onlineresource meta field.
Without it, MapServer guesses one from the request, which behind the gateway
gives an internal host or a /cgi-bin path that does not work.

The field must be MAP_URL_REPLACE/<route>/<name>, where <name> is the file
name without .map. The Dockerfiles replace MAP_URL_REPLACE with the address of
the environment. <route> is where the file is served:

- referentiekaarten/: /tiled
- private/: /maps
- repository root: /maps (public image) or /tiled (the tiled image is built on
  top of the public one, e.g. kbk10)

Pass paths relative to the repository root, as pre-commit does. The check reads
the text instead of parsing with mappyfile, which cannot parse every mapfile
that MapServer accepts.
"""

import re
import sys
from pathlib import Path

# liveness probe, not a published service
SKIP = {"healthcheck.map"}
ROUTES = {"referentiekaarten": ["tiled"], "private": ["maps"]}
ONLINERESOURCE = re.compile(r"""^\s*(["'])ows_onlineresource\1\s+(["'])(.*?)\2""", re.MULTILINE)
FIRST_KEYWORD = re.compile(r"^\s*([A-Za-z]+)", re.MULTILINE)

errors = []
for file in sys.argv[1:]:
    path = Path(file)
    if path.name in SKIP:
        continue
    text = path.read_text(encoding="utf-8")
    first = FIRST_KEYWORD.search(text)
    if not first or first.group(1).upper() != "MAP":
        # fragment, e.g. a LAYER that is copied into another mapfile
        continue
    routes = ROUTES.get(path.parent.name, ["maps", "tiled"])
    expected = [f"MAP_URL_REPLACE/{route}/{path.stem}" for route in routes]
    values = [m.group(3) for m in ONLINERESOURCE.finditer(text)]
    if not values or any(value not in expected for value in values):
        errors.append(
            f"{file}: ows_onlineresource is {values or 'missing'}, expected "
            + " or ".join(f'"{e}"' for e in expected)
        )

for error in errors:
    print(error, file=sys.stderr)
sys.exit(1 if errors else 0)
