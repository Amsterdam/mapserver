import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers = [
    ("Servicegebieden", "Servicegebieden Rest", "Rest"),
    ("Servicegebieden", "Servicegebieden Glas", "Glas"),
    ("Servicegebieden", "Servicegebieden Papier", "Papier"),
    ("Servicegebieden", "Servicegebieden Textiel", "Textiel"),
    ("Servicegebieden", "Servicegebieden GFT", "GFT"),
    ("Servicegebiedenlocatie", "Servicegebiedenlocatie Rest", "Rest"),
    ("Servicegebiedenlocatie", "Servicegebiedenlocatie Glas", "Glas"),
    ("Servicegebiedenlocatie", "Servicegebiedenlocatie Papier", "Papier"),
    ("Servicegebiedenlocatie", "Servicegebiedenlocatie Textiel", "Textiel"),
    ("Servicegebiedenlocatie", "Servicegebiedenlocatie GFT", "GFT")
]

colors = ("#8dd3c7", "#ffffb3", "#bebada", "#fb8072", "#80b1d3", "#fdb462", "#b3de69", "#fccde5", "#d9d9d9", "#bc80bd")


with block("MAP"):
    p("NAME", "huishoudelijkafvalservicegebieden")
    p("INCLUDE", "header.inc")


    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Huishoudelijkafval Servicegebieden")
            q("ows_onlineresource", "MAP_URL_REPLACE/maps/huishoudelijkafvalservicegebieden")
            q("ows_abstract", "Servicegebieden van huishoudelijkafvalcontainers",)

    
    for group, layer_name, filter_value in layers:

        if group == 'Servicegebieden':

            with block("LAYER"):
                sql = f"geometrie from (SELECT *, (regexp_matches(servicegebieden_locatie_id, '[0-9](?!.*[0-9])'))[1] AS last_numeric_digit FROM huishoudelijkafval_servicegebieden where fractie_omschrijving = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE POLYGON")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")

                with block("PROJECTION"):
                    q("init=epsg:28992")
                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", "Servicegebieden")
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometry")
                    q("gml_geometry_type", "polygon")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")
                    q("wms_enable_request", "!GetLegendGraphic")

                
                for i in range(10):

                    with block("CLASS"):
                        p("NAME", f"{i}")

                        # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                        # de laatste digit wordt gebruikt om zowel een groep te maken als een kleur uit de lijst te pakken, 
                        #dat maakt dat zowel het cluster als het gebied dezelfde kleur krijgen.
                        print (f'EXPRESSION ("[last_numeric_digit]" eq "{i}")')
                        with block("STYLE"):
                            p(f'COLOR "{colors[i]}"')
                            p("OPACITY", 90) 
                            p(f'OUTLINECOLOR "{colors[i]}"')
                            p("WIDTH ", 2)


        if group == 'Servicegebiedenlocatie':

            with block("LAYER"):
                sql = f"geometrie from (SELECT *, (regexp_matches(id, '[0-9](?!.*[0-9])'))[1] AS last_numeric_digit FROM huishoudelijkafval_servicegebieden_locatie where cluster_fractie_omschrijving = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE POINT")
                # p("MINSCALEDENOM 10")
                # p("MAXSCALEDENOM 9001")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
                p("LABELITEM", "aantal_woningen")

                with block("PROJECTION"):
                    q("init=epsg:28992")
                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", "Servicegebieden locaties")
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometry")
                    q("gml_geometry_type", "point")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")
                    q("wms_enable_request", "!GetLegendGraphic")
                

                for i in range(10):

                    with block("CLASS"):
                        p("NAME", f"{i}")

                        # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                        # de laatste digit wordt gebruikt om zowel een groep te maken als een kleur uit de lijst te pakken, 
                        #dat maakt dat zowel het cluster als het gebied dezelfde kleur krijgen.
                        print (f'EXPRESSION ("[last_numeric_digit]" eq "{i}")')
                        with block("STYLE"):
                            p("SYMBOL", "stip")
                            p("SIZE 16")
                            p(f"COLOR '{colors[i]}'")
                            p('OUTLINECOLOR 0 0 0')
                            p ('WIDTH 1')

                        with block("LABEL"):
                            p("MINSCALEDENOM 100")
                            p("MAXSCALEDENOM 1000")
                            p("COLOR 0 0 0")
                            p("OUTLINECOLOR 255 255 255")
                            p("OUTLINEWIDTH 3")
                            p("FONT", "Ubuntu-M")
                            p("TYPE truetype")
                            p("SIZE 10")
                            p("POSITION AUTO")
                            p("PARTIALS FALSE")
                            p("OFFSET -30 10")