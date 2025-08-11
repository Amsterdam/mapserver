import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()


# From https://www.amsterdam.nl/stelselpedia/hr-index/catalogus-hr/domeinen/sbi-code/.
sbi = {
    "A Landbouw, bosbouw en visserij": [
        ("01", "Landbouw, jacht en dienstverlening voor de landbouw en jacht", "#FF0000"),
        ("02", "Bosbouw, exploitatie van bossen en dienstverlening voor de bosbouw", "#00FF00"),
        ("03", "Visserij en aquacultuur", "#0000FF")
    ],
    "B Winning van delfstoffen": [
        ("05", "Winning van steenkool en bruinkool", "#FFFF00"),
        ("06", "Winning van aardolie en aardgas", "#FFFF00"),
        ("07", "Winning van metaalertsen", "#FFFF00"),
        ("08", "Overige winning van delfstoffen", "#FF00FF"),
        ("09", "Dienstverlening voor de winning van delfstoffen", "#00FFFF")
    ],
    "C Industrie": [
        ("10", "Vervaardiging van voedingsmiddelen", "#FFA500"),
        ("11", "Vervaardiging van dranken", "#800080"),
        ("12", "Vervaardiging van tabaksproducten", "#FF4500"),
        ("13", "Vervaardiging van textiel", "#228B22"),
        ("14", "Vervaardiging van kleding", "#4169E1"),
        ("15", "Vervaardiging van leer, lederwaren en soortgelijke producten van andere materialen", "#FF69B4"),
        ("16", "Houtindustrie en vervaardiging van artikelen van hout en kurk, met uitzondering van meubelen; vervaardiging van artikelen van riet en van vlechtwerk", "#32CD32"),
        ("17", "Vervaardiging van papier en papierwaren", "#8A2BE2"),
        ("18", "Activiteiten op het gebied van drukwerk en reproductie van opgenomen media", "#DC143C"),
        ("19", "Vervaardiging van cokes en van geraffineerde aardolieproducten", "#00CED1"),
        ("20", "Vervaardiging van chemicaliën en chemische producten", "#FFD700"),
        ("21", "Vervaardiging van farmaceutische grondstoffen en producten", "#808000"),
        ("22", "Vervaardiging van producten van rubber of kunststof", "#4682B4"),
        ("23", "Vervaardiging van overige niet-metaalhoudende minerale producten", "#00FF7F"),
        ("24", "Vervaardiging van basismetalen", "#8B008B"),
        ("25", "Vervaardiging van producten van metaal, met uitzondering van machines en apparatuur", "#FF6347"),
        ("26", "Vervaardiging van computers en van elektronische en optische apparatuur", "#556B2F"),
        ("27", "Vervaardiging van elektrische apparatuur", "#800000"),
        ("28", "Vervaardiging van machines en apparaten, n.e.g.", "#9932CC"),
        ("29", "Vervaardiging van motorvoertuigen, aanhangwagens en opleggers", "#20B2AA"),
        ("30", "Vervaardiging van overige vervoermiddelen", "#FA8072"),
        ("31", "Vervaardiging van meubelen", "#2E8B57"),
        ("32", "Vervaardiging van overige goederen", "#6A5ACD"),
        ("33", "Reparatie, onderhoud en installatie van machines en apparaten", "#B22222")
    ],
    "D Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht": [
        ("35", "Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht", "#4682B4")
    ],
    "E Winning en distributie van water; afval- en afvalwaterbeheer en sanering": [
        ("36", "Winning, behandeling en distributie van water", "#FF5733"),
        ("37", "Afvalwaterinzameling en -behandeling", "#33FF57"),
        ("38", "Afvalinzameling, voorbereiding tot recycling, en verwijdering", "#3377FF"),
        ("39", "Sanering en overig afvalbeheer", "#FF33FF")
    ],
    "F Bouwnijverheid": [
        ("41", "Burgerlijke en utiliteitsbouw", "#FF5733"),
        ("42", "Grond-, water- en wegenbouw", "#33FF57"),
        ("43", "Gespecialiseerde werkzaamheden in de bouw", "#3377FF") 
    ],
    "G Groot- en detailhandel": [
        ("46", "Groothandel", "#33FF57"),
        ("47", "Detailhandel", "#3366FF")
    ],
    "H Vervoer en opslag": [
        ("49", "Vervoer over land en via pijpleidingen", "#FF5733"),
        ("50", "Vervoer over water", "#33FF57"),
        ("51", "Luchtvaart", "#3366FF"),
        ("52", "Opslag en dienstverlening voor vervoer", "#FF33FF"),
        ("53", "Post- en koeriersdiensten", "#FFFF33")
    ],
    "I Logies-, maaltijd- en drankverstrekking": [
        ("55", "Logiesverstrekking en -bemiddeling", "#BF8080"),
        ("56", "Exploitatie van eet- en drinkgelegenheden", "#BFBFBF")
    ],
    "J Activiteiten van uitgeverijen, omroepactiviteiten, en activiteiten op het gebied van productie en distributie van inhoud": [
        ("58", "Activiteiten van uitgeverijen", "#BF80FD"),
        ("59", "Productie en distributie van films en video- en televisieprogramma’s en audio, maken van geluidsopnamen en uitgeven van muziekopnamen", "#BF80BF"),
        ("60", "Programmering, uitzending, persagentschappen en overige activiteiten op het gebied van de verspreiding van inhoud", "#BF8040")
        ],
    "K Telecommunciatie, computerprogrammering en consultancy, informatica-infrastructuur en overige activiteiten op het gebied van informatiediensten": [
        ("61", "Telecommunicatie", "#BFBF80"),
        ("62", "Computerprogrammering, consultancy en aanverwante activiteiten", "#BFBFBF"),
        ("63", "Dienstverlenende activiteiten op het gebied van informatie", "#BF8080")
        ],
    "L Activiteiten op het gebied van financiële dienstverlening en verzekeringen": [
        ("64", "Financiële dienstverlening, met uitzondering van verzekeringen en pensioenfondsen", "#FF6347"),
        ("65", "Activiteiten op het gebied van verzekeringen en pensioenfondsen, met uitzondering van verplichte sociale verzekeringen", "#4682B4"),
        ("66", "Ondersteunende activiteiten voor financiële diensten, verzekeringen en pensioenen", "#9400D3")
    ],
    "M Exploitatie van en handel in onroerend goed": [
        ("68", "Exploitatie van en handel in onroerend goed", "#00FF00")
    ],
    "N Wetenschappelijke en technische activiteiten en specialistische zakelijke dienstverlening": [
        ("69", "Rechtskundige en boekhoudkundige dienstverlening", "#FF00FF"),
        ("70", "Activiteiten van hoofdkantoren, interne concerndiensten en managementadvisering", "#00FF7F"),
        ("71", "Activiteiten van architecten en ingenieurs; technisch ontwerp en advies, keuring en controle", "#000080"),
        ("72", "Wetenschappelijk onderzoek en ontwikkeling", "#8B0000"),
        ("73", "Reclameactiviteiten, marktonderzoek en public relations", "#FFA500"),
        ("74", "Overige wetenschappelijke en technische activiteiten en overige specialistische zakelijke dienstverlening", "#4B0082"),
        ("75", "Veterinaire dienstverlening", "#FFD700")
    ],
    "O Verhuur van roerende goederen en overige zakelijke dienstverlening": [
        ("77", "Verhuur en lease", "#008000"),
        ("78", "Arbeidsbemiddeling, activiteiten van uitzendbureaus en personeelsbeheer", "#FF4500"),
        ("79", "Activiteiten van reisbureaus, reisorganisatoren, reserveringsbureaus en aanverwante activiteiten", "#00FFFF"),
        ("80", "Opsporings- en beveiligingsdiensten", "#0000FF"),
        ("81", "Diensten in verband met gebouwen; landschapsverzorging", "#FF00FF"),
        ("82", "Administratieve en ondersteunende activiteiten ten behoeve van kantoren en overige zakelijke dienstverlening", "#FFFF00")
    ],
    "P Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen": [
        ("84", "Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen", "#808080")
    ],
    "Q Onderwijs": [
        ("85", "Onderwijs", "#008080")
    ],
    "R Gezondheids- en welzijnszorg": [
        ("86", "Gezondheidszorg", "#800000"),
        ("87", "Verpleging, verzorging en begeleiding met verblijf", "#FF00FF"),
        ("88", "Maatschappelijke dienstverlening zonder verblijf", "#00FFFF")
    ],
    "S Kunst, cultuur, sport en recreatie activiteiten": [
        ("90", "Activiteiten op het gebied van scheppende en uitvoerende kunst", "#008000"),
        ("91", "Activiteiten van bibliotheken, archieven, musea en overige culturele activiteiten", "#800080"),
        ("92", "Exploitatie van loterijen, kansspelen en kansspelautomaten", "#000080"),
        ("93", "Sport, ontspanning en recreatie", "#FFA500")
    ],
    "T Overige dienstverlening": [
        ("94", "Activiteiten van ledenorganisaties", "#FF00FF"),
        ("95", "Reparatie en onderhoud van computers, consumentenartikelen, auto’s en motorfietsen", "#00FFFF"),
        ("96", "Persoonlijke dienstverlening", "#0000FF")
    ],
    "U Activiteiten van huishoudens als werkgever en niet-gedifferentieerde productie van goederen en diensten door huishoudens voor eigen gebruik": [
        ("97", "Activiteiten van huishoudens als werkgever van huishoudelijk personeel", "#800080"),
        ("98", "Niet-gedifferentieerde productie van goederen en diensten door particuliere huishoudens voor eigen gebruik", "#FFA500")
    ],
    "V Activiteiten van extraterritoriale organisaties en instanties": [
        ("99", "Activiteiten van extraterritoriale organisaties en instanties", "#008080")
    ]
}


with block("MAP"):
    p("NAME", "handelsregister")
    p("INCLUDE", "header.inc")


    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Handelsregister")
            q("ows_onlineresource", "MAP_URL_REPLACE/maps/hr")
            q("ows_abstract", "Vestigingen in de gemeente Amsterdam uit het Handelsregister",)

    with block("LEGEND"):
        p("STATUS ON")
        p("KEYSIZE 16 16")
    
    for group in sbi:

        with block("LAYER"):
            #ik moest hier helaas de hele data in 1x ophalen en dan later een expression met een filter op de SBI code doen.. 
            sql = f"""
                SELECT
                    naam, vestigingsnummer, bezoek_geopunt, substring(sbi_code FROM 1 FOR 2) as sbi_code_group, omschrijving
                FROM
                    hr_ves hv
                    INNER JOIN hr_ves_activiteiten hva
                    ON hva.parent_id = hv.vestigingsnummer
                WHERE
                    bezoek_geopunt IS NOT NULL
                    AND is_hoofdactiviteit = 'Ja'
            """

            sql = " ".join(sql.split())  # Normalize whitespace.
            sql = (
                f"bezoek_geopunt FROM ({sql}) AS sub"
                + " USING srid=28992 USING UNIQUE vestigingsnummer"
            )

            slug_group = slugify(group)

            p("NAME", slug_group)
            p("INCLUDE", "connection/dataservices.inc")
            p("DATA", sql)
            p("TYPE POINT")
            p("GROUP", 'handelsregister')
            # p("MINSCALEDENOM 10")
            # p("MAXSCALEDENOM 9001")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            p("PROCESSING", "CLOSE_CONNECTION=DEFER")
            p("STATUS OFF")
            p("LABELITEM", "naam")

            with block("PROJECTION"):
                q("init=epsg:28992")
            
            with block("METADATA"):
                q("ows_title", group)
                q("ows_group_title", 'Handelsregister')
                q("gml_include_items", "all")
                q("wms_enable_request", "*")
                q("ows_abstract", "Handelsregister Amsterdam")
                q("gml_featureid", "vestigingsnummer")
                q("gml_geometries", "geometry")
                q("gml_geometry_type", "point")                
                q("gml_types", "auto")
                q("wms_include_items", "all")
            

            for code, descr, color in sbi[group]:
                slug = slugify(descr)

                with block("CLASS"):
                    p("NAME", slug)
                    p("TITLE", descr)

                    # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                    print (f'EXPRESSION ("[sbi_code_group]" eq "{code}")')
                    with block("STYLE"):
                        p("SYMBOL", "stip")
                        p("SIZE 14")
                        p(f"COLOR '{color}'")
                        p('OUTLINECOLOR 255 255 255')
                        p ('WIDTH 1.5')

                    with block("LABEL"):
                        p("MINSCALEDENOM 100")
                        p("MAXSCALEDENOM 500")
                        p("COLOR 0 0 0")
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 3")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p("SIZE 10")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")
                        p("OFFSET -60 10")