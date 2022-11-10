#!/usr/bin/env python

import argparse
import glob
import logging
import re
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import mappyfile as mf
from mappyfile.parser import Parser
from mappyfile.pprint import PrettyPrinter
from mappyfile.transformer import MapfileToDict
from schematools.types import DatasetSchema
from schematools.utils import dataset_schemas_from_url

SCHEMA_URL = "https://schemas.data.amsterdam.nl/datasets"
ACC_SCHEMA_URL = "https://acc.schemas.data.amsterdam.nl/datasets"

repo_root = Path(__file__).parent.parent

parser = argparse.ArgumentParser()
parser.add_argument(
    "--acc", action="store_const", const=ACC_SCHEMA_URL, default=SCHEMA_URL
)
parser.add_argument("--private", action="store_true", help="Only handle private maps")
parser.add_argument(
    "-v", "--verbose", action="store_const", const=logging.DEBUG, default=logging.INFO
)
parser.add_argument(
    "-i",
    "--include",
    nargs="*",
    help="List of mapfiles to parse (references by the name of the file i.e.: <name>.map)",
)
parser.add_argument(
    "-e",
    "--exclude",
    nargs="*",
    help="List of mapfiles to exclude (references by the name of the file i.e.: <name>.map)",
)

logger = logging.getLogger("[Auth check script]")


def parse_private(fname: Path | str):
    """Use the mapfile Parser directly so we can parse the file
    while pointing the parser to the repo root dir to resolve includes.

    This is required because INCLUDEs in private maps assume that the
    maps have been copied to the repository root before opening them
    with the mapserver parser.
    """

    parser = Parser(expand_includes=True, include_comments=False)

    text = parser.open_file(fname)
    # pretend that the file is in the repo root
    ast = parser.parse(text, fn=repo_root / Path(fname).name)
    m = MapfileToDict(include_position=False, include_comments=False)
    return m.transform(ast)


SCOPE_OPENBAAR = "OPENBAAR"
SCOPE_FP_MDW = "FP/MDW"


def scope_too_high(scope: str, highest_scope: str) -> bool:
    ordering = {SCOPE_OPENBAAR: 0, SCOPE_FP_MDW: 1}

    return ordering.get(scope, 999) > ordering[highest_scope]


azure_pattern = re.compile(".*dbname=mdbdataservices.*")
cloudvps_pattern = re.compile(".*dbname=dataservices.*")


def is_reference_db_conn(dsn: str) -> bool:
    return bool(azure_pattern.match(dsn) or cloudvps_pattern.match(dsn))


def auth_from_layer(
    map_name: str,
    layer: dict[str, str],
    schemas: dict[str, DatasetSchema],
    highest_scope: str,
) -> list[SimpleNamespace]:
    """Check if the layer uses tables from the reference database that contain scopes
    that are too high according to the given highest_scope, and if so, dump the auth info in
    a namespace describing the table and field level auth scopes that are too high."""
    # The default connectiontype is local, in which case we are consuming from a
    # local shapefile
    if "connectiontype" not in layer or layer["connectiontype"].lower() != "postgis":
        return []
    if "connection" not in layer or not is_reference_db_conn(layer["connection"]):
        return []

    data_expr = layer["data"][0]
    logger.debug("Data definition for layer %s: \n\n %s", layer.get("name"), data_expr)

    auth_data = []
    # brute force it
    for dataset in schemas.values():
        for table in dataset.tables:
            if table.db_name in data_expr:
                table_auth = SimpleNamespace(
                    map_=map_name,
                    layer=layer["name"],
                    table=table.db_name,
                    table_scopes=set(),
                    field_scopes=[],
                    max_scope=highest_scope,
                )
                for scope in dataset.auth:
                    if scope_too_high(scope, highest_scope):
                        table_auth.table_scopes.add(scope)

                for f in table.fields:
                    for scope in f.auth:
                        if scope_too_high(scope, highest_scope):
                            table_auth.field_scopes.append((f.db_name, scope))

                if len(table_auth.table_scopes) or len(table_auth.field_scopes):
                    auth_data.append(table_auth)

    return auth_data


def run_check(
    schema_url: str,
    private_only: bool,
    include_maps: Optional[list[str]],
    exclude_maps: Optional[list[str]],
):
    printer = PrettyPrinter()

    public_maps = sorted(glob.glob(str(repo_root / f"*.map")))
    private_maps = sorted(glob.glob(str(repo_root / "private/*.map")))
    logger.info(
        "Found %s public and %s private maps", len(public_maps), len(private_maps)
    )

    logger.info("Loading schemas from %s", schema_url)
    schemas = dataset_schemas_from_url(schema_url)

    prohibited_queries = []

    for fname in private_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = parse_private(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            # private maps must not contain scopes higher than FP/MDW
            prohibited_queries.extend(
                auth_from_layer(map_["name"], layer, schemas, SCOPE_FP_MDW)
            )
    if prohibited_queries:

        logger.info(
            "Found the following queries in private maps that are possibly breaching auth requirements: \n\n - %s",
            "\n - ".join(map(str, prohibited_queries)),
        )

    if private_only:
        return

    prohibited_queries = []
    for fname in public_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = mf.open(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            # public maps must not contain scopes higher than OPENBAAR
            prohibited_queries.extend(
                auth_from_layer(map_["name"], layer, schemas, SCOPE_OPENBAAR)
            )

    if prohibited_queries:
        logger.info(
            "Found the following queries in pulic maps that are possibly breaching auth requirements: \n\n - %s",
            "\n - ".join(map(str, prohibited_queries)),
        )


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.verbose)
    run_check(args.acc, args.private, args.include, args.exclude)
