#!/usr/bin/env python

from generate import block, header, p, q


species = [
    "Iep (Ulmus)",
    "Linde (Tilia)",
    "Esdoorn (Acer)",
    "Es (Fraxinus)",
    "Plataan (Platanus)",
    "Eik (Quercus)",
    "Populier (Populus)",
    "Els (Alnus)",
    "Wilg (Salix)",
    "Berk (Betula)",
    "Kers (Prunus)",
    "Haagbeuk (Carpinus)",
    "Meidoorn (Crataegus)",
    "Acacia (Robinia)",
    "Paardenkastanje (Aesculus)",
    "Vleugelnoot (Pterocarya)",
]

layers = [name for name in species] + ["Onbekende soorten", "Overige soorten"]

header("BOR")

with block("MAP"):
    p("NAME", "bomen")
    p("INCLUDE", "header.inc")
    p("DEBUG", 5)

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Objecten openbare ruimte - bomen")
            q(
                "ows_abstract",
                "Dataset met actuele informatie over de bomen in beheer van gemeente Amsterdam",
            )
            q("wms_extent", "100000 450000 150000 500000")

    for name in layers:
        shortname = name.split()[0].lower()

        with block("LAYER"):
            p("NAME", shortname)
            p("GROUP", "bomen")

            with block("PROJECTION"):
                q("init=epsg:28992")

            p("INCLUDE", "connection/dataservices.inc")
            if name == "Onbekende soorten":
                select_soort = "soortnaam_top = 'Onbekend' OR soortnaam_top IS NULL"
            elif name == "Overige soorten":
                select_soort = (
                    " AND ".join(f"soortnaam_top != '{s}'" for s in species)
                    + " AND soortnaam_top IS NOT NULL"
                )
            else:
                select_soort = f"soortnaam_top = '{name}'"
            p(
                "DATA",
                "geometrie FROM ("
                "   SELECT id, geometrie, soortnaam_top FROM public.bomen_stamgegevens_v2"
                "   WHERE type_soortnaam = 'Bomen'"
                f"  AND ({select_soort})"
                ") AS sub"
                " USING srid=28992"
                " USING UNIQUE id",
            )
            p("TYPE POINT")

            with block("METADATA"):
                q("wfs_enable_request", "!*")
                q("wms_title", name)
                q("wms_enable_request", "*")
                q("wms_srs", "EPSG:28992")
                q("wms_name", "Bomen")
                q("wms_format", "image/png")
                q("wms_server_version", "1.3.0")
                q("wms_extent", "100000 450000 150000 500000")

            p("LABELITEM", "soortnaam_top")
            p("CLASSITEM", "soortnaam_top")

            with block("CLASS"):
                p("NAME", name)
                p('MINSCALE', 3000)

                with block("STYLE"):
                    p("SYMBOL", f"bomen_{shortname}")
                    p("SIZE", 16)


            with block ("CLASS"):
                p('MAXSCALE', 3000)
                with block("STYLE"):
                    p("SYMBOL", f"bomen_{shortname}")
                    p("SIZE", 26)
