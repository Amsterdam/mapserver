#!/usr/bin/env python

# Generates the beschermdestadsdorpsgezichten mapfile.

from generate import block, p, q


BSD_LONG = "Beschermde stads- en dorpsgezichten"
BSD_SHORT = "beschermdestadsdorpsgezichten"

layers = [
    ("Gemeentelijk beschermd stadsgezicht", "#00008b70"),
    ("Gemeentelijk beschermd dorpsgezicht", "#0000cd70"),
    ("Rijksbeschermd stadsgezicht", "#cd000070"),
    ("Rijksbeschermd dorpsgezicht", "#ff450070"),
]

print("# GENERATED FILE, DO NOT EDIT.\n\n")
print("# TEAM: SOEB\n")

with block("MAP"):
    p("NAME", BSD_SHORT)
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", BSD_LONG)
            q(
                "ows_abstract",
                "Kaart met gegevens over beschermde stads- en dorpsgezichten in de gemeente Amsterdam",
            )
            q("wms_extent", "100000 450000 150000 500000")

    for name, color in layers:
        with block("LAYER"):
            p("NAME", name)

            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            p(
                "DATA",
                f"geometry FROM public.{BSD_SHORT}_{BSD_SHORT} USING UNIQUE id USING srid=28992",
            )
            p("TYPE POLYGON")

            with block("METADATA"):
                q("wfs_enable_request", "none")
                q("wms_title", name)
                q("wms_enable_request", "*")
                q("wms_abstract", BSD_LONG)
                q("wms_srs", "EPSG:28992")
                q("wms_name", BSD_LONG)
                q("wms_format", "image/png")
                q("wms_server_version", "1.3.0")
                q("wms_extent", "100000 450000 150000 500000")

            p("LABELITEM", "status")
            p("CLASSITEM", "status")

            with block("CLASS"):
                p("NAME", name)
                p("EXPRESSION", name)

                with block("STYLE"):
                    p("COLOR", color)
