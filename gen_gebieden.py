from generate import block, header, p, q


# name, group, classname, table, color, minscale, midscale, maxscale, abstract
#
# Scales are for the labels only.
layers = [
    (
        "buurt",
        "bestuurlijke_gebieden",
        "Buurt",
        "buurten",
        "210 150 50",
        100,
        6001,
        8001,
        "Buurten van de gemeente Amsterdam",
    ),
    # The *_simple layers exist for backward compatibility only.
    (
        "buurt_simple",
        "bestuurlijke_gebieden",
        "Buurt",
        "buurten",
        "210 150 50",
        100,
        6001,
        8001,
        "Buurten van de gemeente Amsterdam",
    ),
    # De historic name "buurtcombinatie" is used for wijken because
    # data.amsterdam.nl still depends on it.
    (
        "buurtcombinatie",
        "bestuurlijke_gebieden",
        "Wijk",
        "wijken",
        "210 100 50",
        5000,
        10001,
        15001,
        "Wijken van de gemeente Amsterdam",
    ),
    (
        "buurtcombinatie_simple",
        "bestuurlijke_gebieden",
        "Wijk",
        "wijken",
        "210 100 50",
        5000,
        10001,
        15001,
        "Wijken van de gemeente Amsterdam",
    ),
    (
        "gebiedsgerichtwerken",
        "gebieden",
        "Gebiedsgerichtwerken-gebied",
        "ggwgebieden",
        "40 150 10",
        4000,
        10001,
        40001,
        "Gebiedsgerichtwerken gebieden van de gemeente Amsterdam",
    ),
    (
        "gebiedsgerichtwerkenpraktijkgebieden",
        "gebieden",
        "Gebiedsgerichtwerken-praktijkgebied",
        "ggpgebieden",
        "0 70 153",
        4000,
        10001,
        40001,
        "Gebiedsgerichtwerken praktijkgebieden van de gemeente Amsterdam",
    ),
    (
        "stadsdeel",
        "bestuurlijke_gebieden",
        "Stadsdeel",
        "stadsdelen",
        "210 50 50",
        15000,
        50001,
        100001,
        "Stadsdelen van de gemeente Amsterdam",
    ),
    (
        "bouwblok",
        "gebieden",
        "Bouwblok",
        "bouwblokken",
        "0 150 255",
        100,
        2501,
        5001,
        "Bouwblokken van de gemeente Amsterdam",
    ),
    # The old gebieden.map said (since 2019) that the following was DEPRECATED,
    # to be replaced by grootstedelijk_regio_amsterdam and
    # grootstedelijk_regio_omgevingsdienst.
    #
    # Should draw from grootstedelijke_gebieden, but see below.
    (
        "grootstedelijkgebied",
        "gebieden",
        "Grootstedelijk gebied",
        "grootstedelijke_projecten",
        "150 40 255",
        4000,
        50001,
        100001,
        "Grootstedelijke Gebieden van de gemeente Amsterdam",
    ),
]


# GROUP grootstedelijkgebieden.
#
# These should draw from the table grootstedelijke_gebieden, but that doesn't
# exist yet. Note that grootstedelijke_gebieden has different column names
# compared to grootstedelijke_projecten, e.g., "identificatie" vs. "id".
#
# name, gsg_type, color, classname
gsg_layers = [
    (
        "grootstedelijk_regio_amsterdam",
        "GSP",
        "160 0 120",
        "Grootstedelijke Gebieden Regie Gemeente Amsterdam",
    ),
    (
        "grootstedelijk_regio_omgevingsdienst",
        "OD",
        "0 160 60",
        "Grootstedelijke Gebieden Regie Omgevingsdienst",
    ),
    # XXX Amsterdam Schema says the allowed values are GSP, OD, PHS of PHSOD.
    # But the values in the refdb are GSP, OD, PS_GSP, PS_OD.
    ("gsg4_phsod", "PS_OD", "120 160 0", "PHS regie Omgevingsdienst"),
    ("gsg4_phs", "PS_GSP", "160 16 0", "PHS regie Gemeente Amsterdam"),
    # XXX The following two are duplicates of the first two layers in this list.
    ("gsg4_od", "OD", "0 160 60", "regie Omgevingsdienst"),
    ("gsg4_gsp", "GSP", "160 0 120", "regie Gemeente Amsterdam"),
]


def make_data(table_basename: str):
    data = f"""geometrie FROM (
        SELECT * FROM public.gebieden_{table_basename}
        WHERE
            begin_geldigheid <= now()
            AND coalesce(eind_geldigheid, now()) >= now()
        ) AS sub
        USING srid=28992 USING UNIQUE identificatie"""
    return " ".join(data.split())  # Normalize whitespace.


header(team="BenK")

with block("MAP"):
    p("NAME", "GEBIEDEN")
    p("INCLUDE", "header.inc")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "GEBIEDEN")
            q(
                "ows_abstract",
                "Gebieden met een geografische component, waarvan Amsterdam de bronhouder is",
            )

    for name, group, classname, table, color, minsc, midsc, maxsc, abstract in layers:
        if table.startswith("grootstedelijke_"):
            # These are structured differently from the rest.
            data = (
                f"geometrie FROM public.gebieden_{table}"
                + "USING srid=28992 USING UNIQUE identificatie"
            )
        else:
            data = make_data(table)

        with block("LAYER"):  # Polygon layer.
            p("NAME", name)
            p("GROUP", group)
            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", data)

            p("TYPE POLYGON")
            p("MINSCALEDENOM 100")
            p("MAXSCALEDENOM 100001")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            with block("PROJECTION"):
                q("init=epsg:28992")

            with block("METADATA"):
                q("ows_title", name)
                q("ows_group_title", group)
                q("ows_abstract", abstract)
                q("gml_featureid", "ID")
                q("gml_include_items", "all")

            with block("CLASS"):
                p("NAME", classname)
                with block("STYLE"):
                    p("ANTIALIAS true")
                    p(f"OUTLINECOLOR {color}")
                    p("WIDTH 2")

        with block("LAYER"):  # Corresponding label layer.
            p("NAME", name + "_label")
            p("GROUP", group)
            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", data)

            p("TYPE POLYGON")
            p(f"MINSCALEDENOM {minsc}")
            p(f"MAXSCALEDENOM {maxsc}")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            with block("PROJECTION"):
                q("init=epsg:28992")

            with block("METADATA"):
                q("ows_title", name + "_label")
                q("ows_group_title", group)
                q("ows_abstract", "Labels van: " + abstract)

            with block("CLASS"):
                p("TEXT", "[naam] ([code])")
                p("NAME", classname + " code")
                for lo, hi, size in [(minsc, midsc, 10), (midsc, maxsc, 8)]:
                    with block("LABEL"):
                        p(f"MINSCALEDENOM {lo}")
                        p(f"MAXSCALEDENOM {hi}")
                        p(f"COLOR {color}")
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 3")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p(f"SIZE {size}")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")

    # UNESCO zones.
    with block("LAYER"):
        p("NAME", "unesco")
        p("GROUP", "gebieden")
        # Switch to dataservices once the data has landed.
        p("INCLUDE", "connection/bag.inc")

        # For refdb:
        #
        # SELECT * FROM public.monumenten_unesco
        # WHERE
        #   datum_aanwijzing <= now()
        #   AND coalesce(datum_actueel_tot, now()) >= now()
        p(
            "DATA",
            "geometrie FROM public.geo_bag_unesco USING srid=28992 USING UNIQUE id",
        )

        p("TYPE POLYGON")
        p("MINSCALEDENOM 100")
        p("MAXSCALEDENOM 20001")
        p("OPACITY 60")
        p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
        with block("PROJECTION"):
            q("init=epsg:28992")

        with block("METADATA"):
            q("ows_title", "unesco")
            q("ows_group_title", "gebieden")
            q("ows_abstract", "Unesco werelderfgoedgrens van de gemeente Amsterdam")
            q("gml_featureid", "ID")
            q("gml_include_items", "all")

        p("CLASSITEM naam")
        for zone, color in [("Kern", "255 140 40"), ("Buffer", "255 200 150")]:
            with block("CLASS"):
                p(f"NAME {zone}zone")
                p(f"EXPRESSION /{zone}zone/")
                with block("STYLE"):
                    p(f"COLOR {color}")
                    p("OUTLINECOLOR 172 172 172")
                    p("WIDTH 1")

    # Grootstedelijke gebieden.
    for name, gsg_type, color, classname in gsg_layers:
        with block("LAYER"):
            group = "gsg4" if name.startswith("gsg4") else "grootstedelijkgebieden"
            p("NAME", name)
            p("GROUP", group)
            p("INCLUDE", "connection/dataservices.inc")
            # p("DATA", make_data("grootstedelijke_projecten"))
            p(
                "DATA",
                "geometrie FROM public.gebieden_grootstedelijke_projecten "
                + "USING srid=28992 USING UNIQUE id",
            )

            p("TYPE POLYGON")
            p(f"MINSCALEDENOM 100")
            p(f"MAXSCALEDENOM 100001")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            with block("PROJECTION"):
                q("init=epsg:28992")

            with block("METADATA"):
                q("ows_title", name)
                q("ows_group_title", group)
                q("ows_abstract", classname)
                q("gml_featureid", "ID")
                q("gml_include_items", "all")

            p(f"""FILTER ("[type]" eq {gsg_type!r})""")

            with block("CLASS"):
                p("NAME", classname)
                with block("STYLE"):
                    p("ANTIALIAS true")
                    p(f"OUTLINECOLOR {color}")
                    p(f"COLOR {color}")
                    p("OPACITY 35")
                    p("WIDTH 2")

                with block("LABEL"):
                    p("MINSCALEDENOM 100")
                    p("MAXSCALEDENOM 50001")
                    p(f"COLOR {color}")
                    p("OUTLINECOLOR 255 255 255")
                    p("OUTLINEWIDTH 3")
                    p("FONT", "Ubuntu-M")
                    p("TYPE truetype")
                    p("SIZE 10")
                    p("POSITION AUTO")
                    p("PARTIALS FALSE")

                with block("LABEL"):
                    p("MINSCALEDENOM 50001")
                    p("MAXSCALEDENOM 100001")
                    p(f"COLOR {color}")
                    p("OUTLINECOLOR 255 255 255")
                    p("FONT", "Ubuntu-M")
                    p("TYPE truetype")
                    p("SIZE 8")
                    p("POSITION AUTO")
                    p("PARTIALS FALSE")
