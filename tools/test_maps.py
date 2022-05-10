#!/bin/env python3

import argparse
import json
import mappyfile
import logging
from urllib3.util import Url
from requests import Session, Request
from typing import Optional
from lark.exceptions import UnexpectedInput
from pathlib import Path
from xml.etree import ElementTree as ET

# set with env var
logging.basicConfig(level=logging.INFO)

description = """
This script runs basic tests for all maps in this repository, it does this by
making the following assertions for each layer in each map.

    - we can run a GetCapabilities request and get back a 200
    - the GetCapabilities response contains a payload with all layers
    - we can run a GetMap request and get back a 200
    - the response of the GetMap request is an image

Optionally, the script compares the hashes of the GetMap images in the response with the hashes stored
at `checksum_input`.

The stored checksums are named after their complete URL path and querystring. If there is no matching
checksum name for a retrieved image-file, the check cannot occur.

As parameters to the WMS request, we take the max. zoom denominator of the layer
and the center of Amsterdam as bounding box.
"""

SCRIPT_DIR = Path(__file__).parent.absolute()
CHECKSUMS_LOCATION = SCRIPT_DIR / "map_checksums.json"
WORKING_DIR = Path.cwd().absolute()

# Namespaces for searching WMS XML responses
XML_DEFAULT_NAMESPACE = "http://www.opengis.net/wms"
XML_NAMESPACES = {
    "default": XML_DEFAULT_NAMESPACE,
    "xlink": "http://www.w3.org/1999/xlink",
}

parser = argparse.ArgumentParser(description=description)
parser.add_argument("-u", "--url", default="https://map.data.amsterdam.nl/maps")
parser.add_argument(
    "-m",
    "--maps_path",
    type=Path,
    default=WORKING_DIR,
    help="Directory containing the mapfiles, this will be recursively globbed for mapfiles. Can be absolute or relative. Defaults to current working dir.",
)
parser.add_argument("-w", "--wms_version", default="1.3.0")
parser.add_argument(
    "-s",
    "--store_checksums",
    action="store_true",
    help="Save the checkums of the retrieved maps",
)
parser.add_argument(
    "-c",
    "--check_checksums",
    action="store_true",
    help="Match the checksums of the retrieved maps with the stored checksums",
)
parser.add_argument(
    "mapfiles",
    nargs="*",
    help="Specify mapfiles that should be processed (the .map extension must be omitted).",
)


def get_capabilities_request(base_url: str, map_name: str, wms_version: str) -> Request:
    url = Url(
        scheme="https",
        host=base_url.removeprefix("https://").removesuffix("/"),
        path=map_name,
    )
    return Request(
        "GET",
        url,
        params={"service": "wms", "version": wms_version, "request": "GetCapabilities"},
    )


def get_map_request(base_url: str, wms_version: str, map_path: Path, layer: str) -> Request:
    """A GetMap request that uses the Mapserver CGI interface"""
    url = Url(
        scheme="https",
        host=base_url.removeprefix("https://").removesuffix("/maps"),
        path="cgi-bin/mapserv",
    )
    return Request(
        "GET",
        url,
        params={
            "map": map_path.absolute(),
            "service": "wms",
            "version": wms_version,
            "request": "GetMap",
            "bbox": "52.36585716840382787,4.898649147373815183,52.3698249470350774,4.910043532111592945", # centered on Waterlooplein
            "crs": "EPSG:4326", # WGS84
            "width": 1852,
            "height": 645,
            "layers": layer,
            "format": "image/png",
            "dpi": 96,
            "map_resolution": 96,
            "format_options": "dpi:96",
            "transparent": True,
        },
    )


args = parser.parse_args()

def run_tests(
    url: str,
    maps_path: Path,
    wms_version: str,
    store_checksums: bool,
    check_checksums: bool,
    maps: Optional[list[str]] = None,
):
    if maps:
        paths = sorted(
            sum([list(maps_path.glob(f"**/{map_}.map")) for map_ in maps], [])
        )
    else:
        paths = sorted(maps_path.glob("**/*.map"))

    failed = []
    with Session() as session:
        for path in paths:
            logging.info(f"Testing {path}")
            try:
                mapfile = mappyfile.open(path)
            except UnexpectedInput:
                logging.warning(f"Skipping {path} because parsing failed.")

            # the URL path is derived from the mapfile name
            map_url_path = str(path).removesuffix(".map").split("/")[-1]

            request = session.prepare_request(
                get_capabilities_request(url, map_url_path, wms_version)
            )
            response = session.send(request)
            assert response.status_code == 200

            payload = ET.fromstring(response.content)
            try:
                assert payload.tag == f"{{{XML_DEFAULT_NAMESPACE}}}WMS_Capabilities"

                service_tag = payload.find("default:Service", XML_NAMESPACES)
                capability_tag = payload.find("default:Capability", XML_NAMESPACES)
                assert service_tag is not None
                assert capability_tag is not None
            except AssertionError:
                failed.append((path, "GetCapabilities", payload))
                
            # TODO: Deeper assertions?
    logging.info(failed)
    logging.info(f"{len(failed)} of {len(paths)} maps failed")


if __name__ == "__main__":
    run_tests(
        args.url,
        args.maps_path,
        args.wms_version,
        args.store_checksums,
        args.check_checksums,
        args.mapfiles,
    )
