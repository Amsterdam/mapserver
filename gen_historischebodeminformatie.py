import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

layers = [
    ("Bodemgebruik en obstakels", "Boerderij", "Boerderij", ('#ebdc56', False)),    #VLAK zit in 'objecten' tabel
    ("Bodemgebruik en obstakels", "Defensieterrein", "Defensieterrein", ('#d5587c', False)),
    ("Bodemgebruik en obstakels", "Fabriek/bedrijventerrein", "Fabriek/bedrijventerrein", ('#a78409', False)),
    ("Bodemgebruik en obstakels", "Gebouw", "Gebouw", ('#0e6f99', False)),
    ("Bodemgebruik en obstakels", "Glastuinbouw", "Glastuinbouw", ('#9bca54', False)),
    ("Bodemgebruik en obstakels", "Object", "Object", ('#03cea2', False)),
    ("Bodemgebruik en obstakels", "Overig", "Overig", ('#d00ee5', False)),
    ("Bodemgebruik en obstakels", "Spoorwegemplacement", "Spoorwegemplacement", ('#ae95b9', False)),
    ("Bodemgebruik en obstakels", "Stookruimte/olietank", "Stookruimte/olietank", ('#713dbe', False)),
    ("Bodemgebruik en obstakels", "Tram- en busremises", "Tram en busremises", ('#3a15e1', False)),
    ("Bodemgebruik en obstakels", "Volkstuinen", "Volkstuinen", ('#06d3f7', False)),
    ("Lijnvormige obstakels", "Gasbuis", "Gasbuis", ('#bfb479', True)), #LIJN zit in 'kabels en leidingen'
    ("Lijnvormige obstakels", "Grondkering", "Grondkering", ('#d7650e',False)),
    ("Lijnvormige obstakels", "Kabel", "Kabel", ('#d67814', True)),
    ("Lijnvormige obstakels", "Mantelbuis", "Mantelbuis", ('#79e0d4', True)),
    ("Lijnvormige obstakels", "Persleiding", "Persleiding", ('#20a620', True)),
    ("Lijnvormige obstakels", "Riool", "Riool", ('#0e5129', True)),
    ("Lijnvormige obstakels", "Spoorweg", "Spoorweg", ('#232323', True)),
    ("Lijnvormige obstakels", "Waterleiding", "Waterleiding", ('#3a15e1', True)),
    ("Dempingen en ophogingen", "Demping", "Demping", ('#e4d62e', False)), #dit zit uiteraard in dempingen en ophogingen
    ("Dempingen en ophogingen", "Depot/stort", "Depot/stort", ('#ce7263', False)),
    ("Dempingen en ophogingen", "Dijk", "Dijk", ('#66b2b1', False)),
    ("Dempingen en ophogingen", "Ophoging", "Ophoging", ('#8c8c8b', False))
]



with block("MAP"):
    p("NAME", "historischebodeminformatie")
    p("INCLUDE", "header.inc")

    with block("PROJECTION"):
        q("init=epsg:28992")


    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Historische Bodeminformatie")
            #q("ows_onlineresource", "MAP_URL_REPLACE/maps/historischebodeminformatie")
            q("ows_abstract", "Historische Bodeminformatie",)

    
    for group, layer_name, filter_value, colors in layers:

        if group == "Bodemgebruik en obstakels":

            with block("LAYER"):
                sql = f"geometrie from (SELECT * FROM public.historische_bodeminformatie_bodemgebruik_en_obstakels where categorie = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE POLYGON")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")

                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", "Bodemgebruik en obstakels")
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometry")
                    q("gml_geometry_type", "polygon")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")


                with block("CLASS"):
                    p("NAME", f"{layer_name_slug}")
                    p("TITLE", f"{layer_name}")

                    with block("STYLE"):
                        p(f'COLOR "{colors[0]}"')
                        p("OPACITY", 40) 
                        p(f'OUTLINECOLOR "{colors[0]}"')
                        p("WIDTH ", 2)


        if group == "Lijnvormige obstakels":

            with block("LAYER"):
                sql = f"geometrie from (SELECT * FROM public.historische_bodeminformatie_lijnvormige_obstakels where categorie = '{filter_value}') as subquery USING srid=28992 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE LINE")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
    
                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", 'Lijnvormige obstakels')
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometrie")
                    q("gml_geometry_type", "linestring")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")


                with block("CLASS"):
                    p("NAME", f"{layer_name_slug}")
                    p("TITLE", f"{layer_name}")

                    with block("STYLE"):
                        p(f'COLOR "{colors[0]}"')
                        p("OPACITY", 40) 
                        p(f'OUTLINECOLOR "{colors[0]}"')
                        p("WIDTH ", 2)
                        if colors[1] == True:
                            with block("PATTERN"):
                                print ("10 5")

        if group == "Dempingen en ophogingen":

            with block("LAYER"):
                sql = f"geometrie from (SELECT *, ST_Force2D(geometrie) as geometrie_2d FROM public.historische_bodeminformatie_dempingen_en_ophogingen where categorie = '{filter_value}') as subquery USING srid=7415 USING UNIQUE id"
                

                layer_name_slug = slugify(layer_name)

                p("NAME", layer_name_slug)
                p("INCLUDE", "connection/dataservices.inc")
                p("DATA", sql)
                p('GROUP', slugify(group))
                p("TYPE POLYGON")
                p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
   
                
                with block("METADATA"):
                    q("ows_title", layer_name)
                    q('ows_group_title', group)
                    q("wms_include_items", "all")
                    q("ows_abstract", 'Dempingen en ophogingen')
                    q("gml_featureid", "id")
                    q("gml_geometries", "geometrie")
                    q("gml_geometry_type", "polygon")
                    q("gml_include_items", "all")
                    q("gml_types", "auto")


                with block("CLASS"):
                    p("NAME", f"{layer_name_slug}")
                    p("TITLE", f"{layer_name}")
                    
                    with block("STYLE"):
                        p(f'COLOR "{colors[0]}"')
                        p("OPACITY", 40) 
                        p(f'OUTLINECOLOR "{colors[0]}"')
                        p("WIDTH ", 2)