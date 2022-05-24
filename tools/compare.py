#!/bin/env python3

"""Compares two map images from different hosts. One host stored in the map checksums and the other given as parameter to the script. """

import argparse
import hashlib
import requests
from PIL import Image, ImageChops
from test_maps import get_checksums, HOST_KEY
from urllib3.util import Url, parse_url
import io

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("map")
    parser.add_argument("layer")
    parser.add_argument("-u", "--url", default="https://acc.map.data.amsterdam.nl", help="host to compare against")

    args = parser.parse_args()

    checksums = get_checksums(args.url)
    stored_host = checksums[HOST_KEY]
    uri = [k for k, v in checksums.items() if args.map in k and args.layer in k][0]
    ref_bytes = requests.get(
        Url(scheme="https", host=stored_host, path=uri), 
        headers={
            "Host": stored_host,  # haproxy uses 'Host' for routing
            "User-Agent": "mapserver/testscript",  # to avoid hitting OWASP3.1 913101
        },
        stream=True
    ).content
    ref_image = Image.open(io.BytesIO(ref_bytes))


    cmp_host = parse_url(args.url)
    cmp_bytes = requests.get(
        Url(scheme=cmp_host.scheme or "https", host=cmp_host.host, path=uri, port=cmp_host.port), 
        headers={
            "Host": cmp_host.host,  # haproxy uses 'Host' for routing
            "User-Agent": "mapserver/testscript",  # to avoid hitting OWASP3.1 913101
        },
        stream=True
    ).content
    cmp_image = Image.open(io.BytesIO(cmp_bytes))

    diff = ImageChops.difference(ref_image, cmp_image)
    if diff.getbbox():
        diff.show()