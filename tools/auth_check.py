#!/usr/bin/env python

import argparse
import glob
from pathlib import Path
from typing import Optional

import logging
import mappyfile as mf
import sqlparse
from mappyfile.parser import Parser
from mappyfile.transformer import MapfileToDict
from mappyfile.pprint import PrettyPrinter
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


def get_table_identifiers(data_expr: str) -> set[str]:
    """Given a data expression from a mapfile DATA parameter,
    get all the table identifiers used in FROM and JOIN clauses.

    This logic assumes that data expressions consist of a single statement,
    i.e: everything after the first semicolon is ignored.
    """
    if len(data_expr) == 0:
        return set()

    table_clauses = {
        "FROM",
        "LEFT OUTER JOIN",
        "INNER JOIN",
        "RIGHT OUTER JOIN",
        "FULL OUTER JOIN",
        "JOIN",
        "RIGHT JOIN",
        "LEFT JOIN",
        "FULL JOIN",
    }

    tokens = [x for x in sqlparse.parse(data_expr)[0].flatten() if not x.is_whitespace]
    identifiers = set()

    for i, token in enumerate(tokens):
        try:
            if (
                tokens[i - 1].is_keyword
                and tokens[i - 1].value.upper() in table_clauses
            ):
                if type(token) == sqlparse.sql.Identifier:
                    identifiers.add(token.value)
        except IndexError:
            # the Identifier token occurs at the beginning of the statement
            # in which case it can not be part of a FROM or JOIN clause
            continue

    return identifiers


def run_check(schema_url: str, private_only: bool, include_maps: Optional[list[str]], exclude_maps: Optional[list[str]]):
    printer = PrettyPrinter()

    public_maps = sorted(glob.glob(str(repo_root / f"*.map")))
    private_maps = sorted(glob.glob(str(repo_root / "private/*.map")))
    logger.info(
        "Found %s public and %s private maps", len(public_maps), len(private_maps)
    )

    logger.info("Loading schemas from %s", schema_url)
    schemas = dataset_schemas_from_url(schema_url)

    private_scopes = set()

    # private maps must not contain scops higher than FP/MDW
    for fname in private_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = parse_private(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            if "connectiontype" not in layer or layer["connectiontype"].lower() != "postgis":
                continue

            data_expr = layer["data"][0]
            logger.debug(
                "Data definition for layer %s: \n\n %s", layer.get("name"), data_expr
            )

            # brute force it
            for dataset in schemas.values():
                for table in dataset.tables:
                    if table.db_name in data_expr:
                        private_scopes |= table.auth
                        private_scopes |= dataset.auth
                        for f in table.fields:
                            private_scopes |= f.auth
    
    logger.info(
        "Found the following scopes in private maps: \n\n - %s", "\n - ".join(private_scopes)
    )

    if private_only:
        return

    public_scopes = set()
    # public maps must not contain scopes higher than OPENBAAR
    for fname in public_maps:
        if include_maps and Path(fname).name.removesuffix(".map") not in include_maps:
            continue
        if exclude_maps and Path(fname).name.removesuffix(".map") in exclude_maps:
            continue

        map_ = mf.open(fname)

        logger.debug("Parsed map: \n%s", printer.pprint(map_))

        for layer in map_["layers"]:
            if "connectiontype" not in layer or layer["connectiontype"].lower() != "postgis":
                continue

            data_expr = layer["data"][0]
            logger.debug(
                "Data definition for layer %s: \n\n %s", layer.get("name"), data_expr
            )

            # brute force it
            for dataset in schemas.values():
                for table in dataset.tables:
                    if table.db_name in data_expr:
                        public_scopes |= table.auth
                        public_scopes |= dataset.auth
                        for f in table.fields:
                            public_scopes |= f.auth
    
    logger.info(
        "Found the following scopes in public maps: \n\n - %s", "\n - ".join(public_scopes)
    )


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(level=args.verbose)
    run_check(args.acc, args.private, args.include, args.exclude)
