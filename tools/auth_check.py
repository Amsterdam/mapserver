#!/usr/bin/env python

import argparse
import glob
import logging
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Optional
from schematools.loaders import get_schema_loader

import mappyfile as mf
from mappyfile.parser import Parser
from mappyfile.pprint import PrettyPrinter
from mappyfile.transformer import MapfileToDict
from schematools.types import DatasetSchema


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
    help="List of mapfiles to exclude (references by the name of the file without the .map extension i.e.: '<name>.map')",
)
parser.add_argument(
    "-l",
    "--exclude-layers",
    nargs="*",
    help="List of layers to exclude (references by the name of the file and the layer separated by a . i.e.: '<mapname>.<layername>')",
)

logger = logging.getLogger("authchecker")


class UnresolvableIncludesParser(Parser):
    """
    Some of our mapfiles contain INCLUDE directives
    pointing to files that are dynamically generated and
    therefore may not exist yet at auth_checking-time.

    This class allows us to walk the mapfile ast without
    breaking on the files that do not exist, but whose
    contents we do not need for auth checking.

    The file content returned is given by an optional substitution function.
    Note that this content must be valid mapfile syntax.
    """

    unresolvable={
        repo_root / "connection": lambda x: f"CONNECTION \"{x}\"",
    }

    def open_file(self, fn):
        for prefix, substitute_func in self.unresolvable.items():
            if str(fn).startswith(str(prefix)):
                return substitute_func(fn)

        return super().open_file(fn)


def parse(fname: Path | str):
    parser = UnresolvableIncludesParser(
        expand_includes=True,
        include_comments=False,
    )

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

def is_reference_db_layer(layer: str) -> bool:
    """Connection files are injected into the repo at build time so we only
    have access to the name of the connection file at auth checking time.
    We assume that any file named dataservices.inc is a connection to the reference database.
    """
    return "connection" in layer and layer["connection"].removesuffix(".inc").endswith("dataservices")


def auth_from_layer(
    map_name: str,
    layer: dict[str, str],
    schemas: dict[str, DatasetSchema],
    highest_scope: str,
) -> list[SimpleNamespace]:
    """Check if the layer uses tables from the reference database that contain scopes
    that are too high according to the given highest_scope, and if so, dump the auth info in
    a namespace describing the table and field level auth scopes that are too high."""
    if not is_reference_db_layer(layer):
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


def exit(check_failed: bool):
    sys.exit(int(check_failed))


def run_check(
    schema_url: str,
    private_only: bool,
    include_maps: Optional[list[str]],
    exclude_maps: Optional[list[str]],
    exclude_layers: Optional[list[tuple[str]]],
):
    printer = PrettyPrinter()

    public_maps = sorted(glob.glob(str(repo_root / f"*.map")))
    private_maps = sorted(glob.glob(str(repo_root / "private/*.map")))
    logger.info(
        "Found %s public and %s private maps", len(public_maps), len(private_maps)
    )
    logger.info("Using %s as repository root", repo_root)

    logger.info("Loading schemas from %s", schema_url)
    loader = get_schema_loader(schema_url)
    schemas = loader.get_all_datasets()

    prohibited_queries = []
    check_failed = False

    for fname in private_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = parse(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            # private maps must not contain scopes higher than FP/MDW
            if (map_["name"], layer["name"]) in exclude_layers:
                continue
            prohibited_queries.extend(
                auth_from_layer(map_["name"], layer, schemas, SCOPE_FP_MDW)
            )
    if prohibited_queries:
        logger.info(
            "Found the following queries in private maps that are possibly breaching auth requirements: \n\n - %s",
            "\n - ".join(map(str, prohibited_queries)),
        )
        check_failed = True

    if private_only:
        exit(check_failed)

    prohibited_queries = []
    for fname in public_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = parse(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            # public maps must not contain scopes higher than OPENBAAR
            if (map_["name"], layer["name"]) in exclude_layers:
                continue
            prohibited_queries.extend(
                auth_from_layer(map_["name"], layer, schemas, SCOPE_OPENBAAR)
            )

    if prohibited_queries:
        logger.info(
            "Found the following queries in public maps that are possibly breaching auth requirements: \n\n - %s",
            "\n - ".join(map(str, prohibited_queries)),
        )
        check_failed = True
    exit(check_failed)


def run():
    args = parser.parse_args()
    logging.basicConfig(level=args.verbose)
    exclude_layers = [
        tuple(x.split("."))
        for x in (args.exclude_layers or [])
        if len(x.split(".")) == 2
    ]
    run_check(args.acc, args.private, args.include, args.exclude, exclude_layers)


if __name__ == "__main__":
    run()
