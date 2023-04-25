#!/usr/bin/env python

# Generates the ziektenplagenexotengroen mapfile.
# TODO rewrite using mappyfile, generalize.

from contextlib import contextmanager

indent: int = 0


def p(*strs: list[str]):
    print("  " * indent, end="")
    print(strs[0], end="")
    if len(strs) > 1:
        print(" ", end="")
    print_quoted(strs[1:])


def q(*strs: list[str]):
    print("  " * indent, end="")
    print_quoted(strs)


def print_quoted(strs: list[str]):
    print(*map(repr, strs))


@contextmanager
def block(typ: str):
    p(typ)
    global indent
    indent += 1
    yield
    indent -= 1
    p("END")


layers = [
    ("Eikenprocessierups aanwezig (Laag)", "caterpillar_blue"),
    ("Eikenprocessierups deels bestreden", "tree_orange"),
    ("Niet in beheergebied Gemeente Amsterdam", "flag_black"),
    ("Eikenprocessierups aanwezig (Urgent)", "caterpillar_red"),
    ("Gemeld", "speechbubble"),
    ("Eikenprocessierups bestreden", "tree_green"),
    ("Geen Eikenprocessierups aanwezig", "tree_black"),
    ("Niet bereikbaar voor bestrijding", "flag_red"),
    ("Eikenprocessierups aanwezig (Standaard)", "caterpillar_orange"),
]

print("# GENERATED FILE, DO NOT EDIT.\n\n")
print("# TEAM: Bor / Beeldschoon\n")

with block("MAP"):
    p("NAME", "ziektenplagenexotengroen")
    p("INCLUDE", "header.inc")
    p("DEBUG", 5)

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Ziekte, plagen, exoten, groen")
            q(
                "ows_abstract",
                "Kaart met gegevens over ziekten, plagen en exoten in het groen in de gemeente Amsterdam",
            )
            q("wms_extent", "100000 450000 150000 500000")

    for name, icon in layers:
        with block("LAYER"):
            p("NAME", name)

            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection_dataservices.inc")
            p(
                "DATA",
                "geometrie FROM public.ziekte_plagen_exoten_groen_eikenprocessierups USING srid=28992 USING UNIQUE id",
            )
            p("TYPE POINT")

            with block("METADATA"):
                q("wfs_enable_request", "none")
                q("wms_title", name)
                q("wms_enable_request", "*")
                q("wms_abstract", "Eikenprocessierups Amsterdam")
                q("wms_srs", "EPSG:28992")
                q("wms_name", "Eikenprocessierups")
                q("wms_format", "image/png")
                q("wms_server_version", "1.3.0")
                q("wms_extent", "100000 450000 150000 500000")

            p("LABELITEM", "urgentie_status_kaartlaag")
            p("CLASSITEM", "urgentie_status_kaartlaag")

            with block("CLASS"):
                p("NAME", name)
                p("EXPRESSION", name)

                with block("STYLE"):
                    p("SYMBOL", icon)
                    p("SIZE", 20)
