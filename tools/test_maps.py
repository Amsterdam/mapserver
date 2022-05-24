#!/bin/env python3

import argparse
import io
from email.mime import base
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qsl
from xml.dom.minidom import Element
from xml.etree import ElementTree as ET
from json.decoder import JSONDecodeError

import mappyfile
from lark.exceptions import UnexpectedInput
from requests import Request, Session
from urllib3.util import Url, parse_url
from PIL import Image

description = """
This script runs basic tests for all maps in this repository, it does this by
making the following assertions for each layer in each map.

    - we can run a GetCapabilities request and get back a 200
    - the GetCapabilities response contains a payload with all layers
    - we can run a GetMap request and get back a 200
    - the response of the GetMap request is an image

Optionally, the script compares the hashes of the GetMap images in the response with the hashes stored
locally (with -s).

The stored checksums are named after their complete URL path and querystring. If there is no matching
checksum name for a retrieved image-file, the check cannot occur.

As parameters to the WMS GetMap request, we take all layers and the center of Amsterdam as bounding box.
"""

SCRIPT_DIR = Path(__file__).parent.absolute()
CHECKSUMS_LOCATION = SCRIPT_DIR / "map_checksums.json"
WORKING_DIR = Path.cwd().absolute()
HOST_KEY = "HOST"

# Namespaces for searching WMS XML responses
XML_DEFAULT_NAMESPACE = "http://www.opengis.net/wms"
XML_XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"
XML_NAMESPACES = {
    "default": XML_DEFAULT_NAMESPACE,
    "xlink": XML_XLINK_NAMESPACE,
}

parser = argparse.ArgumentParser(description=description)
parser.add_argument("-u", "--url", default="https://acc.map.data.amsterdam.nl")
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
    "-v",
    "--verbose",
    action="store_true",
    help="Show detailed output of failed tests",
)
parser.add_argument(
    "-p",
    "--private",
    action="store_true",
    help="Include private maps in testing",
)
parser.add_argument(
    "mapfiles",
    nargs="*",
    help="Specify mapfiles that should be processed (the .map extension must be omitted).",
)


def get_capabilities_request(base_url: str, map_name: str, wms_version: str) -> Request:
    parsed = parse_url(base_url)
    host = parsed.host
    url = Url(
        scheme=parsed.scheme or "https", # allow scheme overrides
        host=host,
        path=f"maps/{map_name}",
        port=parsed.port # allow port overrides
    )
    return Request(
        "GET",
        url,
        params={"service": "wms", "version": wms_version, "request": "GetCapabilities"},
        headers={
            "Host": host,  # haproxy uses 'Host' for routing
            "User-Agent": "mapserver/testscript",  # to avoid hitting OWASP3.1 913101
        },
    )


def get_map_request(
    base_url: str, wms_version: str, map_path: str, layer: str
) -> Request:
    """A GetMap request that uses the Mapserver CGI interface"""
    parsed = parse_url(base_url)
    host = parsed.host
    url = Url(
        scheme=parsed.scheme or "https", # allow scheme overrides
        host=host,
        path="cgi-bin/mapserv",
        port=parsed.port # allow port overrides
    )
    return Request(
        "GET",
        url,
        params={
            "map": map_path,
            "service": "wms",
            "version": wms_version,
            "request": "GetMap",
            "bbox": "52.36585716840382787,4.898649147373815183,52.3698249470350774,4.910043532111592945",  # centered on Waterlooplein
            "crs": "EPSG:4326",  # WGS84
            "width": 1852,
            "height": 645,
            "layers": layer,
            "format": "image/png",
            "dpi": 96,
            "map_resolution": 96,
            "format_options": "dpi:96",
            "transparent": True,
        },
        headers={
            "Host": host,  # haproxy uses 'Host' for routing
            "User-Agent": "mapserver/testscript",  # to avoid hitting OWASP3.1 913101
        },
    )


def map_param_from_tag(e: Element):
    links = e.find("./default:Request/default:GetMap//*[@xlink:href]", XML_NAMESPACES)
    return parse_qsl(links.attrib.get(f"{{{XML_XLINK_NAMESPACE}}}href"))[0][1]


def get_checksums(base_url: str):
    try:
        with open(CHECKSUMS_LOCATION) as fh:
            checksums = json.load(fh)
    except (FileNotFoundError, JSONDecodeError):
        checksums = {HOST_KEY: base_url}
    return checksums


def run_tests(
    url: str,
    maps_path: Path,
    wms_version: str,
    store_checksums: bool,
    check_checksums: bool,
    private: bool,
    maps: Optional[list[str]] = None,
):
    if maps:
        paths = sorted(
            sum([list(maps_path.glob(f"**/{map_}.map")) for map_ in maps], [])
        )
    else:
        paths = sorted(maps_path.glob("**/*.map"))

    # TODO: If we include private maps and there is a private and public map
    # with the same name, give preference to the private map (this is the case for externeveiligheid)
    if not private:
        paths = [p for p in paths if "private" not in str(p)]

    failed = []
    n_processed = 0

    # count the number of images that have no data
    # to estimate the quality of this testscript
    n_blank = 0

    checksums = {}
    if check_checksums:
        checksums = get_checksums(url)

    with Session() as session:
        for path in paths:
            logging.info(f"Testing {path}")
            try:
                mapfile = mappyfile.open(path)
            except UnexpectedInput:
                logging.warning(f"Skipping {path} because parsing failed.")
                continue

            # the URL path is derived from the mapfile name
            map_url_path = str(path).removesuffix(".map").split("/")[-1]

            request = session.prepare_request(
                get_capabilities_request(url, map_url_path, wms_version)
            )
            response = session.send(request)
            if response.status_code == 200:
                payload = ET.fromstring(response.content)
            else:
                # Responses other than 200 do not provide XML output
                n_processed += len(mapfile["layers"])
                failed.append(
                    (
                        path,
                        "GetCapabilities",
                        response.content,
                        f"Status code is {response.status_code}",
                    )
                )
                continue

            try:
                assert (
                    payload.tag == f"{{{XML_DEFAULT_NAMESPACE}}}WMS_Capabilities"
                ), "Root tag has unexpected name"

                service_tag = payload.find("default:Service", XML_NAMESPACES)
                capability_tag = payload.find("default:Capability", XML_NAMESPACES)
                assert service_tag is not None, "No Service tag found"
                assert capability_tag is not None, "No Capability tag found"
                # Only include Layers that are a child of the root Layer, i.e.: all Groups and Layers
                server_layers = set(
                    [
                        x.text
                        for x in capability_tag.findall(
                            "./default:Layer//default:Layer/default:Name",
                            XML_NAMESPACES,
                        )
                    ]
                )

                # can be replaced with ET.findunique when
                # https://github.com/geographika/mappyfile/pull/153 gets released
                groups = set(
                    [item.get("group", None) for item in mapfile["layers"]]
                ) - {
                    None,
                }

                mapfile_layers = {x["name"] for x in mapfile["layers"]} | groups
                assert (
                    server_layers == mapfile_layers
                ), f"Layers dont match; server has {len(server_layers)}, mapfile has {len(mapfile_layers)}"
            except AssertionError as e:
                n_processed += 1
                failed.append((path, "GetCapabilities", ET.tostring(payload), str(e)))
                continue

            # We get the file path of the map from the XML document because it may not
            # be the same as our local path
            map_param = map_param_from_tag(capability_tag)

            # We need to run a separate query for each layer because querying multiple layers
            # (even when sorted) does not guarantee a deterministic rendering order
            for layer in server_layers - groups:
                layer_id = f"{path} - {layer}",
                n_processed += 1
                request = session.prepare_request(
                    get_map_request(url, wms_version, map_param, layer)
                )

                response = session.send(request, stream=True)  # lazy download

                if (
                    response.status_code != 200
                    or response.headers["Content-Type"] != "image/png"
                ):
                    ct = response.headers["Content-Type"]
                    failed.append(
                        (
                            layer_id,
                            "GetMap",
                            response.content,
                            f"Status code is {response.status_code} and Content-Type is {ct}",
                        )
                    )
                    continue

                if store_checksums or check_checksums:
                    key = response.request.path_url
                    img_bytes = response.content
                    if Image.open(io.BytesIO(img_bytes)).getbbox() is None:
                        n_blank += 1

                    server_checksum = hashlib.md5(img_bytes).hexdigest()
                    if check_checksums:
                        stored_checksum = checksums.get(key, None)
                        try:
                            assert stored_checksum == server_checksum
                        except AssertionError:
                            failed.append(
                                (
                                    layer_id,
                                    "GetMap",
                                    response.content,
                                    f"Checksums dont match, server: {server_checksum} stored: {stored_checksum}",
                                )
                            )
                    if store_checksums:
                        checksums[key] = server_checksum

    if store_checksums:
        CHECKSUMS_LOCATION.touch(exist_ok=True)
        with open(CHECKSUMS_LOCATION, "r+") as fh:
            try:
                payload = json.load(fh)
            except JSONDecodeError:
                payload = {HOST_KEY: url}
            
            if payload[HOST_KEY] == url:
                fh.seek(0)
                json.dump(payload | checksums, fh)
            else:
                logging.warning("Storing checksums would result in mixing checksums from different hosts")
                logging.warning("skipping checksum storage.")

    for f in failed:
        logging.info(f"{f[1]} failed for {f[0]}. Error: {f[3]}  ")
        logging.debug(f"Payload:\n {f[2]}")

    if n_processed > 0:
        n_failed = len(failed)
        logging.info(
            f"Testresults: {n_processed - len(failed)} of {n_processed} ({round(100 - n_failed / n_processed * 100, 2)}%) maplayers succeeded"
        )
        logging.info(
            f"Testresults: {n_blank} of {n_processed} images are empty ({round(100 - n_blank / n_processed * 100, 2)}%)"
        )


if __name__ == "__main__":
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    run_tests(
        args.url,
        args.maps_path,
        args.wms_version,
        args.store_checksums,
        args.check_checksums,
        args.private,
        args.mapfiles,
    )
