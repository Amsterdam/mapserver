#!/usr/bin/env python

# Generates the overlastgebieden map.

from generate import block, header, p, q

# Name, basename of table, color
layers = [
    ("algemeen_overlastgebied", "algemeenoverlast_v2", '#d4212c'),
    ("cameratoezichtgebied", "cameratoezicht_v2", '#337229'),
    ("dealeroverlastgebied", "dealeroverlast_v2", '#3166bc'),
    ("uitgaansoverlastgebied", "uitgaansoverlast_v1", '#ff8011'),
    ("alcoholverbodsgebied", "alcoholverbod_v2", '#a91ba9'),
    ("straatartiestverbod", "straatartiestverbod_v2", '#990033'),
    ("taxi-standplaatsgebied", "taxistandplaats_v1", '#ecd316'),
    ("barbecueverbodsgebieden", "barbecueverbod_v2", '#a00078'),
    ("rondleidingverbodsgebieden", "rondleidingverbod_v2", '#00d2b4'),
    ("messenverbodgebieden", "messenverbod_v2", '#ff0000'),
    ("groepsfietsverbodgebieden", "groepsfietsverbod_v2", '#ffff00'),
    ("raamsluitingstijden", "sluitingstijdenkernwallen_v2", '#00a03c'),
    ("alcoholverkoopverbodgebied", "alcoholverkoopverbod_v2", '#e50082'),
    ("blowverbodsgebied", "blowverbodsgebied_v2", '#009dec'),
    ("bedelverbodgebied", "bedelverbod_v2", "#fd4401")
]

header()

with block("MAP"):
    p("NAME", "Overlastgebieden")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("team", "SVD")
            q("ows_title", "Overlastgebieden")
            q("ows_abstract", "Overlastgebieden")

    for name, basename, color in layers:
        with block("LAYER"):
            p("NAME", name)
            p("GROUP", "overlastgebieden")
            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", f"geometry FROM public.overlastgebieden_{basename}_v2 USING srid=28992 USING UNIQUE id")
            p("TYPE POLYGON")
            p("MINSCALEDENOM 100")
            p("MAXSCALEDENOM 400000")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            with block("PROJECTION"):
                q("init=epsg:28992")

            with block("METADATA"):
                q("ows_title", name)
                q("ows_group_title", "overlastgebieden")
                q("ows_abstract", "Overlastgebieden van de gemeente Amsterdam")
                q("gml_featureid", "ID")
                q("gml_include_items", "all")
                q("wms_extent", "100000 450000 150000 500000")

            with block("CLASS"):
                p("NAME", name.replace("-", "_").title().replace("_", ""))
                with block("STYLE"):
                    p("ANTIALIAS true")
                    p(f'COLOR "{color}"') # p(f'COLOR "#{color:06x}"')
                    p("OPACITY 20")
                with block("STYLE"):
                    p(f'OUTLINECOLOR "{color}"') # p(f'OUTLINECOLOR "#{color:06x}"')
                    p("WIDTH 2")

    for name, basename, color in layers:
        name += "_label"

        with block("LAYER"):
            p("NAME", name)
            p("GROUP", "overlastgebieden")
            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", f"geometry FROM public.overlastgebieden_{basename} USING srid=28992 USING UNIQUE id")
            p("TYPE POLYGON")

            if name == "algemeen_overlastgebied":
                p("MAXSCALEDENOM", 8000)
            else:
                p("MINSCALEDENOM", 100)
                p("MAXSCALEDENOM", 8001)

            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            with block("PROJECTION"):
                q("init=epsg:28992")

            with block("METADATA"):
                q("ows_title", name)
                q("ows_group_title", "overlastgebieden")
                q("ows_abstract", "Labels van de overlastgebieden van de gemeente Amsterdam")

            with block("CLASS"):
                p("TEXT", "[oov_naam]")
                p("NAME", name)

                for minscale, maxscale, fontsize in [
                    (None, 3000, 14),
                    (3000, 6000, 12),
                    (6000, 8000, 10),
                ]:
                    with block("LABEL"):
                        if minscale is not None:
                            p("MINSCALEDENOM", minscale)
                        p("MAXSCALEDENOM", maxscale)
                        p(f'COLOR "{color}"') # p(f'COLOR "#{color:06x}"')
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 1")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p(f"SIZE {fontsize}")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")
