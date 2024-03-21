import re
import random

from generate import block, header, p, q


def slugify(s: str) -> str:
    # TODO would be cleaner to convert to NFD, then remove combining chars.
    s = s.replace("ë", "e")
    return re.sub(r"[^A-Za-z]+", "_", s).strip("_").lower()

def random_colorpicker ():
    min = 0
    max = 255
    red = random.randint(min, max) 
    green = random.randint(min, max) 
    blue = random.randint(min, max) 
    
    return f'{red} {green} {blue}'


# From https://www.amsterdam.nl/stelselpedia/hr-index/catalogus-hr/domeinen/sbi-code/.
sbi = {
    "A Landbouw, bosbouw en visserij": [
        ("01", "Landbouw, jacht en dienstverlening voor de landbouw en jacht", "#FF0000"),
        ("02", "Bosbouw, exploitatie van bossen en dienstverlening voor de bosbouw", "#00FF00"),
        ("03", "Visserij en kweken van vis en schaaldieren", "#0000FF")
    ],
    "B Winning van delfstoffen": [
        ("06", "Winning van aardolie en aardgas", "#FFFF00"),
        ("08", "Winning van delfstoffen (geen olie en gas)", "#FF00FF"),
        ("09", "Dienstverlening voor de winning van delfstoffen", "#00FFFF")
    ],
    "C Industrie": [
        ("10", "Vervaardiging van voedingsmiddelen", "#FFA500"),
        ("11", "Vervaardiging van dranken", "#800080"),
        ("12", "Vervaardiging van tabaksproducten", "#FF4500"),
        ("13", "Vervaardiging van textiel", "#228B22"),
        ("14", "Vervaardiging van kleding", "#4169E1"),
        ("15", "Vervaardiging van leer, lederwaren en schoenen", "#FF69B4"),
        ("16", "Primaire houtbewerking en vervaardiging van artikelen van hout, kurk, riet en vlechtwerk (geen meubels)", "#32CD32"),
        ("17", "Vervaardiging van papier, karton en papier- en kartonwaren", "#8A2BE2"),
        ("18", "Drukkerijen, reproductie van opgenomen media", "#DC143C"),
        ("19", "Vervaardiging van cokesovenproducten en aardolieverwerking", "#00CED1"),
        ("20", "Vervaardiging van chemische producten", "#FFD700"),
        ("21", "Vervaardiging van farmaceutische grondstoffen en producten", "#808000"),
        ("22", "Vervaardiging van producten van rubber en kunststof", "#4682B4"),
        ("23", "Vervaardiging van overige niet-metaalhoudende minerale producten", "#00FF7F"),
        ("24", "Vervaardiging van metalen in primaire vorm", "#8B008B"),
        ("25", "Vervaardiging van producten van metaal (geen machines en apparaten)", "#FF6347"),
        ("26", "Vervaardiging van computers en van elektronische en optische apparatuur", "#556B2F"),
        ("27", "Vervaardiging van elektrische apparatuur", "#800000"),
        ("28", "Vervaardiging van overige machines en apparaten", "#9932CC"),
        ("29", "Vervaardiging van auto's, aanhangwagens en opleggers", "#20B2AA"),
        ("30", "Vervaardiging van overige transportmiddelen", "#FA8072"),
        ("31", "Vervaardiging van meubels", "#2E8B57"),
        ("32", "Vervaardiging van overige goederen", "#6A5ACD"),
        ("33", "Reparatie en installatie van machines en apparaten", "#B22222")
    ],
    "D Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht": [
        ("35", "Productie en distributie van en handel in elektriciteit, aardgas, stoom en gekoelde lucht", "#4682B4")
    ],
    "E Winning en distributie van water; afval- en afvalwaterbeheer en sanering": [
        ("36", "Winning en distributie van water", "#FF5733"),
        ("37", "Afvalwaterinzameling en -behandeling", "#33FF57"),
        ("38", "Afvalinzameling en -behandeling; voorbereiding tot recycling", "#3377FF"),
        ("39", "Sanering en overig afvalbeheer", "#FF33FF")
    ],
    "F Bouwnijverheid": [
        ("41", "Algemene burgerlijke en utiliteitsbouw en projectontwikkeling", "#FF5733"),
        ("42", "Grond-, water- en wegenbouw (geen grondverzet)", "#33FF57"),
        ("43", "Gespecialiseerde werkzaamheden in de bouw", "#3377FF") 
    ],
    "G Groot- en detailhandel; reparatie van auto's": [
        ("45", "Handel in en reparatie van auto's, motorfietsen en aanhangers", "#FF5733"),
        ("46", "Groothandel en handelsbemiddeling (niet in auto's en motorfietsen)", "#33FF57"),
        ("47", "Detailhandel (niet in auto's)", "#3366FF")
    ],
    "H Vervoer en opslag": [
        ("49", "Vervoer over land", "#FF5733"),
        ("50", "Vervoer over water", "#33FF57"),
        ("51", "Luchtvaart", "#3366FF"),
        ("52", "Opslag en dienstverlening voor vervoer", "#FF33FF"),
        ("53", "Post en koeriers", "#FFFF33")
    ],
    "I Logies-, maaltijd- en drankverstrekking": [
        ("55", "Logiesverstrekking", "#BF8080"),
        ("56", "Eet- en drinkgelegenheden", "#BFBFBF")
    ],
    "J Informatie en communicatie": [
        ("58", "Uitgeverijen", "#BF80FD"),
        ("59", "Productie en distributie van films en televisieprogramma's; maken en uitgeven van geluidsopnamen", "#BF80BF"),
        ("60", "Verzorgen en uitzenden van radio- en televisieprogramma's", "#BF8040"),
        ("61", "Telecommunicatie", "#BFBF80"),
        ("62", "Dienstverlenende activiteiten op het gebied van informatietechnologie", "#BFBFBF"),
        ("63", "Dienstverlenende activiteiten op het gebied van informatie", "#BF8080")
        ],
        "K Financiële instellingen": [
        ("64", "Financiële instellingen (geen verzekeringen en pensioenfondsen)", "#FF6347"),
        ("65", "Verzekeringen en pensioenfondsen (geen verplichte sociale verzekeringen)", "#4682B4"),
        ("66", "Overige financiële dienstverlening", "#9400D3")
    ],
    "L Verhuur van en handel in onroerend goed": [
        ("68", "Verhuur van en handel in onroerend goed", "#00FF00")
    ],
    "M Advisering, onderzoek en overige specialistische zakelijke dienstverlening": [
        ("69", "Rechtskundige dienstverlening, accountancy, belastingadvisering en administratie", "#FF00FF"),
        ("70", "Holdings (geen financiële), concerndiensten binnen eigen concern en managementadvisering", "#00FF7F"),
        ("71", "Architecten, ingenieurs en technisch ontwerp en advies; keuring en controle", "#000080"),
        ("72", "Speur- en ontwikkelingswerk", "#8B0000"),
        ("73", "Reclame en marktonderzoek", "#FFA500"),
        ("74", "Industrieel ontwerp en vormgeving, fotografie, vertaling en overige consultancy", "#4B0082"),
        ("75", "Veterinaire dienstverlening", "#FFD700")
    ],
    "N Verhuur van roerende goederen en overige zakelijke dienstverlening": [
        ("77", "Verhuur en lease van auto's, consumentenartikelen, machines en overige roerende goederen", "#008000"),
        ("78", "Arbeidsbemiddeling, uitzendbureaus en personeelsbeheer", "#FF4500"),
        ("79", "Reisbemiddeling, reisorganisatie, toeristische informatie en reserveringsbureaus", "#00FFFF"),
        ("80", "Beveiliging en opsporing", "#0000FF"),
        ("81", "Facility management, reiniging en landschapsverzorging", "#FF00FF"),
        ("82", "Overige zakelijke dienstverlening", "#FFFF00")
    ],
    "O Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen": [
        ("84", "Openbaar bestuur, overheidsdiensten en verplichte sociale verzekeringen", "#808080")
    ],
    "P Onderwijs": [
        ("85", "Onderwijs", "#008080")
    ],
    "Q Gezondheids- en welzijnszorg": [
        ("86", "Gezondheidszorg", "#800000"),
        ("87", "Verpleging, verzorging en begeleiding met overnachting", "#FF00FF"),
        ("88", "Maatschappelijke dienstverlening zonder overnachting", "#00FFFF")
    ],
    "R Cultuur, sport en recreatie": [
        ("90", "Kunst", "#008000"),
        ("91", "Culturele uitleencentra, openbare archieven, musea, dieren- en plantentuinen, natuurbehoud", "#800080"),
        ("92", "Loterijen en kansspelen", "#000080"),
        ("93", "Sport en recreatie", "#FFA500")
    ],
    "S Overige dienstverlening": [
        ("94", "Levensbeschouwelijke en politieke organisaties, belangen- en ideële organisaties, hobbyclubs", "#FF00FF"),
        ("95", "Reparatie van computers en consumentenartikelen", "#00FFFF"),
        ("96", "Wellness en overige dienstverlening; uitvaartbranche", "#0000FF")
    ],
    "T Huishoudens als werkgever; niet-gedifferentieerde productie van goederen en diensten door huishoudens voor eigen gebruik": [
        ("97", "Huishoudens als werkgever van huishoudelijk personeel", "#800080"),
        ("98", "Niet-gespecificeerde productie van goederen en diensten door particuliere huishoudens voor eigen gebruik", "#FFA500")
    ],
    "U Extraterritoriale organisaties en lichamen": [
        ("99", "Extraterritoriale organisaties en lichamen", "#008080")
    ]
}

#header(team="BenK")

with block("MAP"):
    p("NAME", "Handelsregister")
    p("INCLUDE", "header.inc")

    p("DEBUG 5")

    with block("WEB"):
        with block("METADATA"):
            q("ows_title", "Handelsregister")
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
            # p("MINSCALEDENOM 10")
            # p("MAXSCALEDENOM 9001")
            p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            p("PROCESSING", "CLOSE_CONNECTION=DEFER")
            p("STATUS OFF")
            p("LABELITEM", "naam")

            with block("PROJECTION"):
                q("init=epsg:28992")
            
            with block("METADATA"):
                q("wms_title", group)
                q("gml_include_items", "all")
                q("wms_enable_request", "*")
                q("wms_abstract", "Handelsregister Amsterdam")
                q("wms_srs", "EPSG:28992")
                q("wms_format", "image/png")
                q("wms_server_version", "1.1.1")

            

            for code, descr, color in sbi[group]:
                slug = slugify(descr)

                # TODO label werkend maken?


                with block("CLASS"):
                    p("NAME", slug)

                    # kleine aanpassing aan de print structuur om te voorkomen dat er '' om deze komt.
                    print (f'EXPRESSION ("[sbi_code_group]" eq "{code}")')
                    with block("STYLE"):
                        p("SYMBOL", "stip")
                        p("SIZE 16")
                        p(f"COLOR '{color}'")
                        p('OUTLINECOLOR 0 0 0')
                        p ('WIDTH 2')

                    with block("LABEL"):
                        p("MINSCALEDENOM 100")
                        p("MAXSCALEDENOM 20000")
                        p("COLOR 0 0 0")
                        p("OUTLINECOLOR 255 255 255")
                        p("OUTLINEWIDTH 3")
                        p("FONT", "Ubuntu-M")
                        p("TYPE truetype")
                        p("SIZE 10")
                        p("POSITION AUTO")
                        p("PARTIALS FALSE")
                        p("OFFSET -60 10")
                


            # with block("LAYER"):
            #     p("NAME", slug + "_label")
            #     p("GROUP", group)
            #     p("INCLUDE", "connection/dataservices.inc")
            #     p("DATA", sql)
            #     p("TYPE POINT")
            #     # p("MINSCALEDENOM 100")
            #     # p("MAXSCALEDENOM 1001")
            #     p("TEMPLATE", "fooOnlyForWMSGetFeatureInfo.html")
            #     p("PROCESSING", "CLOSE_CONNECTION=DEFER")
            #     p("STATUS OFF")

            #     with block("PROJECTION"):
            #         q("init=epsg:28992")

            #     with block("METADATA"):
            #         q("ows_title", slug + "_label")
            #         q("ows_group_title", "vestigingen_cbs_label")
            #         q("ows_abstract", "Labels van vestigingen")

            #     p("LABELITEM", "naam")

            #     with block("CLASS"):
            #         with block("LABEL"):
            #             # p("MINSCALEDENOM 100")
            #             # p("MAXSCALEDENOM 1001")
            #             p("COLOR 0 0 0")
            #             p("OUTLINECOLOR 255 255 255")
            #             p("OUTLINEWIDTH 3")
            #             p("FONT", "Ubuntu-M")
            #             p("TYPE truetype")
            #             p("SIZE 10")
            #             p("POSITION AUTO")
            #             p("PARTIALS FALSE")
            #             p("OFFSET -60 10")
